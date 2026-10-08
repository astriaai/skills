---
name: artboard
description: Legacy alias for the storyboard skill. Use when someone invokes /artboard or asks for the former artboard workflow; explain that it is now Storyboard, then create a text-only cinematic video storyboard in video_prompt and clear the image prompt without generating a grid image.
---

# Artboard is now Storyboard

Tell the user briefly that Artboard is now called Storyboard, then fulfill the
request directly. Do not ask them to restart with another command.

Create a text-only cinematic storyboard from the current draft and references.
Never generate a 4x4 artboard, storyboard image, contact sheet, or first-frame
image.

Use the **storyboard** model-selection rule: preserve an explicit user choice;
otherwise use the first Featured video model, currently Seedance 2.5 720p
(`seedance25_720p`). Do not ask the user to choose a video model or preserve
an automatically populated model over this default.

Write 16 numbered cinematic shots, varying camera scale and angle while keeping
the same references, subject, wardrobe, location, lighting, and grade. Preserve
every `<lora:...>` and `<faceid:...>` token exactly. Give each shot one filmable
action and do not repeat a camera scale twice in a row.

Use existing tunes directly in `video_prompt` as `<faceid:ID:1> CLASS_NAME`
(or their actual `<lora:...>` mention), following **storyboard**. Video mode,
including Seedance 2.5, supports these tokens; Astria resolves their images.
Do not replace tunes with their training-image URLs or put those images in
`image_references`. Use that array only for separately supplied raw images;
omit it when all references are tunes.

Follow the **storyboard** skill for host-specific presentation: use
`present_generation` only when Astria exposes it; otherwise show the English
storyboard text for review. Clear image prompt text in the Astria draft and
preserve ordered raw references. Do not generate for a planning request.

When explicitly asked to generate, use the connected `generate_video` MCP tool
(see **astria-api**) with the exact approved `video_prompt`, chosen
`video_model`, supported duration and a fresh idempotency key. Omit `text`.
Pass raw HTTPS references as the ordered `image_references` array. For local
files, follow **astria-api**'s upload/optional CLI guidance.
