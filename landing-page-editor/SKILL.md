---
name: landing-page-editor
description: Use when editing, updating, or iterating on a workspace's landing page HTML (the magazine-style /w/:slug page). Supports incremental edits — fetch the current HTML, make targeted changes, then write it back. NOT for initial generation — that comes from the `brief` field which runs the server-side LANDING_PAGE_PROMPT against Gemini.
allowed-tools: Bash(astria:*), Read, Write, Edit
---

# Workspace Landing Page Editor

The workspace landing page (rendered at `/w/:slug`) is a single self-contained
HTML blob stored on `workspace.landing_page_html`. It is generated from scratch
by the server-side `LANDING_PAGE_PROMPT` whenever a `brief` is submitted — that
path overwrites the HTML wholesale.

For ANY change that should not regenerate the whole page (typography tweaks,
layout edits, adding a section, changing copy, swapping an image, fixing a
tagline), edit the HTML directly and write it back. Do NOT send a `brief`
unless the user wants a full regeneration.

Use `get_workspace` with the destination workspace `id` to read the current HTML
and `update_workspace` with that same `id` and `landing_page_html` to save edits.
For embedded agents, omit the optional `workspace` scope to inherit the current
chat scope unless the user explicitly requested another destination.
Use `brief` only for an explicitly requested full regeneration.

## Constraints carried over from `LANDING_PAGE_PROMPT`

When editing, preserve these invariants (the live `/w/:slug` page depends on them):

- The output is **inner body HTML** — no `<html>`, `<head>`, `<body>`, or `<!DOCTYPE>` tags
- Styling uses **Tailwind utility classes** (already loaded on the page). Use `<style>` only for hover/animation effects Tailwind can't express
- Pack links are exactly `/p/{slug}`; model/reference links use the `link` field from the tunes JSON verbatim (do NOT re-encode `%5B`/`%5D`)
- Every image / video is wrapped in an `<a>` tag
- Image and video URLs must be ones that already exist — do not invent URLs
- Never use data URIs or embedded image data in HTML or CSS (including base64 images and inline SVG images). Use hosted HTTPS image URLs from Astria workspace attachments instead.
- Videos use `<video autoplay muted loop playsinline poster="POSTER_URL"><source src="VIDEO_URL" type="video/mp4"></video>`
- The string `__TUNES_JSON_PAYLOAD__` inside `<script type="application/json" id="tunes-data">…</script>` is a server-side placeholder. The server substitutes it at render time with the live tunes JSON. **Never replace it with literal JSON** — that freezes the cast and newly added tunes won't appear
- Editorial styling: serif headlines, generous whitespace, hairline rules, `object-cover object-[center_top]` on portrait images, `max-h-[70vh]` on hero spreads, `aspect-[4/5]` or `aspect-[3/4]` on portrait containers

## Workflow

### 1. Fetch the current landing page HTML

Call `get_workspace` and retain `landing_page_html` unchanged as the starting point.
Preview the rendered page at `/w/{slug}`.

### 2. Read data needed for the edit

Use `list_templates`, `list_references`, and `list_prompts` with their declared
schemas. Read only the requested workspace. Use limit/offset pagination as needed.

### 3. Upload and attach images with Astria

Before inserting a supplied image into the page, call `attach_workspace_images`
with `id` set to the destination workspace ID, `image_urls` containing the supplied
HTTPS URLs, and a fresh `idempotency_key`. This includes Astria direct-upload URLs:
putting a URL in HTML does not attach its blob, and unattached uploads can be purged.
For local files, use Astria's `create_upload` tool to prepare the upload, execute
its returned upload command, and verify it succeeds before passing the returned
`blob_signed_id` to `attach_workspace_images` in its `signed_ids` array.
`create_upload` only prepares an upload slot; it does not upload or attach the
image itself. Never attach a pending upload or embed image bytes in the page.

The tool reuses Astria blobs and imports external images into workspace storage.
Use the returned `images[].url` values in the HTML. If attachment fails, resolve
the error before saving HTML that uses those images. Images already listed in
`get_workspace.images` need no attachment call. Do not create a reference or a
generation merely to retain a landing-page image.

### 4. Make the incremental edit

Preserve unrelated HTML and the constraints above. Save a working text file
only if helpful; do not substitute a filename for the HTML tool argument.

### 5. Save and verify

Call `update_workspace` with the complete `landing_page_html` and a fresh
idempotency_key. Do not pass `brief`. Read it back with `get_workspace` and
verify the saved change, confirm the new images appear in `images`, and check the
rendered page when browser access is available.

## Regenerating from scratch

Only when the user explicitly asks for a full redesign — submit a `brief` and
the server runs `LANDING_PAGE_PROMPT` against Gemini, overwriting the HTML:

Call `update_workspace` with the requested `brief` and a fresh idempotency_key.
Attach supplied images using step 3 before submitting the brief, so the generator
receives them as workspace assets.
Read the resulting HTML with `get_workspace` and verify the result.
