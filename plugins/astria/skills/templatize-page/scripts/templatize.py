#!/usr/bin/env python3
"""Turn lifestyle images into an Astria pack of pose-swap prompts.

For each --pose-image-url:
  1. Send to Nano Banana to remove the subject's shoes (barefoot edit).
  2. Wait for the edited image.
  3. Create a pose tune (faceid) from the edited image — mirrors the
     "Convert to Reference" UI flow.
  4. Create a prompt that pairs the pose tune with the workspace's first
     shoes/sandals reference, assigned to a freshly-created pack named
     after --pack-title.

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
PROMPT_TEMPLATE = (
    "Reproduce the same <faceid:{pose_tune_id}:1.0> pose image but replace "
    "the original shoes with <faceid:{shoe_tune_id}:1.0> shoes"
)


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


def barefoot_edit(astria, image_url):
    # Astria dedups prompts by text within a tune, so an identical edit
    # instruction on two different source photos collides onto one prompt.
    # Append a per-image marker (derived from the source URL) to keep each
    # edit distinct without changing the instruction.
    marker = hashlib.sha1(image_url.encode()).hexdigest()[:10]
    text = f"{BAREFOOT_EDIT_TEXT}\n\n(ref:{marker})"
    prompt = astria.run(
        "generate", "--model", "gemini", "--text", text,
        "--input-image", image_url, "--num-images", "1",
        "--resolution", "2K", "--wait",
    )
    images = prompt.get("images") or []
    if not images:
        raise SystemExit(f"barefoot edit (prompt {prompt.get('id')}) produced no image")
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


def create_swap_prompt(astria, pose_tune_id, shoe_tune_id, pack_id):
    text = PROMPT_TEMPLATE.format(pose_tune_id=pose_tune_id, shoe_tune_id=shoe_tune_id)
    prompt = astria.run(
        "generate", "--model", "gemini", "--text", text,
        "--num-images", "1", "--resolution", "2K",
        "--pack-id", str(pack_id),
    )
    log(f"prompt     id={prompt['id']}  pack_id={pack_id}  pose={pose_tune_id}  shoe={shoe_tune_id}")
    return prompt


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pack-title", required=True, help="Title for the new pack (typically the page title).")
    parser.add_argument("--pose-image-url", action="append", required=True, dest="pose_image_urls",
                        help="A lifestyle image URL. Repeat per pose.")
    parser.add_argument("--workspace", help="Workspace id (defaults to the astria CLI's configured workspace).")
    args = parser.parse_args()

    astria = Astria(args.workspace)
    shoe = find_shoe_tune(astria)
    pack = create_pack(astria, args.pack_title)

    pose_prompts = []
    for index, image_url in enumerate(args.pose_image_urls, start=1):
        log(f"--- image {index}/{len(args.pose_image_urls)}: {image_url}")
        edited_url = barefoot_edit(astria, image_url)
        pose_tune = create_pose_tune(astria, edited_url, args.pack_title, index)
        swap_prompt = create_swap_prompt(astria, pose_tune["id"], shoe["id"], pack["id"])
        pose_prompts.append({"pose_tune_id": pose_tune["id"], "prompt_id": swap_prompt["id"]})

    print(f"pack_id={pack['id']} pack_slug={pack.get('slug', '')} pack_url=/packs/{pack['id']}")
    for entry in pose_prompts:
        print(f"prompt_id={entry['prompt_id']} pose_tune_id={entry['pose_tune_id']}")


if __name__ == "__main__":
    main()
