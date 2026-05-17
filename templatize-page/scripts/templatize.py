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
prompt to it.

Every API call goes through the bundled `astria` CLI, which handles auth and
workspace scoping. No environment variables and no extra Python packages
needed — only the standard library.
"""
import argparse
import hashlib
import json
import subprocess
import sys

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
    "Reproduce the same <faceid:{pose_tune_id}:1.0> pose image but replace "
    "the original shoes with <faceid:{shoe_tune_id}:1.0> shoes"
)
POSE_PLACEHOLDER = "{pose}"


def log(msg):
    print(msg, file=sys.stderr, flush=True)


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


def create_pack_prompt(astria, text, pack_id):
    """Create a pack template prompt — stored on the pack, not rendered here."""
    prompt = astria.run(
        "generate", "--model", "gemini", "--text", text,
        "--num-images", "1", "--resolution", "2K",
        "--pack-id", str(pack_id),
    )
    log(f"prompt     id={prompt['id']}  pack_id={pack_id}")
    return prompt


def run_shoes(astria, args):
    shoe = find_shoe_tune(astria)
    pack = create_pack(astria, args.pack_title)
    results = []
    for index, image_url in enumerate(args.pose_image_urls, start=1):
        log(f"--- image {index}/{len(args.pose_image_urls)}: {image_url}")
        edited_url = subject_edit(astria, image_url, BAREFOOT_EDIT_TEXT)
        pose_tune = create_pose_tune(astria, edited_url, args.pack_title, index)
        text = SHOE_PROMPT_TEMPLATE.format(pose_tune_id=pose_tune["id"], shoe_tune_id=shoe["id"])
        prompt = create_pack_prompt(astria, text, pack["id"])
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
        edited_url = subject_edit(astria, item["url"], SILHOUETTE_EDIT_TEXT)
        pose_tune = create_pose_tune(astria, edited_url, args.pack_title, index)
        text = item["prompt"].replace(POSE_PLACEHOLDER, f"<faceid:{pose_tune['id']}:1.0>")
        prompt = create_pack_prompt(astria, text, pack["id"])
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
    parser.add_argument("--workspace", help="Workspace id (defaults to the astria CLI's configured workspace).")
    args = parser.parse_args()

    if args.mode == "shoes" and not args.pose_image_urls:
        parser.error("shoes mode needs at least one --pose-image-url")
    if args.mode == "silhouette" and not args.spec:
        parser.error("silhouette mode needs --spec")

    astria = Astria(args.workspace)
    pack, results = (run_shoes if args.mode == "shoes" else run_silhouette)(astria, args)

    print(f"pack_id={pack['id']} pack_slug={pack.get('slug', '')} pack_url=/packs/{pack['id']}")
    for prompt_id, pose_tune_id in results:
        print(f"prompt_id={prompt_id} pose_tune_id={pose_tune_id}")


if __name__ == "__main__":
    main()
