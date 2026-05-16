---
name: templatize-page
description: Use when the user asks to turn a fashion / lookbook webpage into an Astria pack — scrapes the page, drops product-only shots, turns the remaining lifestyle photos into pose references (via Nano Banana barefoot edit), and creates one prompt per pose pairing it with the workspace's first shoes/sandals reference. Trigger phrases — "templatize this page", "make a pack from this lookbook", "/templatize-page <url>".
allowed-tools: Bash(astria:*), Bash(python3:*), Bash(curl:*), Bash(mkdir:*), Read
---

# Templatize Page

Given a brand's lookbook / collection / editorial URL, build an Astria pack
whose prompts let the user swap that page's footwear for any of their
workspace's shoe references.

End state: one new pack (titled after the page), N new `pose` tunes (one per
surviving lifestyle image), N new prompts inside the pack of the form:

```
Reproduce the same <faceid:{pose_tune_id}:1.0> pose image but replace
the original shoes with <faceid:{shoe_tune_id}:1.0> shoes
```

Two Python scripts ship with this skill in `scripts/` (stdlib only). They call
the bundled `astria` CLI for every API operation, so authentication and
workspace scoping are handled for you — see the `astria-api` skill.

## Workflow

### 1. Scrape the page

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scrape.py" <url>
```

Emits JSON: `{"title": "...", "url": "<final url>", "images": [{"url": "...", "alt": "...", "width": ..., "height": ...}, ...]}`. The page `<title>` (or `og:title` when set) is the pack title. Capture both — `title` for the pack, `images` for the next step.

### 2. Classify each image (drop packshots)

The scrape returns every visible image — including product-only shots (a shoe
on a plain background, no model) that we do NOT want as poses. Filter visually:

1. Download every candidate to `/tmp/` so they can be read locally:
   ```bash
   mkdir -p /tmp/templatize && i=0
   for url in <url1> <url2> ...; do
     i=$((i+1)); curl -sSL -o "/tmp/templatize/img_${i}.jpg" "$url"
   done
   ```
2. `Read` each `/tmp/templatize/img_*.jpg` file. For each one decide:
   - **Keep** when a person is visible wearing or holding product (a lifestyle / editorial / on-model shot).
   - **Drop** when the frame is a product alone — a single shoe / sandal / handbag on a plain or studio backdrop with no human figure. Also drop logos, banners, swatches.
   - **When in doubt, keep.** A borderline cropped-from-the-knees shot is fine; the edit step will normalize it.
3. Build the list of surviving original URLs (the public URLs — `templatize.py` passes them to Nano Banana).

### 3. Templatize

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/templatize.py" \
  --pack-title "<page title>" \
  --pose-image-url <surviving_url_1> \
  --pose-image-url <surviving_url_2> \
  ...
```

The script handles everything else end-to-end:

1. Looks up the workspace's first shoe/sandal reference via `astria tunes list --name shoes --name sandals`. Aborts if there is none.
2. Creates the pack via `astria packs create`.
3. Per image: sends a Nano Banana "remove shoes → barefoot" edit and waits for it, creates a `pose` faceid tune from the edited image, creates a swap prompt with the `<faceid:pose><faceid:shoe>` template, and assigns it to the new pack.

Pass `--workspace <id>` to target a specific workspace; otherwise the `astria`
CLI's configured workspace is used.

The script prints one status line per artifact to stderr (`edit ...`,
`pose tune id=...`, `prompt id=... pack_id=...`) and a final summary block to
stdout with the new pack ID and per-pose `prompt_id` / `pose_tune_id` pairs.

### 4. Report

Surface the new pack to the user — quote the pack title + ID, the number of
prompts created, and point them to `/packs/<pack_id>`.

## Worked example

User: `/templatize-page https://www.gentlesouls.com/lookbook/spring-2026`

1. `scrape.py` → JSON with `title="Gentle Souls Spring 2026 Lookbook"` and ~14 images.
2. Download all 14 to `/tmp/templatize/`. Read each one. 5 are packshots (single shoe, white background) — drop them. 9 are on-model lifestyle photos — keep.
3. `templatize.py --pack-title "Gentle Souls Spring 2026 Lookbook" --pose-image-url https://.../look-01.jpg ...` (9 URLs).
4. Report: "Created pack **Gentle Souls Spring 2026 Lookbook** (id 4821) with 9 pose-swap prompts using shoe reference *Brown leather sandal* (id 4457109) — find it at /packs/4821."

## Notes

- The barefoot edit prompt is deliberately conservative: it keeps pose / outfit / lighting / framing identical so the resulting tune captures the original styling, only minus the original footwear.
- `tune[name]` is hardcoded to `pose` (every output should be usable as a pose ref regardless of the original subject).
- The pack uses `model_type=faceid` because the prompts inside reference faceid tunes (pose + shoe). Generation defaults: `resolution=2K`, `num_images=1`; aspect ratio is left unset so the barefoot edit follows the input image (Gemini rejects `aspect_ratio=auto`).
- If the page is gated (Shopify login wall, paywall) `scrape.py` returns empty `images` — fall back to asking the user for direct image URLs.
