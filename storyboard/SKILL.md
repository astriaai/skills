---
name: storyboard
description: Turn a rough scene, image prompt, or reference-led visual idea into a text-only cinematic video storyboard. Use for /storyboard, "turn this into a cinematic scene", "storyboard this video", or direct text-to-video planning. Write the finished shot sequence into video_prompt and clear the image prompt; never generate a storyboard-grid image.
---

# Video Storyboard

Turn the current draft into a cinematic shot sequence written directly in the
video prompt. Never generate a 4x4 artboard, storyboard image, contact sheet, or
first-frame image.

Always write the finished storyboard and all generation prompt text in English,
even when the user communicates or supplies the draft in another language. The
surrounding conversation may remain in the user's language. Translate
non-English draft content into English while preserving its meaning and all
reference tokens exactly.

## Use the current draft

Read the current image prompt, reference tokens, aspect ratio, and any existing
video prompt from page context. Also read `image_reference_urls` as an ordered
sequence of generated scene images to compose into a full short film. Treat a
handoff such as "Turn this into a cinematic scene" as permission to make the missing creative choices when the
draft already contains a reference, scene, and general idea of the frame. Do
not ask the user to repeat those details.

Discard every reference whose tune `name` is `pose`, including its complete
`<lora:...> pose` or `<faceid:...> pose` mention. Never copy a `pose` tune into
the storyboard or use its reference image for the video. This applies even when
copying an otherwise completed prompt verbatim. Do not remove ordinary prose
that describes a subject's pose, stance, or movement.

Choose references by their role:

- **Ingredients:** people, products, garments, packshots, accessories, and other
  subjects to combine within scenes use tune tokens in `video_prompt`.
- **Scenes:** multiple generated images depicting composed scenes use ordered
  `image_reference_urls` in the composer / `image_references` in MCP to build
  the full short film. Describe motion and transitions through those scenes.

Both can be used in one film: tune tokens keep ingredients consistent while
scene images define the sequence. A dress packshot and a person's face are
ingredients, not successive scene waypoints.

Preserve every other `<lora:...>` and `<faceid:...>` token exactly. Existing
tunes are supported directly in `video_prompt`, including Seedance 2.5:
`<faceid:123:1> woman wearing <faceid:456:1> dress`. Keep the tune's class name
immediately after its token. If the draft identifies selected tunes by ID or
metadata rather than prompt tokens, use their actual IDs, model types and class
names to write the corresponding mentions; use `get_reference` when needed.

Astria resolves these tune mentions and supplies their reference images to the
video model. Do not replace tune tokens with training-image URLs, copy tune
images into `image_reference_urls` / `image_references`, or create duplicate
tunes. A video tool need not expose a separate tune-ID argument: the mentions
in `video_prompt` select the tunes. Never claim video mode only accepts image
URLs or that tune tokens work only for image generation.

Keep the same character, products, wardrobe, location, time of day, lighting,
and grade throughout the sequence unless the requested story changes one.
Preserve every scene image reference exactly and in the same order. Do not
turn these generated scene images into tunes or embed their URLs in the
storyboard text. A scene image reference may be a public HTTP(S) URL or an
absolute `/workspace/...` path from an attached file; keep either form unchanged and never rewrite a workspace path
as `file://` or invent a public URL for it.

## Write the storyboard

Default to 16 numbered shots for a 15-second video unless the user explicitly
requests another supported duration:

- Give each shot one camera scale, one subject, and one filmable action.
- Do not repeat a camera scale twice in a row. Rotate among extreme close-up,
  close-up, medium, long, and extreme long shots.
- Vary angles with front, back, profile, low-angle, top-down, and
  over-the-shoulder views where useful.
- Use shots 1-3 to establish the hero, environment, and motion; shots 4-13 for
  the action montage; and shots 14-16 for a product/detail beat and a closing
  wide shot.
- Put the global light, color grade, grain, and atmosphere in shot 1, then keep
  them continuous.
- Use the identical reference token whenever its subject appears. Chain
  continuity with phrases such as "the same woman", "she", and "her".
- When ordered generated scene images are present, make the action progress
  from scene 1 through the final scene in order, describing filmable motion
  and transitions that connect them into a full short film.

Write only the numbered shots in the finished video prompt. Do not add a grid
header or describe storyboard tiles.

## Apply it to the composer

When running inside Astria and the host exposes `present_generation`, use the
composer workflow below. In other hosts, present the English storyboard text
for review; do not invent a composer tool or submit a generation for a planning
request. Use **astria-api** for the connected MCP transport.

Choose the video model from `list_models` before preparing the draft:

- Preserve a video model only when the user explicitly selected it.
- Otherwise, use the first model in the composer's **Featured** video group:
  currently **Seedance 2.5 720p** (`seedance25_720p`). When featured ordering is
  unavailable in the host, use `seedance25_720p` from `list_models`.
- Do not ask the user to choose between Seedance 2.5 and Seedance 2. Prior videos
  and an automatically populated draft or catalog default do not override the
  featured default.

Call `present_generation` exactly once with the complete current generation
draft. Put the completed sequence in `video_prompt`, set `text` to the empty
string, discard all `pose` tune references, and preserve the remaining fields
from Current generation draft JSON, including the ordered generated scene
`image_reference_urls` array. Set `video_duration` to `15` unless the user
explicitly requested another supported duration. Set `video_model` to the
explicitly user-selected model or the featured default from the rules above. This writes
the sequence directly to video mode with no image/first-frame prompt. Do not
repeat the storyboard in assistant text.

If the current image prompt already contains the completed storyboard or the
user asks to move the current prompt into video mode, remove any `pose` tune
reference, then put everything else into the `present_generation`
`video_prompt` field and set `text` to the empty string. Preserve English
content verbatim. If the content is not in English, translate it faithfully
into English without summarizing, prefixing, trimming, or otherwise rewriting
it beyond translation.

## Generate video

When the user explicitly asks to generate, pass the exact approved, pose-tune-
free storyboard as `video_prompt`, omit `text` entirely, and default to a
15-second duration unless the user explicitly requested another supported
duration:

- If `prompt.text` still contains the content and `video_prompt` is empty,
  discard any `pose` tune reference, move the remaining `prompt.text` into
  `video_prompt`, and clear `prompt.text` before generation. Preserve English
  content byte-for-byte. Translate non-English content faithfully into English;
  do not expand, summarize, prefix, trim, or otherwise rewrite it beyond
  translation during this generation step.
- If `video_prompt` is already populated, discard any `pose` tune reference and
  use English content as-is; translate non-English content faithfully into
  English before generation.

Call `generate_video` with the chosen catalog `video_model`, the exact
`video_prompt`, `duration: "15"`, `num_images: "1"`, the current aspect ratio
when available, and a fresh `idempotency_key`. Keep existing tune mentions
in `video_prompt`; do not also attach their training images. Include
`image_references` for the generated scene images being composed into the film,
as an array of HTTPS URLs in the intended scene order. Use tune tokens for
products/packshots and other ingredients. Omit the array when there are no
scene images. For local scene-image paths, obtain real uploaded URLs or use
the optional CLI workflow in **astria-api**. Do not rewrite local paths into invented URLs.

Replace `"15"` only when the user requested another supported duration. Generated
scene waypoints are not first-frame prompts. Do not create or pass an artboard
image or an image/first-frame prompt unless the user asks for one.
