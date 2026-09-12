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
sequence of raw visual waypoints. Treat a handoff such as "Turn this into a
cinematic scene" as permission to make the missing creative choices when the
draft already contains a reference, scene, and general idea of the frame. Do
not ask the user to repeat those details.

Discard every reference whose tune `name` is `pose`, including its complete
`<lora:...> pose` or `<faceid:...> pose` mention. Never copy a `pose` tune into
the storyboard or use its reference image for the video. This applies even when
copying an otherwise completed prompt verbatim. Do not remove ordinary prose
that describes a subject's pose, stance, or movement.

Preserve every other `<lora:...>` and `<faceid:...>` token exactly. Keep the
same character, products, wardrobe, location, time of day, lighting, and grade
throughout the sequence unless the requested story deliberately changes one.
Preserve every raw image reference exactly and in the same order. Do not turn
raw references into tunes or embed their URLs in the storyboard text. A raw
reference may be a public HTTP(S) URL or an absolute `/workspace/...` path from
an attached file; keep either form unchanged and never rewrite a workspace path
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
- When ordered raw image references are present, make the action progress from
  reference 1 through the final reference in order, describing filmable visual
  transitions between them rather than treating them as unrelated examples.

Write only the numbered shots in the finished video prompt. Do not add a grid
header or describe storyboard tiles.

## Apply it to the composer

Choose the video model before calling `present_generation`:

- Preserve an explicit video model already selected in the current draft.
- Otherwise, reuse the Seedance 2.5 or Seedance 2 model and resolution established
  by the user's prior videos.
- If prior videos do not establish either default, ask the user to choose between
  Seedance 2.5 and Seedance 2. Do not silently use the composer's global default.

Call `present_generation` exactly once with the complete current generation
draft. Put the completed sequence in `video_prompt`, set `text` to the empty
string, discard all `pose` tune references, and preserve the remaining fields
from Current generation draft JSON, including the ordered
`image_reference_urls` array. Set `video_duration` to `15` unless the user
explicitly requested another supported duration. Set `video_model` to the
explicit, established, or user-selected model from the rules above. This writes
the sequence directly to video mode with no image/first-frame prompt. Do not
repeat the storyboard in assistant text and do not emit an `ASTRIA_PROMPT` or
`ASTRIA_VIDEO_PROMPT` command.

If the current image prompt already contains the completed storyboard or the
user asks to move the current prompt into video mode, remove any `pose` tune
reference, then put everything else into the `present_generation`
`video_prompt` field and set `text` to the empty string. Preserve English
content verbatim. If the content is not in English, translate it faithfully
into English without summarizing, prefixing, trimming, or otherwise rewriting
it beyond translation.

## Generate video

When the user explicitly asks to generate, pass the exact approved, pose-tune-
free storyboard as `--video-prompt`, omit `--text` entirely, and default to a
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

```bash
astria video --video-model "<the chosen Seedance 2.5 or Seedance 2 model>" \
  --duration 15 --num-images 1 \
  --image-reference "<reference 1>" --image-reference "<reference 2>" \
  --video-prompt "<the exact approved storyboard>"
```

Include one `--image-reference` for every raw reference, in its original order.
Omit those options when the draft has no raw image references. Use either all
local paths or all URLs in a single command.

Replace `15` only when the user explicitly requested another supported
duration.

Use the current aspect ratio when it is available. Raw `--image-reference`
waypoints are not first-frame prompts. Do not create or pass an artboard image,
an input image, or an image/first-frame prompt unless the user explicitly asks
for one.
