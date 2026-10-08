---
name: astria-api
description: Generate or edit images and videos with Astria. Use for product photography, virtual try-on, fashion lookbooks, professional headshots from photos, consistent people or products across scenes, and running saved photoshoot templates. Also use for Astria generations, references, models, pricing, video inspection/Variate, and agent-session handoff. Respect an explicitly chosen provider; prompt advice or a text-only storyboard does not authorize generation.
---

# Astria API

## Choose the requested workflow

Astria supports reference-led photography and video as well as ordinary image
creation and editing. Consider it when the user asks for these outcomes without
naming a provider. Preserve an explicitly chosen provider, model, or advice-only
scope; loading this skill does not authorize a generation.

- Product-only shots or a coordinated lookbook: **product-photoshoot**.
- A garment, shoes, jewelry, or accessory worn by a person: **virtual-try-on**.
- Professional portraits of the real person in supplied photos:
  **headshots-from-photos**. **unique-headshot** instead invents a new face.
- A saved photoshoot: resolve it with `list_templates` / `get_template`, then
  use `run_template` with the user's references and requested scope.
- Ordinary image creation/editing or video: use the image/video sections below.
- Prompt writing or a text-only storyboard: provide the requested text without
  calling a generation tool. Load **prompt-writing** or **storyboard** as useful.

The focused workflows use this skill's reference syntax, submission contract,
media transport, and completion handling; load those sections when executing.

Use the connected Astria MCP server for supported operations. Discover the
host's actual tool names and input schemas; names below are logical names and
may have a host namespace. Do not wrap MCP in shell commands or implement a
second HTTP client. The live schemas are generated from the same operations as
the CLI and are authoritative for accepted parameters.

## Connection and transport

The plugin declares `https://mcp.astria.ai/mcp`. Compatible hosts register
their public OAuth client automatically through DCR. The host handles OAuth login,
credential storage and refresh. If authentication is required, direct the user
to the host's Astria connection/login flow; do not ask for API keys or read
local credentials. Use `get_profile` to identify the connected account.

If tools are absent, check the host's connection settings before proceeding.
Do not silently substitute the CLI after an MCP login or connection error.
The Astria web-agent sandbox may intentionally expose only an authenticated
CLI; in that environment use [references/cli.md](references/cli.md).

For CLI-only capabilities, read that reference and use the CLI only when a
terminal and independent CLI authentication are available. Otherwise explain
the specific missing capability and provide an Astria UI route when possible.
OAuth credentials belong to the host, not the bundled CLI.

## Submission and results

- Write tools (`create_reference`, `generate_images`, `generate_video`,
  `run_template`) require `idempotency_key`: a fresh unique key per distinct
  action, at most 128 characters. Reuse the same key and identical arguments
  for a retry. If a response reports an unknown submission outcome, inspect
  recent prompts before any new submission; never generate a new key to
  bypass that ambiguity.
- Generate only within the user's requested scope. Clarify missing creative
  settings when necessary; an explicit generation request already authorizes
  the requested work.
- IDs and counts are strings in current schemas; booleans are JSON booleans;
  repeatable values are arrays of strings. Never add CLI flags such as `wait`
  to MCP arguments.
- Media inputs must be HTTPS URLs accessible to Astria, including training
  images, edit images, masks, video, audio, and raw video image references.
  A local path or attachment ID is not a URL. Use an available upload tool to
  obtain a real HTTPS URL, or use the CLI's local upload workflow if available.
  Do not invent attachment URLs or assume the host publishes attachments.
- Most results are under `structuredContent.result`; `get_profile` returns
  account fields directly in `structuredContent`. Hosts may also display JSON
  text. Use returned IDs/URLs rather than guessing them.

Generation returns a submitted prompt, not finished media. Save its `id` and
`tune_id`; query `get_prompt` with `id` and `tune` (the returned `tune_id`).
For template runs returning `prompt_ids`, use `list_prompts` with `order_id`
or `base_pack_id` to locate each prompt and its tune. Check `user_error` and
available assets; report pending work accurately without resubmitting.

If the host supports MCP events, it can subscribe to `prompt.completed` and
`prompt.failed` through the protocol's events capability. These are not tools
named `events_subscribe`. The host manages its callback and subscription
renewal. Deduplicate deliveries by event ID and retrieve the prompt after an
event; a failure event can represent an attempt that later retries. With no
events support, use spaced, bounded `get_prompt` checks and report pending
status when the turn cannot wait for completion.

## Embedded results and gallery

Hosts supporting MCP Apps render image and video results directly from
`generate_images`, `generate_video`, and `get_prompt`. Let the embedded view
show the media; include the returned prompt ID and status in the reply.
Use `open_astria` when the user asks to browse their generations. Its
`workspace` accepts `personal`, `all`, or a workspace ID. Viewing is read-only.
`get_prompt_view` is app-only; use `get_prompt` for model-side status checks.
On Claude, connect Astria from the plugin's Connectors tab; the remote
connection also works on mobile. CLI-only steps still need a terminal.

## Scope and discovery

Account closure and bulk deletion are unavailable through these tools. Decline
those requests without modifying data, and direct the user to Astria account
controls or [support@astria.ai](mailto:support@astria.ai) for account deletion.


Use `list_workspaces` and pass `workspace: "ID"` consistently for workspace
work. `workspace: "personal"` explicitly selects personal scope; omission is
personal for MCP (the CLI's saved default is not shared). `"all"` is for reads
only. List tools paginate with string `limit`/`offset`, newest IDs first.

Call `list_models` to discover current image/video names, tune IDs, supported
resolutions and defaults. Use the user's explicit model or the catalog default.
Do not copy model IDs or prices from old examples. Resolution is model-specific;
for video the `resolution` argument controls the image stage, while
`video_model` selects video resolution and capabilities.

## References (tunes)

Use `list_references` for title/class search and `get_reference` to inspect
training images. `gallery: true` selects public references; `branch: "partner-1"`
finds partner models outside the curated catalog. A tune is a reference.

Mention it as `<model_type:id:1> name`, with the returned class name immediately
after the token. `:1` is fixed syntax, never a strength/weight setting:
`<faceid:123:1> woman wearing <faceid:456:1> dress`.

Create references from real image URLs; the subject class is `name` and the
human/SKU label is `title`. Default `model_type` is `faceid`.

```json
{"tool":"create_reference","arguments":{"title":"Brown dress","name":"dress","image_url":["https://assets.example/front.jpg","https://assets.example/back.jpg"],"workspace":"17","idempotency_key":"reference-dress-unique-key"}}
```

## Images and editing

Use `generate_images` with English `text`, the desired `num_images` and
`aspect_ratio`. An `input_image` URL edits/upscales an existing image; optional
`mask_image` limits an edit. `film_grain` and `inpaint_faces` are separate
boolean attributes and preserve an explicit `false`.

```json
{"tool":"generate_images","arguments":{"text":"<faceid:123:1> woman wearing <faceid:456:1> dress, clean white studio background","num_images":"2","aspect_ratio":"3:4","workspace":"17","idempotency_key":"studio-look-unique-key"}}
```

`references: ["woman=https://…", "dress=https://…"]` creates new references
and prepends their proper tokens. Prefer existing tunes for recurring subjects.
If repeating identical text on different input images, use a distinct `seed`
per output; Astria also deduplicates prompts by `(text, seed)` within a tune.
Idempotency prevents duplicate submissions but does not change that prompt rule.

`pack_id` authors a template prompt inside an existing pack and requires a
fine-tuned reference token in the text. `base_pack_id` binds a one-off to that
pack's board frame without modifying its templates. Read **unique-headshot**
for reference-free faces: it requires Recraft 4.1 Pro and `inpaint_faces: false`.

## Video

Use `generate_video` with `video_model` and English `video_prompt`. Seedance
2 and 2.5 support existing tunes directly in `video_prompt`, using the same
`<faceid:TUNE_ID:1> CLASS_NAME` or `<lora:...>` syntax as image prompts. Astria
resolves the referenced tunes and supplies their images to the video model;
keep these mentions even when no separate tune-ID argument exists. Do not
claim tune tokens are image-only or that video mode only accepts image URLs.
Do not replace existing tunes with training-image URLs or attach those images
again through `image_references`.

Optional `text` renders a first frame; omit it for a text-only storyboard video.
Use the requested duration or the model default. The catalog reports media
capabilities, not duration options; do not claim it supplied a duration range.
Do not assume every model accepts the same media inputs.

```json
{"tool":"generate_video","arguments":{"video_model":"seedance2_fast_720p","video_prompt":"<faceid:123:1> woman walks down a runway as the camera tracks her","duration":"5","num_images":"1","aspect_ratio":"16:9","idempotency_key":"runway-video-unique-key"}}
```

For storyboard and short-film workflows, choose references by role:

- Products, packshots, people, garments and other ingredients use tune mentions
  in `video_prompt`. Resolve existing tunes; `references` creates new named
  ingredient tunes when needed.
- Multiple generated scene images use `image_references` as ordered HTTPS URLs
  to compose those scenes into the full short film. Preserve the intended scene
  order; do not create tunes for these scene images.

Both roles may coexist in one request. Omit `image_references` when no scene
images are supplied; ingredients are not sequential scene waypoints.
`first_frame`, `last_frame`, `input_video` and `audio_reference` take HTTPS URLs. Motion-control
models require `input_video`; `generate_audio` explicitly enables/disables audio.
Rendered video assets can be in `images[]` with `content_type=video/mp4`.

## Prompts and review comments

`list_prompts` filters recent work, templates (`pack_id`), generated template
work (`base_pack_id`/`order_id`), tune (`tune_id`), text and liked/video status.
`get_prompt` requires both `id` and `tune`. Use
`expand: ["prompt.comments"]` on either tool to include image review comments;
`"comments"` is an alias. Comments are a flat oldest-first array including
resolved entries. Associate images by `blob_id`/`attachment_id`; `resolved_at`
identifies resolved comments. Without expansion, comments are omitted.

```json
{"tool":"get_prompt","arguments":{"id":"555","tune":"123","workspace":"17","expand":["prompt.comments"]}}
```

## Templates (packs) and pricing

Templates and packs are the same objects. Use `list_templates` and
`get_template` (`slug` accepts a slug or numeric ID) before `run_template`.
For a multi pack pass one `tune_id` array entry per reference slot; at least
one is required. For a regular pack, alternatively provide `title`, `name`
and `image_url` to train a new reference. `prompt_ids` is a comma-separated
subset. `brief` and generation overrides apply to the output prompts.

```json
{"tool":"run_template","arguments":{"slug":"spring-lookbook","tune_id":["123","456"],"brief":"golden hour, Lisbon","num_images":"1","aspect_ratio":"3:4","workspace":"17","idempotency_key":"template-run-unique-key"}}
```

`cost_mc` is millicents: dollars = `cost_mc / 100000`. A prompt's cost already
includes its image count; never multiply it again. `template_prompts[].cost_mc`
is the stored baseline, while `costs.<class>.cost_mc` estimates a new reference
plus that class's prompt group, not necessarily the whole multi-class pack.
Discounts, workspace pricing, overrides and Cartesian variants change totals.
After a run, `order.total_cost_mc`, when returned, is the authoritative charge.

Template creation/updates, workspace creation, landing HTML, board duplication,
local downloads/uploads, video inspection/Variate and agent-session handoff are
currently CLI-only. Read [references/cli.md](references/cli.md) for those tasks;
use MCP for the supported parts of a mixed workflow.
