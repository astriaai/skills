---
description: Use when editing, updating, or iterating on a workspace's landing page HTML (the magazine-style /w/:slug page). Supports incremental edits — fetch the current HTML, make targeted changes, then PATCH it back. Also covers pulling all packs/prompts/tunes from the workspace so edits can reference real data. NOT for initial generation — that comes from the `brief` field which runs the server-side `LANDING_PAGE_PROMPT` against Gemini.
---

# Workspace Landing Page Editor

The workspace landing page (rendered at `/w/:slug`) is a single self-contained HTML blob stored on `workspace.landing_page_html`. It is generated from scratch by the server-side `LANDING_PAGE_PROMPT` (see `app/models/concerns/gemini_api.rb`) whenever `workspace[brief]` is submitted — that path overwrites the HTML wholesale.

For ANY change that should not regenerate the whole page (typography tweaks, layout edits, adding a section, changing copy, swapping an image, fixing a tagline), edit the HTML directly and PATCH it back. Do NOT send `brief` unless the user wants a full regeneration.

## Constraints carried over from `LANDING_PAGE_PROMPT`

When editing, preserve these invariants (the live `/w/:slug` page depends on them):

- The output is **inner body HTML** — no `<html>`, `<head>`, `<body>`, or `<!DOCTYPE>` tags
- Styling uses **Tailwind utility classes** (already loaded on the page). Use `<style>` only for hover/animation effects Tailwind can't express
- Pack links are exactly `/p/{slug}`; model/reference links use the `link` field from the tunes JSON verbatim (do NOT re-encode `%5B`/`%5D`)
- Every image / video is wrapped in an `<a>` tag
- Image and video URLs must be ones that already exist — do not invent URLs
- Videos use `<video autoplay muted loop playsinline poster="POSTER_URL"><source src="VIDEO_URL" type="video/mp4"></video>`
- The string `__TUNES_JSON_PAYLOAD__` inside `<script type="application/json" id="tunes-data">…</script>` is a server-side placeholder. Server substitutes it at render time with the live tunes JSON. **Never replace it with literal JSON** — that freezes the cast and newly added tunes won't appear
- Editorial styling: serif headlines, generous whitespace, hairline rules, `object-cover object-[center_top]` on portrait images, `max-h-[70vh]` on hero spreads, `aspect-[4/5]` or `aspect-[3/4]` on portrait containers

## Workflow

### 1. Fetch the current landing page HTML

```
curl -s -X GET "$ASTRIA_BASE_URL/workspaces/$WORKSPACE_ID.json" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  | jq -r '.landing_page_html' > /tmp/landing_page.html
```

The JSON also exposes `title`, `slug`, `brief`, `url`, `public_at`, `unlisted_at`. To preview the rendered page (with the tunes placeholder substituted), open `$ASTRIA_BASE_URL/w/{slug}` in a browser.

### 2. Pull all workspace data (when an edit needs to reference real packs / prompts / tunes)

Each list endpoint paginates via `limit`/`offset` (default sort id desc). Loop until you've collected everything.

**All packs in the workspace:**
```
curl -s -X GET "$ASTRIA_BASE_URL/packs?limit=100" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  | jq '[.[] | {id, title, slug, subtitle, url, main_class_name, public_at}]'
```

**All public tunes (the "cast" rendered on the page):**
```
curl -s -X GET "$ASTRIA_BASE_URL/tunes?limit=200" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  | jq '[.[] | {id, title, name, public_at, orig_images}]'
```

**All prompts in the workspace** (page through with `offset` until empty):
```
curl -s -X GET "$ASTRIA_BASE_URL/prompts?limit=100&offset=0" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  | jq '[.[] | {id, text, pack_id, tune_id, num_images, is_video, aspect_ratio, images, video}]'
```

**Prompts for a specific pack** (cheaper when only one section is being edited):
```
curl -s -X GET "$ASTRIA_BASE_URL/prompts?pack_id=<pack_id>&limit=100" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID"
```

### 3. Make the incremental edit

Edit `/tmp/landing_page.html` locally. Keep changes surgical — the prompt produced thousands of bytes of layout and most of it should stay verbatim. Re-read the constraints section above before saving.

### 4. PATCH the workspace

Send the modified HTML back. **Do NOT include `brief`** unless you want the server to discard your edits and regenerate from scratch via Gemini.

```
curl -s -X PATCH "$ASTRIA_BASE_URL/workspaces/$WORKSPACE_ID.json" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  --data-binary @<(jq -n --rawfile html /tmp/landing_page.html '{workspace: {landing_page_html: $html}}') \
  | jq '{id, slug}'
```

Or pass the HTML inline (escape carefully — multipart form is easier for large bodies):
```
curl -s -X PATCH "$ASTRIA_BASE_URL/workspaces/$WORKSPACE_ID.json" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -F "workspace[landing_page_html]=<-" < /tmp/landing_page.html
```

### 5. Verify

Navigate to `/w/{slug}` (use [ASTRIA_NAV:/w/{slug}]) and visually confirm the change. The `__TUNES_JSON_PAYLOAD__` placeholder is replaced server-side at render time — if a JSON-shaped string still shows on the rendered page, the placeholder was accidentally deleted or renamed.

## Regenerating from scratch

Only when the user explicitly asks for a full redesign — submit `workspace[brief]` and the server will run `LANDING_PAGE_PROMPT` against Gemini and overwrite `landing_page_html`:

```
curl -s -X PATCH "$ASTRIA_BASE_URL/workspaces/$WORKSPACE_ID.json" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -F "workspace[brief]=Editorial fashion lookbook, AW26, dark moody palette, emphasize the womenswear packs"
```
