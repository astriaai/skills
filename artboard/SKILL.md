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

The `--text` is **the 16 numbered shots themselves** — nothing else. No
generic "A 4x4 storyboard artboard…" header; the prompt IS the tile
descriptions. The 4x4 grid layout is communicated to GPT Image 2 by the
numbered list (1–16) plus the CLI's `--aspect-ratio` and `--num-images 1`
flags.

```
1) <shot scale> of <subject + reference tokens>, <one clear action>, <technique>. <atmosphere — name the light, grade and grain here so every tile inherits it>.
2) ...
...
16) ...
```

Each shot is one short line. Template per shot:

`N) <shot scale> of <subject with reference tokens>, <one clear action><, optional cinematic technique>.`

Tile 1 carries the global style cue (light, color grade, grain, atmosphere)
once — the remaining 15 tiles inherit it through "the same woman", "her",
re-used reference tokens, and named continuity.

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
```

## Worked example B — urban / single hero product (9:16 vertical video)

```
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
```

## Workflow

1. **Inventory the references from recent usage.** The chat session is
   already scoped to the workspace, so the commands below need no `-w`.
   - `astria prompts list --limit 20` — the last ~20 prompts of any kind
     (Nano Banana, GPT Image 2, video, …). Scan each one's `text` for
     `<faceid:NNNN:1.0>` tokens; these IDs are the references the user
     has actually been working with. Count appearances so you know which
     are heavily used.
   - For each unique ID, `astria tunes get <id>` to read the tune's
     `name` (class — `woman`, `boy`, `dress`, `shoes`, …), `title`
     (display name — `Hazel`, `goods_484475_sub14_3x4 copy`, …) and an
     image you can show as a thumbnail.

   That curated set — the references already present in recent prompts —
   IS the reference list you present in step 2. Don't enumerate the full
   workspace tunes; the user will pick from what they've been using.
   Don't assume an artboard already exists; treat any recent prompts as
   signal. Gather the candidates yourself — don't send the user off to
   browse.
2. **Clarify the brief — ask before writing.** Use one `AskUserQuestion` call;
   per the interaction rule, put *only* questions in that turn:
   - **Final video aspect ratio** — *always* ask (`16:9` / `9:16` / `1:1` /
     `4:5`). The tiles must match the video the artboard will drive.
   - **Topic / action / vibe** — if the user hasn't already said what the video
     is about, ask for the subject, setting and mood.
   - **References — always a multi-select, every reference from step 1
     listed as its own option.** Single `AskUserQuestion` with
     `multiSelect: true`. Each option is one of the references discovered
     in step 1 — label it with the tune's `title` (display name), put the
     `name` class in the description ("woman", "shirt", "shoes", …), and
     include the tune's image as a thumbnail. The user picks which
     subset appears in the artboard. If a needed reference is missing,
     ask for an image and create the tune with `astria tunes create`.
     **"Generic cast" is never the default** — every tile that shows the
     character or a product must carry a `<faceid:NNNN:1.0>` token.

   Skip any question whose answer the user already gave; only ask what's
   genuinely unclear (except the references multi-select — that one always
   happens).
3. **Write the artboard** — 16 numbered shots — following the shot-scale
   rotation, consistency rules and story arc above. No generic header line;
   tile 1 carries the global style cue (light, color grade, grain, atmosphere)
   so the remaining 15 tiles inherit it. Set `--aspect-ratio` to the ratio
   chosen in step 2.
4. **Show the user the full prompt text** for review/edit before generating.
5. **Generate** (see below).
6. **Hand off to video — same prompt drives the cut.** Run `astria video`
   with the **same 16 numbered shots** as `--video-prompt`, prefixed with
   one line: **"A cinematic video with the below video shots."** That
   reframes the list from "tiles in a grid" to "cuts in a 15-second
   sequence" — the shot descriptions stay verbatim, including their
   `<faceid:NNNN:1.0>` tokens, so cast continuity carries into the cut.

   **Do NOT pass the artboard image as `--input-image`.** The artboard
   exists to pre-visualize the story for the user before the video pass;
   it is not a video first frame. Feeding a 4×4 grid to the video model
   gets you a grid animating in place, not a cinematic cut.

   ```bash
   astria video --video-model seedance2_720p \
     --aspect-ratio <VIDEO_RATIO> --num-images 1 --duration 15 \
     --text "<the artboard's shot 1, verbatim — sets the first video frame>" \
     --video-prompt "A cinematic video with the below video shots.
   1) <shot 1 — copied verbatim from the artboard's --text>
   2) <shot 2>
   ...
   16) <shot 16>"
   ```

   `--num-images 1` is required for video — without it the API returns
   `{"num_images":["must be 1 for --video"]}`.

   **`--text` must be a real first-frame description, not a placeholder.**
   Astria generates the video's first frame from this text (via Nano
   Banana, by default) and seedance animates from there. A vague string
   like `"First frame placeholder."` produces an unrelated image
   (verified live — yields a generic photo with the faceids in some
   random scene), and seedance then has nothing coherent to animate
   from. Copy the artboard's **shot 1** verbatim into `--text` so the
   first frame matches the artboard's opening close-up.

   **Reference budget.** Video models cap the number of unique
   `<faceid:NNNN:1.0>` references per prompt much more tightly than image
   models — over the cap and the generation errors. Keep the video prompt
   focused: prefer the face references (cast continuity is what carries
   the cut) and drop most garment references, describing wardrobe in
   plain words instead. If the artboard used many garment references,
   trim them for the video prompt; the artboard already showed the user
   how the garments look.

## Generation command

```bash
astria generate --model gpt-image-2 --aspect-ratio <VIDEO_RATIO> --num-images 1 \
  --text "1) Close-up of the <faceid:4644372:1.0> woman laughing, wearing a straw hat. Natural sunlight, soft film grain, warm beach atmosphere.
2) Long shot of the same woman wearing the <faceid:4767051:1.0> dress and the <faceid:4767037:1.0> bag, holding her hat...
...
16) Long shot — the surfboard set in the sand beside the <faceid:4767037:1.0> bag, the woman's silhouette walking toward the water."
```

- `--model gpt-image-2` — required; GPT Image 2 handles numbered grids best.
- `--aspect-ratio` — set to the **final video's** aspect ratio (confirmed with
  the user); `--num-images 1` for a single artboard image.
- Plain newlines between each numbered shot are fine inside `--text`.
- Bump `--num-images` to 2 only if the user wants layout variants to choose
  from.

## Constraints & tips

- **16 tiles, 4x4** is the default. Going past ~18 makes individual tiles too
  small for the video pass to read.
- **References are mandatory.** Every tile that shows the character or a
  product must carry its `<faceid:NNNN:1.0>` token. Bare descriptions
  ("teenage boy", "young woman") lose likeness and break the artboard's job
  as a text-to-video reference. If the user hasn't told you which references
  to use, ask via the multi-select question in step 2 — never default to a
  generic cast.
- One clear, *filmable* action per tile; the video model animates the motion
  between cuts.
- Keep one color grade and lighting mood named in tile 1 — consistency across
  tiles is the whole point of an artboard.
- If results drift (different face per tile, wrong product), check the tune's
  `name` and `orig_images` per the `prompt-writing` skill's "Reviewing bad
  results" section.
