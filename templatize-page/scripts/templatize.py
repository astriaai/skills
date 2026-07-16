#!/usr/bin/env python3
"""Turn lifestyle images into an Astria pack of pose-swap prompts.

Two variants, selected with --mode:

  shoes (default) — for each --pose-image-url:
    barefoot-edit the photo (remove the shoes), make a `pose` faceid tune
    from it, and create a prompt swapping in the workspace's first
    shoes/sandals reference.

  silhouette — driven by a --spec JSON file, an array of
    {"url": ..., "prompt": "...{pose}..."} objects:
    silhouette-edit the photo (keep only the posed figure), make a `pose`
    faceid tune from it, and create the caller-composed prompt with the new
    pose tune id substituted into its `{pose}` placeholder. The caller
    composes each prompt — `<faceid:ID>` tokens for the references the user
    chose to swap, plain text for the parts they did not.

Both variants create one pack named after --pack-title and assign every
prompt to it. Each pack prompt is rendered at the closest standard aspect
ratio to its source image, so the generated look keeps the original framing;
--aspect-ratio overrides the detection for the whole run.

Every API call goes through the bundled `astria` CLI, which handles auth and
workspace scoping. No environment variables and no extra Python packages
needed — only the standard library.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import urllib.request

BAREFOOT_EDIT_TEXT = (
    "Remove the subject's shoes so they are barefoot. Keep everything else "
    "identical — same pose, same outfit, same setting, same lighting, same "
    "composition."
)
SILHOUETTE_EDIT_TEXT = (
    "Reproduce this image keeping only a silhouette of the person, mainly "
    "showing their pose and body position."
)
SHOE_PROMPT_TEMPLATE = (
    "Reproduce the same <faceid:{pose_tune_id}:1> pose image but replace "
    "the original shoes with <faceid:{shoe_tune_id}:1> shoes"
)
POSE_PLACEHOLDER = "{pose}"

# Aspect ratios the Gemini image model accepts. Each source image's true ratio
# is snapped to the nearest of these so the generated pack prompt renders at
# the original framing instead of Gemini's square default.
ASPECT_RATIOS = {
    "21:9": 21 / 9, "16:9": 16 / 9, "3:2": 3 / 2, "4:3": 4 / 3, "5:4": 5 / 4,
    "1:1": 1.0,
    "4:5": 4 / 5, "3:4": 3 / 4, "2:3": 2 / 3, "9:16": 9 / 16,
}
# Fallback when a source image can't be fetched or its format isn't readable —
# fashion lookbook shots are overwhelmingly portrait.
DEFAULT_ASPECT_RATIO = "3:4"
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
MAX_HEADER_BYTES = 512 * 1024  # enough to reach the dimensions of any web image


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def image_dimensions(data):
    """Return (width, height) parsed from raw image bytes, or None if the
    format isn't one we can read (PNG, GIF, JPEG, WebP)."""
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    if data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        width, height = struct.unpack("<HH", data[6:10])
        return width, height
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return _webp_dimensions(data)
    if data[:2] == b"\xff\xd8":
        return _jpeg_dimensions(data)
    return None


def _webp_dimensions(data):
    fourcc = data[12:16]
    if fourcc == b"VP8X" and len(data) >= 30:           # extended format
        width = (data[24] | data[25] << 8 | data[26] << 16) + 1
        height = (data[27] | data[28] << 8 | data[29] << 16) + 1
        return width, height
    if fourcc == b"VP8L" and len(data) >= 25:           # lossless
        bits = struct.unpack("<I", data[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if fourcc == b"VP8 " and len(data) >= 30:           # lossy
        width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return width, height
    return None


def _jpeg_dimensions(data):
    """Walk JPEG segment markers to the start-of-frame, which carries the size."""
    i, n = 2, len(data)
    while i + 4 <= n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0x00, 0xFF):                      # stuffing / fill bytes
            i += 1
            continue
        if marker == 0x01 or 0xD0 <= marker <= 0xD9:    # standalone, no payload
            i += 2
            continue
        if marker == 0xDA:                              # start of scan — no header past here
            break
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):  # SOFn
            if i + 9 <= n:
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            return None
        i += 2 + seg_len
    return None


def closest_aspect_ratio(width, height):
    ratio = width / height
    return min(ASPECT_RATIOS, key=lambda name: abs(ASPECT_RATIOS[name] - ratio))


def detect_aspect_ratio(image_url):
    """Snap a source image's real aspect ratio to the closest value Gemini
    accepts. Falls back to DEFAULT_ASPECT_RATIO when the image can't be fetched
    or its format isn't recognized."""
    try:
        request = urllib.request.Request(image_url, headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(MAX_HEADER_BYTES)
    except Exception as exc:                            # network / HTTP failure
        log(f"aspect     {image_url}: fetch failed ({exc}) — using {DEFAULT_ASPECT_RATIO}")
        return DEFAULT_ASPECT_RATIO
    dims = image_dimensions(data)
    if not dims or dims[0] <= 0 or dims[1] <= 0:
        log(f"aspect     {image_url}: dimensions unreadable — using {DEFAULT_ASPECT_RATIO}")
        return DEFAULT_ASPECT_RATIO
    width, height = dims
    aspect = closest_aspect_ratio(width, height)
    log(f"aspect     {image_url}: {width}x{height} -> {aspect}")
    return aspect


class Astria:
    """Thin wrapper around the `astria` CLI."""

    def __init__(self, workspace=None):
        self.workspace = workspace

    def run(self, *args):
        argv = ["astria", *args]
        if self.workspace:
            argv += ["--workspace", self.workspace]
        proc = subprocess.run(argv, capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"`{' '.join(argv)}` failed: {proc.stderr.strip()}")
        out = proc.stdout.strip()
        return json.loads(out) if out else None


def find_shoe_tune(astria):
    tunes = astria.run("tunes", "list", "--name", "shoes", "--name", "sandals")
    if not tunes:
        raise SystemExit("No shoe or sandal references found in the workspace — "
                         "upload one before running /templatize-page.")
    shoe = tunes[0]
    log(f"shoe tune  id={shoe['id']}  title={shoe.get('title')!r}  name={shoe.get('name')!r}")
    return shoe


def create_pack(astria, title):
    pack = astria.run("packs", "create", "--title", title)
    log(f"pack       id={pack['id']}  title={pack.get('title')!r}")
    return pack


def subject_edit(astria, image_url, edit_text):
    """Run a Nano Banana edit on one photo and return the edited image URL.

    Astria dedups prompts by (text, seed) within a tune, so an identical edit
    instruction on two source photos would collide onto one prompt. Derive a
    per-image seed from the source URL so each edit stays distinct — without
    appending anything to the prompt text, which Nano Banana may otherwise
    render into the image as a caption."""
    seed = int(hashlib.sha1(image_url.encode()).hexdigest()[:8], 16)
    prompt = astria.run(
        "generate", "--model", "gemini", "--text", edit_text,
        "--input-image", image_url, "--num-images", "1",
        "--resolution", "2K", "--seed", str(seed), "--wait",
    )
    images = prompt.get("images") or []
    if not images:
        raise SystemExit(f"edit (prompt {prompt.get('id')}) produced no image")
    log(f"edit       prompt_id={prompt['id']}  image={images[0]}")
    return images[0]


def create_pose_tune(astria, edited_image_url, pack_title, index):
    title = f"{pack_title} — pose {index:02d}"
    tune = astria.run(
        "tunes", "create", "--title", title, "--name", "pose",
        "--model-type", "faceid", "--model", "gemini",
        "--image-url", edited_image_url,
    )
    log(f"pose tune  id={tune['id']}  title={title!r}")
    return tune


def create_pack_prompt(astria, text, pack_id, aspect_ratio):
    """Create a pack template prompt — stored on the pack, not rendered here."""
    prompt = astria.run(
        "generate", "--model", "gemini", "--text", text,
        "--num-images", "1", "--resolution", "2K",
        "--aspect-ratio", aspect_ratio,
        "--pack-id", str(pack_id),
    )
    log(f"prompt     id={prompt['id']}  pack_id={pack_id}  aspect_ratio={aspect_ratio}")
    return prompt


def run_shoes(astria, args):
    shoe = find_shoe_tune(astria)
    pack = create_pack(astria, args.pack_title)
    results = []
    for index, image_url in enumerate(args.pose_image_urls, start=1):
        log(f"--- image {index}/{len(args.pose_image_urls)}: {image_url}")
        aspect_ratio = args.aspect_ratio or detect_aspect_ratio(image_url)
        edited_url = subject_edit(astria, image_url, BAREFOOT_EDIT_TEXT)
        pose_tune = create_pose_tune(astria, edited_url, args.pack_title, index)
        text = SHOE_PROMPT_TEMPLATE.format(pose_tune_id=pose_tune["id"], shoe_tune_id=shoe["id"])
        prompt = create_pack_prompt(astria, text, pack["id"], aspect_ratio)
        results.append((prompt["id"], pose_tune["id"]))
    return pack, results


def load_silhouette_spec(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if not isinstance(spec, list) or not spec:
        raise SystemExit('--spec must be a non-empty JSON array of '
                          '{"url": ..., "prompt": ...} objects')
    for item in spec:
        if not item.get("url") or not item.get("prompt"):
            raise SystemExit('every spec item needs a "url" and a "prompt"')
        if POSE_PLACEHOLDER not in item["prompt"]:
            raise SystemExit(f'every spec prompt must contain the literal '
                             f'{POSE_PLACEHOLDER} placeholder for the pose tune')
    return spec


def run_silhouette(astria, args):
    spec = load_silhouette_spec(args.spec)
    pack = create_pack(astria, args.pack_title)
    results = []
    for index, item in enumerate(spec, start=1):
        log(f"--- image {index}/{len(spec)}: {item['url']}")
        aspect_ratio = args.aspect_ratio or detect_aspect_ratio(item["url"])
        edited_url = subject_edit(astria, item["url"], SILHOUETTE_EDIT_TEXT)
        pose_tune = create_pose_tune(astria, edited_url, args.pack_title, index)
        text = item["prompt"].replace(POSE_PLACEHOLDER, f"<faceid:{pose_tune['id']}:1>")
        prompt = create_pack_prompt(astria, text, pack["id"], aspect_ratio)
        results.append((prompt["id"], pose_tune["id"]))
    return pack, results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mode", choices=["shoes", "silhouette"], default="shoes",
                        help="shoes: barefoot edit + shoe-swap prompt (default). "
                             "silhouette: silhouette edit + caller-composed prompt.")
    parser.add_argument("--pack-title", required=True, help="Title for the new pack (typically the page title).")
    parser.add_argument("--pose-image-url", action="append", dest="pose_image_urls",
                        help="shoes mode: a lifestyle image URL. Repeat per pose.")
    parser.add_argument("--spec", help="silhouette mode: path to a JSON array of "
                                       '{"url": ..., "prompt": "...{pose}..."} objects.')
    parser.add_argument("--aspect-ratio", dest="aspect_ratio",
                        help="Force this aspect ratio for every generated prompt "
                             "(e.g. 3:4). Omit to detect each source image's ratio "
                             "and snap to the closest standard one.")
    parser.add_argument("--workspace", help="Workspace id (defaults to the astria CLI's configured workspace).")
    args = parser.parse_args()

    if args.mode == "shoes" and not args.pose_image_urls:
        parser.error("shoes mode needs at least one --pose-image-url")
    if args.mode == "silhouette" and not args.spec:
        parser.error("silhouette mode needs --spec")
    if args.aspect_ratio and args.aspect_ratio not in ASPECT_RATIOS:
        parser.error(f"--aspect-ratio must be one of: {', '.join(ASPECT_RATIOS)}")

    astria = Astria(args.workspace)
    pack, results = (run_shoes if args.mode == "shoes" else run_silhouette)(astria, args)

    print(f"pack_id={pack['id']} pack_slug={pack.get('slug', '')} pack_url=/packs/{pack['id']}")
    for prompt_id, pose_tune_id in results:
        print(f"prompt_id={prompt_id} pose_tune_id={pose_tune_id}")


if __name__ == "__main__":
    main()
