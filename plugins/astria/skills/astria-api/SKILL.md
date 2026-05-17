---
name: astria-api
description: Use when making API calls to Astria for tunes, prompts, packs, or image/video generation (Gemini/Seedream). The reference for the `astria` CLI.
allowed-tools: Bash(astria:*)
---

# Astria CLI Reference

All Astria operations go through the bundled **`astria`** command-line tool. It
handles authentication, the API base URL, and workspace scoping for you — never
build raw `curl` calls and never read API tokens from environment variables.

Output is JSON on stdout, so you can parse ids and image URLs directly.

## Authentication

`astria` resolves credentials automatically:
1. Environment variables, if present (the Astria web app injects these).
2. `~/.astria/config.json`, written by `astria login`.

If a command fails with *"not authenticated"*, tell the user to run:

```bash
astria login          # prompts for an API key (astria.ai/users/edit/api)
```

Check the active account any time with `astria whoami`.

## Profiles

Profiles work like the AWS CLI — keep separate credentials, base URL and
workspace per profile (e.g. production vs a local dev server):

```bash
astria --profile localhost login --base-url http://localhost:3000
astria --profile localhost generate --text "..."
ASTRIA_PROFILE=localhost astria tunes list       # env-var form
```

`--profile <name>` (before the subcommand) or the `ASTRIA_PROFILE` env var
selects it. Each profile is its own file — `~/.astria/config.<name>.json`; the
default profile stays at `~/.astria/config.json`.

## Tune reference syntax

The core concept. A **tune** is a fine-tuned model trained on user images —
"tune" and "reference" mean the same thing. Reference a tune inside prompt text
with `<model_type:id:1> name`:

- `model_type` and `id` come from the tune JSON (`astria tunes get <id>`)
- `name` is the tune's class name and MUST appear right after the `<...>` token
- Combine freely: `<faceid:123:1> woman wearing <faceid:456:1> dress, white studio background`

`<faceid:123:1> woman` is correct; `John` (a bare name the model never trained on) is wrong.

## Workspace scoping

Add `-w/--workspace` to any command:
- `-w <id>` — target a specific workspace
- `-w all` — query across every workspace
- omit it — uses `WORKSPACE_ID`/config default, or personal scope

## Models

`--model` accepts a model name or a raw tune id. **Don't hardcode model
names — discover the current catalog at runtime:**

```bash
astria models              # each model's name, title, tune id and supported resolutions
astria models --refresh    # force-refresh (otherwise cached for a day)
```

The catalog is fetched from the Astria server, so it stays current as models
are added or retired and the tune ids never go stale. The output marks the
`default` model (used when `--model` is omitted) and lists each model's
supported `--resolution` values — a model with no resolutions listed doesn't
accept `--resolution`.

---

## Tunes / references

```bash
astria tunes list                              # all tunes
astria tunes list --title "brown dress"        # by title / product name / SKU
astria tunes list --name shoes --name sandals  # by class name (repeatable)
astria tunes list --gallery --model-type faceid --limit 200   # public gallery
astria tunes get 123
astria tunes create --title "Brown dress" --name dress \
  --description "satin brown dress" \
  --image-url https://example.com/a.jpg --image-url https://example.com/b.jpg
astria tunes create --title "Studio shot" --name woman --image ./face1.jpg --image ./face2.jpg
astria tunes update 123 --name ring --title "Gold ring"
```

`tunes create` takes `--image-url` (remote) and/or `--image` (local file),
both repeatable. `--name` is the subject class (man, woman, dress, shoes,
sandals, pose, …). `--model-type` defaults to `faceid`.

## Prompts

```bash
astria prompts list                            # recent prompts
astria prompts list --pack-id 88               # a pack's template prompts
astria prompts list --tune-id 123              # prompts for one tune
astria prompts list --text "white background" --limit 100 --offset 0
astria prompts get 555 --model nano-banana-pro       # one prompt (needs its tune/model)
astria prompts update 555 --model nano-banana-pro --pack-id 88   # assign a prompt to a pack
```

## Generate images

```bash
astria generate --text "<faceid:123:1> woman, clean white studio background"
astria generate --model nano-banana-pro --text "..." --num-images 4 --aspect-ratio 3:4 --resolution 2K
astria generate --model seedream --text "product photo of headphones on marble" --num-images 2
astria generate --text "recreate this in 4K" --input-image https://example.com/photo.jpg
astria generate --text "..." --pack-id 88 --wait     # assign to pack, block until ready
```

- `--input-image` accepts a URL or a local file path (used for image editing/upscaling).
- `--wait` polls until the images are ready and prints the finished prompt JSON.
  Without it, the command returns immediately — images render asynchronously.
- `aspect_ratio` values: `1:1 16:9 9:16 21:9 9:21 3:2 2:3 5:4 4:5 4:3`.
- `--seed` sets the generation seed. Astria dedups prompts by `(text, seed)`
  within a tune, so the same prompt text reused on different input images
  collapses onto one prompt — pass a distinct `--seed` per call to keep them
  separate without altering the prompt text.

## Generate video

Video runs through the same prompt: the image stage renders the first frame
from `--text`, then the video model animates it from `--video-prompt`.

```bash
astria video --text "a model walking on a runway" \
  --video-model seedance2_fast_720p --video-prompt "camera tracks alongside her" \
  --duration 5 --aspect-ratio 16:9 --wait

astria video --text "zwx man <faceid:123:1> in a dance arena" \
  --video-model kling30_motion_control_pro --video-prompt "match the dance moves" \
  --duration 10 --input-video ./reference.mp4
```

- `--first-frame` / `--last-frame` / `--input-video` accept a URL or local file.
- Motion-control models (`*_motion_control*`, `wan_animate_*`, `dreamactor_m2`,
  `happyhorse_motion_control`) require `--input-video`.

### `video_model` values and cost

Costs are per 5-second base (per 10s for motion-control / fixed-duration
models) and scale linearly with duration. `_audio` models include a soundtrack.

| video_model                     | cost (¢)    | duration options |
|----------------------------------|------------:|------------------|
| seedance_480p                    |          10 | 2–12             |
| seedance_v15_720p                |          14 | 4–12             |
| seedance_v15_audio_720p          |          29 | 4–12             |
| cinematic_video                  |          84 | 5, 10, 15        |
| wan25_720p                       |          53 | 5, 10            |
| wan26_720p / wan26_1080p         |       53/79 | 5, 10, 15        |
| wan27_720p / wan27_1080p         |       55/83 | 5, 10, 15        |
| wan_animate_720p                 |          44 | 10               |
| ltx23_720p / ltx23_1080p         |       17/22 | 5, 10, 15, 20    |
| happyhorse_720p / _1080p         |      77/132 | 3–10             |
| happyhorse_motion_control        |         154 | 10               |
| dreamactor_m2                    |          29 | 10               |
| seedance2_fast_480p / _720p      |      60/140 | 4–15             |
| seedance2_480p / _720p / _1080p  | 120/280/450 | 4–15             |
| veo31_fast_720p / _1080p         |          85 | 4, 6, 8          |
| veo31_fast_4k                    |         264 | 8                |
| veo31_lite_720p / _1080p         |       44/71 | 4, 6, 8          |
| kling30_standard / _pro          |      92/123 | 3–15             |
| kling30_4k                       |         263 | 3–15             |
| kling30_motion_control / _pro    |     277/370 | 10               |

Video output is delivered in the prompt's `images[]` with `content_type=video/mp4`.

## Download

`astria download` saves a prompt's rendered assets (images, or `video/mp4`) to a
local directory. It works from a **prompt id alone** — no tune id needed — and
fetches each prompt fresh from the API, so assets that finished rendering since
the last `cache refresh` are picked up.

```bash
astria download 555 556 557                       # ids as arguments
astria download 555 --out ./shoot                  # custom target directory
astria download --prompts-file ids.txt             # one id per line (or whitespace)
astria prompts list --pack-id 88 | \
  python3 -c 'import sys,json; [print(p["id"]) for p in json.load(sys.stdin)]' | \
  astria download                                  # ids piped on stdin
```

- Prompt ids come from positional args, `--prompts-file`, and/or stdin; they are
  deduped with original order preserved.
- `--out` defaults to `./astria-downloads` and is created if missing.
- Each asset is saved as `prompt-<id>-<NN><ext>` — `<NN>` is a zero-padded
  index, `<ext>` is derived from the URL (`.jpg`/`.png`/`.webp`/`.mp4`/…).
- Downloads run in parallel (~6 at a time).
- A prompt that 404s, errors, or has no images yet is reported in the JSON
  output (`error` field) and does not abort the run.
- The JSON summary lists per prompt `{id, images, saved[], error?}` plus
  `totals {prompts, downloaded, failed}`.

## Packs

Packs are surfaced in the Astria GUI as **Templates** — "pack" and "template" are interchangeable terms for the same object.

```bash
astria packs list
astria packs create --title "Spring Lookbook"
astria prompts update 555 --model nano-banana-pro --pack-id 88   # add a prompt to the pack
```

## Workspaces & landing pages

```bash
astria workspaces list
astria landing get -w 42                        # workspace JSON incl. landing_page_html
astria landing set -w 42 --html-file ./edited.html
```

## Cache (local snapshot + query layer)

`astria cache refresh` snapshots tunes/prompts/packs/user into `./.cache/ws_<slug>/`
so repeated lookups are instant. Each refresh writes both `<resource>.json` files
**and** a SQLite database `cache.db` with indexed `tunes`, `prompts`, `packs`
tables. `astria cache refresh tunes` refreshes one resource; `astria cache path`
prints the directory.

```bash
astria cache refresh                 # pull everything → JSON files + cache.db
astria cache refresh --force         # refresh even if the cache is still fresh
astria cache refresh prompts         # refresh just one resource
astria cache path                    # print the cache directory
```

### Query the local cache (no API calls)

`get`, `find`, `uses` and `stats` read **only** `cache.db` — never the API — so
an agent can cross-reference tunes/prompts/packs instantly. If the DB is missing
they tell you to run `astria cache refresh` first. All emit JSON.

```bash
astria cache get tunes 1234              # one record (full JSON) by id
astria cache get prompts 42367297
astria cache get packs 4001

astria cache find tunes --name woman --title "Red Dress"   # substring filters
astria cache find prompts --pack-id 7 --tune-id 99 --text hat
astria cache find packs --main-class dress --title boot

astria cache uses 4636200                # prompts whose text references tune 4636200
astria cache stats                       # row counts per table + cache age
```

`find` filters are substring matches except `--pack-id` / `--tune-id`, which are
exact. `uses` cross-references a tune id against prompt text — it matches only
prompts that embed the id inside a reference token like `<faceid:4636200:1.0>`
or `<lora:4636200:0.8>`, not bare mentions of the number.

The SQLite schema: each of `tunes` / `prompts` / `packs` has the useful lookup
columns as real indexed columns plus a `json` TEXT column holding the complete
record (`tunes`: id, name, title; `prompts`: id, text, pack_id, tune_id,
num_images, aspect_ratio, resolution; `packs`: id, title, slug, main_class_name).

## Raw API escape hatch

For anything without a dedicated verb:

```bash
astria api GET /prompts --query limit=5 --query offset=0
astria api POST /tunes --form 'tune[title]=Hat' --form 'tune[images][]=@./hat.jpg'
```

## Pagination

List commands accept `--limit N` and `--offset Y`. Default sort is id
descending, so `--offset` walks backwards through history.

## Errors

A non-zero exit prints `astria: <METHOD> <PATH> → HTTP <code>: <message>` on
stderr. Surface the message to the user and suggest a fix. HTTP 422 means a
validation error (missing/invalid fields).
