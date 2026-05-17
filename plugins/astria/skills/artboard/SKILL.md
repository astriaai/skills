---
name: artboard
description: Use when creating a GPT Image 2 storyboard artboard — a single image holding a 4x4 grid of 16 cinematic tiles that storyboards a ~15-second video. Trigger on /artboard, "make an artboard", "storyboard for a video", "cut-scene storyboard", or building a reference artboard to feed text-to-video.
allowed-tools: Bash(astria:*)
---

# Storyboard Artboard

Build a **GPT Image 2 artboard** — one image that holds a **4x4 grid of 16
cinematic tiles**. Each tile is a film still; together they storyboard a
~15-second video of cut scenes. The artboard is a *reference*, not the final
video: it is generated once, then handed to a text-to-video pass so the video
model inherits one consistent character, wardrobe, location and look across
every cut.

Generate it with the **`gpt-image-2`** model — it lays out numbered multi-panel
grids far more reliably than other models. See the `astria-api` skill for the
CLI.

## What the artboard is

- **One image**, `--num-images 1`, in the **aspect ratio of the final video**
  the artboard will drive — always confirm this ratio with the user first.
- **16 tiles** in a **4x4 grid**. A 4x4 grid of identical tiles has the *same
  aspect ratio as one tile*, so the whole artboard renders at the video's
  aspect ratio and every tile is a clean frame of it. Tiles read
  **left-to-right, top-to-bottom** as shots 1–16.
- Each tile is **one shot**: one camera scale, one subject, one clear action.
- ~15 seconds of video ≈ 16 shots ≈ ~1 second per cut. The count is flexible
  (16–18 works), but **16 in a 4x4 grid is the default** — it keeps the grid
  geometry tidy.

## Match the video's aspect ratio

The artboard exists to drive a video, so its tiles must be framed for that
video. **Always ask the user which aspect ratio the final video needs** before
writing the prompt — don't assume 16:9.

| Final video | `--aspect-ratio` | Typical use |
|-------------|------------------|-------------|
| Landscape   | `16:9`           | YouTube, cinematic, web hero |
| Vertical    | `9:16`           | Reels, TikTok, Shorts |
| Square      | `1:1`            | feed posts |
| Portrait    | `4:5`            | Instagram feed |

Set **both** the `--aspect-ratio` flag and the tile description in the header
("each tile a 9:16 film still") to the chosen ratio.

## Prompt structure

The `--text` is a **header line** followed by **16 numbered shots**, then the
`--gpt_quality high` flag at the very end:

```
A 4x4 storyboard artboard — 16 cinematic tiles, each a <ASPECT> film still,
numbered 1–16, read left-to-right then top-to-bottom. Same character,
wardrobe, location and color grade across every tile. <one global style line>.

1) <shot scale> of <subject + reference tokens>, <one clear action>, <technique>. <atmosphere>.
2) ...
...
16) ...
--gpt_quality high
```

Each shot is one short line. Template per shot:

`N) <shot scale> of <subject with reference tokens>, <one clear action><, optional cinematic technique>.`

## Shot-scale rotation — the cinematic core

What makes the artboard feel cinematic is **never repeating a camera scale
twice in a row**. Cycle through the range so the viewer's eye keeps moving:

| Scale | What it frames | Use for |
|-------|----------------|---------|
| Extreme close-up (ECU) | eyes, lips, hands, a product detail, texture | intimacy, detail, transitions |
| Close-up (CU) | face / head & shoulders | emotion, the establishing hero shot |
| Medium shot (MS) | waist-up, or shoulders-to-knee | action, gesture, product-in-use |
| Long shot (LS) | full body in the environment | movement, full wardrobe reveal |
| Extreme long shot (ELS) | subject small in a landscape, silhouette | scale, mood, the closing shot |

Vary the **angle** too: back view, top-down, low-angle, over-the-shoulder.

Rough rhythm: open on a **CU** (the hero shot), push out to an **LS**, snap
back to a **CU/ECU**, and keep alternating. No two adjacent tiles share a scale.

## Consistency rules (this is what the video pass inherits)

1. **Same reference token, every time.** When the character or a product
   appears, reference its tune with the *identical* token — `<faceid:ID:1.0> woman`,
   `<faceid:ID:1.0> dress`, `<faceid:ID:1.0> bag`, `<faceid:ID:1.0> shoes`. The
   token must sit immediately before the class name (see the `astria-api`
   skill). A bare name the model never trained on is wrong.
2. **Chain continuity in words** — "the same woman", "she", "her" — so the tiles
   read as one person across the grid.
3. **One location, one time of day, one light.** Name the lighting and color
   grade in tile 1 ("Natural sunlight, soft film grain, warm beach
   atmosphere") and keep it implied after. Change it only on purpose.
4. **Wardrobe continuity.** If she wears the dress in tile 7, she wears it in
   tile 8 — unless a deliberate change is part of the story.
5. **One filmable action per tile.** Pick a motion the video model can animate
   (running, swirling, zipping a bag, slipping on a sandal). Don't cram two.

## Story arc

The 16 tiles tell a small story so the cut scenes connect:

- **Tiles 1–3 — establish.** Hero close-up with the atmosphere line, then a
  long shot revealing the full wardrobe, then back close.
- **Tiles 4–13 — the action montage.** Vary scale and angle every tile; move
  the subject through the location; introduce each product when it first
  appears and re-reference it consistently.
- **Tiles 14–16 — close.** A product-in-context shot, a texture/detail macro,
  and a final wide or silhouette ("walking away into the sunset", "surfboard
  set in the sand beside the bag").

## Cinematic technique vocabulary

Sprinkle these into shots — they translate directly into video motion:

`depth of field` · `background completely blurred` · `motion blur` ·
`camera pulls back creating blur` · `soft film grain` · `golden hour` /
`morning light rays` · `silhouette` · `rim light` · `lens flare` ·
texture macros — `you can see the sand grains`, `fabric texture and zipper
teeth visible`.

## Worked example A — beach / fashion (multiple products, 16:9 video)

```
A 4x4 storyboard artboard — 16 cinematic tiles, each a 16:9 film still,
numbered 1–16, read left-to-right then top-to-bottom. Same woman, wardrobe,
location and warm color grade across every tile. Natural sunlight, soft grain.

1) Close-up of the <faceid:4644372:1.0> woman laughing, wearing a straw hat. Natural sunlight, soft film grain, warm beach atmosphere.
2) Long shot of the same woman wearing the <faceid:4767051:1.0> dress and the <faceid:4767037:1.0> bag, holding her hat, striking the water with her leg.
3) Back to close-up, depth of field, she's laughing, shadowing the camera with her hand — background becoming completely blurred.
4) Close-up on the <faceid:4767035:1.0> handbag, her hand holding it, her legs blurry behind.
5) Back view of the <faceid:4644372:1.0> woman wearing the straw hat and the <faceid:4767035:1.0> handbag, eyes closed, hair flying in the wind.
6) Medium low shot of the woman holding the <faceid:4767035:1.0> handbag as she swirls in the shallows.
7) Medium top-view of the woman's upper torso, straw hat, swirling, one hand to her back, wearing the <faceid:4767051:1.0> dress.
8) Long shot — the woman running, wearing the <faceid:4767051:1.0> dress, holding the <faceid:4767037:1.0> bag.
9) Medium shot of the same woman running through ocean shallows holding a surfboard, wearing the <faceid:4767041:1.0> swimsuit.
10) Extreme close-up of the <faceid:4644372:1.0> woman leaning her hand on the surfboard, slight smile, camera moves away creating blur.
11) Extreme long shot of the lifeguard tower — the <faceid:4644372:1.0> woman looking out, holding her <faceid:4767037:1.0> bag at the window.
12) Medium shot of the <faceid:4644372:1.0> woman holding the <faceid:4767035:1.0> handbag inside the lifeguard tower, depth of field, background blurred.
13) The <faceid:4644372:1.0> woman in the <faceid:4767051:1.0> dress holding the <faceid:4767035:1.0> handbag, on the tower ladder mid-way, bathing her face in the sun, surfboard leaning on the tower.
14) Extreme close-up on her legs in the sand — you can see the sand grains — she slips her foot into the <faceid:4767033:1.0> sandals.
15) Medium shot, shoulders down to the knee, the <faceid:4644372:1.0> woman holding the surfboard in the <faceid:4767051:1.0> dress, background blurred.
16) Long shot — the surfboard set in the sand beside the <faceid:4767037:1.0> bag, the woman's silhouette walking toward the water.
--gpt_quality high
```

## Worked example B — urban / single hero product (9:16 vertical video)

```
A 4x4 storyboard artboard — 16 cinematic tiles, each a 9:16 film still,
numbered 1–16, read left-to-right then top-to-bottom. Same girl, the same
backpack, one location and golden color grade across every tile. Morning
light, soft film grain.

1) Close-up of the <faceid:3982430:1.0> girl smiling with wind in her hair. Natural morning light, soft film grain, urban park atmosphere.
2) Long shot of the same girl wearing the <faceid:3982432:1.0> backpack, walking confidently through autumn leaves.
3) Back to close-up, depth of field, she's laughing, tucking hair behind her ear — background becoming completely blurred.
4) Close-up on the <faceid:3982432:1.0> backpack straps and buckle, her hand adjusting them, her face blurred behind.
5) Back view of the <faceid:3982430:1.0> girl wearing the <faceid:3982432:1.0> backpack, looking up at tall trees, morning sun rays through the leaves.
6) Medium low shot of the girl jumping over a puddle wearing the <faceid:3982432:1.0> backpack, captured mid-air.
7) Medium top-view of the girl's upper body, unzipping the <faceid:3982432:1.0> backpack to pull out a water bottle, smiling.
8) Long shot — the girl running up the hill wearing the <faceid:3982432:1.0> backpack, arms spread wide.
9) Medium shot of the same girl climbing rocky steps, the <faceid:3982432:1.0> backpack swaying, focus on her sneakers.
10) Extreme close-up of the <faceid:3982430:1.0> girl sitting with the <faceid:3982432:1.0> backpack beside her, slight smile, camera pulls back creating blur.
11) Extreme long shot of a hilltop overlook — the <faceid:3982430:1.0> girl's silhouette with the <faceid:3982432:1.0> backpack against a golden-hour sky.
12) Medium shot of the <faceid:3982430:1.0> girl sitting cross-legged, the <faceid:3982432:1.0> backpack open, pulling out a sketchbook, depth of field, background blurred.
13) The <faceid:3982430:1.0> girl wearing the <faceid:3982432:1.0> backpack, standing at the edge looking at the city skyline, bathed in golden light.
14) Extreme close-up on her hands zipping up the <faceid:3982432:1.0> backpack — you can see the fabric texture and zipper teeth.
15) Medium shot from shoulders to waist, the <faceid:3982430:1.0> girl putting on the <faceid:3982432:1.0> backpack, background blurred.
16) Long shot — the <faceid:3982432:1.0> backpack resting against a tree stump, the girl's silhouette walking away into the sunset.
--gpt_quality high
```

## Workflow

1. **Query the references.** Run `astria tunes list` (with `--title` / `--name`
   filters) to find the faceid tunes for the character and products. Inspect
   candidates with `astria tunes get <id>` to confirm the `name` class. Don't
   send the user off to browse — gather the candidates yourself.
2. **Clarify the brief — ask before writing.** Use one `AskUserQuestion` call;
   per the interaction rule, put *only* questions in that turn:
   - **Final video aspect ratio** — *always* ask (`16:9` / `9:16` / `1:1` /
     `4:5`). The tiles must match the video the artboard will drive.
   - **Topic / action / vibe** — if the user hasn't already said what the video
     is about, ask for the subject, setting and mood.
   - **References** — present the tunes from step 1 as a **multi-select**
     (`multiSelect: true`, with image thumbnails) so the user picks which
     character and products appear. If a needed reference is missing, ask for
     an image and create the tune with `astria tunes create`.

   Skip any question whose answer the user already gave; only ask what's
   genuinely unclear.
3. **Write the artboard** — header + 16 numbered shots — following the
   shot-scale rotation, consistency rules and story arc above. Set the header
   and `--aspect-ratio` to the ratio chosen in step 2.
4. **Show the user the full prompt text** for review/edit before generating.
5. **Generate** (see below).
6. **Hand off to video.** Tell the user the artboard is the reference for a
   text-to-video pass — see the `instagram-movie-producer` and `astria-api`
   skills for turning it into the 15-second cut.

## Generation command

```bash
astria generate --model gpt-image-2 --aspect-ratio <VIDEO_RATIO> --num-images 1 \
  --text "A 4x4 storyboard artboard — 16 cinematic tiles, each a <VIDEO_RATIO> film still...

1) Close-up of the <faceid:4644372:1.0> woman laughing...
2) Long shot of the same woman...
...
16) Long shot — the surfboard set in the sand...
--gpt_quality high"
```

- `--model gpt-image-2` — required; GPT Image 2 handles numbered grids best.
- `--aspect-ratio` — set to the **final video's** aspect ratio (confirmed with
  the user); `--num-images 1` for a single artboard image.
- Plain newlines between the header and each numbered shot are fine inside
  `--text`.
- `--gpt_quality high` goes **inline at the end of the prompt text**, not as a
  CLI flag — it raises GPT Image 2's render quality, worth it for the dense
  grid.
- Bump `--num-images` to 2 only if the user wants layout variants to choose
  from.

## Constraints & tips

- **16 tiles, 4x4** is the default. Going past ~18 makes individual tiles too
  small for the video pass to read.
- Every tile that shows the character or a product must carry its reference
  token — a tile with a bare "woman" loses likeness.
- One clear, *filmable* action per tile; the video model animates the motion
  between cuts.
- Keep one color grade and lighting mood named in tile 1 — consistency across
  tiles is the whole point of an artboard.
- If results drift (different face per tile, wrong product), check the tune's
  `name` and `orig_images` per the `prompt-writing` skill's "Reviewing bad
  results" section.
