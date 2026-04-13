---
description: Use when making API calls to Astria for tunes, prompts, packs, or image generation (Gemini/Seedream)
---

# Astria API Reference

API credentials are available as environment variables:
- $ASTRIA_AUTH_TOKEN — Bearer token
- $ASTRIA_BASE_URL — API base URL
- $WORKSPACE_ID — Default workspace ID (if set)
- $GEMINI_TUNE_ID — Gemini tune ID
- $SEEDREAM_TUNE_ID — Seedream tune ID

Use these directly in curl commands.
- Always include `Authorization`
- Workspace header rules:
  - Use `-H "X-Workspace-Id: $WORKSPACE_ID"` for the default workspace
  - Use `-H "X-Workspace-Id: <workspace_id>"` to target a different workspace
  - Use `-H "X-Workspace-Id: all"` for cross-workspace queries
  - Omit `X-Workspace-Id` only when intentionally using personal/default scope without workspace context
For better tool-call readability in chat logs, always include an explicit method with `-X` (for example, `-X GET`, `-X POST`) in Astria curl commands.

---

## Users

### Get current user
GET $ASTRIA_BASE_URL/users

Example:
curl -s -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" -H "X-Workspace-Id: $WORKSPACE_ID" "$ASTRIA_BASE_URL/users" | jq '{ usd_balance_mc, auto_extend_tunes, top_off_amount, purchased_plugin_at }'

---

## Tunes (Fine-tuned models)

### List tunes
GET $ASTRIA_BASE_URL/tunes

Example:
curl -s -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" -H "X-Workspace-Id: $WORKSPACE_ID" "$ASTRIA_BASE_URL/tunes" | jq '.[].id, .[].title, .[].name', .[].orig_images'

### List public gallery tunes
GET $ASTRIA_BASE_URL/gallery/tunes?model_type=faceid&limit=200

### Get tune
GET $ASTRIA_BASE_URL/tunes/:id

Example:
curl -s -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" -H "X-Workspace-Id: $WORKSPACE_ID" "$ASTRIA_BASE_URL/tunes/123" | jq '.[].id, .[].title, .[].name', .[].orig_images'

### Create tune / reference
POST $ASTRIA_BASE_URL/tunes
Content-Type: multipart/form-data

Parameters:
- tune[title] (required) - Display name
- tune[images][] - Images - multipart file upload
- tune[image_urls][] - Training images as URLs (alternative to file upload)
- tune[name] - Subject class name (e.g., man, woman, dog, style, shirt, pants, shoes, sandals, etc...)
- tune[base_tune_id] - $GEMINI_TUNE_ID
- tune[model_type] - "faceid"

Example - create tune with image URLs:
curl -s -X POST "$ASTRIA_BASE_URL/tunes" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -F "tune[title]=Brown dress" \
  -F "tune[base_tune_id]=$GEMINI_TUNE_ID" \
  -F "tune[name]=dress" \
  -F "tune[characteristics]={\"short_description\":\"satin brown dress\"}" \
  -F "tune[image_urls][]=https://example.com/photo1.jpg" \
  -F "tune[image_urls][]=https://example.com/photo2.jpg" | jq '.[].id, .[].title, .[].name', .[].orig_images'

### Update tune
PATCH $ASTRIA_BASE_URL/tunes/:id
Parameters: tune[title], tune[name], tune[auto_extend], tune[characteristics]


---

## Prompts (Image generation)

### Create prompt (generate images)
POST $ASTRIA_BASE_URL/tunes/:tune_id/prompts

1. When creating a prompt - make sure the user is in the /prompts page, or navigate there by using [ASTRIA_NAV:/prompts]. 
2. Use the prompt-writing skill. 
2. No need to check prompt status as images will appear automatically in the UI when ready.
3. Before creating the prompt, display the prompt using [ASTRIA_PROMPT:...] - this will allow the user to edit the prompt in the prompt box. Use @ask-question-tool to offer to create the prompt for him with different reasonable parameters of num_images, aspect_ratio, and resolution (for Gemini) with multiple questions. Do not ask these questions unless we have already established the user preferences.

Parameters:
- prompt[text] (required) - Prompt text. Use <1> as subject token for fine-tuned models.
- prompt[num_images] - Number of images (1-8)
- prompt[aspect_ratio] - Aspect ratio string: "1:1","16:9,"9:16,"21:9,"9:21,"3:2","2:3","5:4","4:5","4:3"
- prompt[resolution] - "1K", "2K" (default), "4K" - only for @GEMINI_TUNE_ID

Example:
curl -s -X POST "$ASTRIA_BASE_URL/tunes/@GEMINI_TUNE_ID/prompts" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -F "prompt[text]=180cm extremely thin and tall model <faceid:4076525:1.0> woman \n Sleek, low, slicked-back bun hairdo\n <faceid:4035726:1.0> earrings \n <faceid:4076806:1.0> outfit woman pants longer til the end of t\n <faceid:4043875:1.0> shoes \n front <faceid:4042961:1.0> pose \n look book plain white background #fff" \
  -F "prompt[resolution]=2K" \
  -F "prompt[aspect_ratio]=3:4" \
  -F "prompt[num_images]=4" | jq '.[].id, .[].text, .[].num_images, .[].images[], .[].aspect_ratio, .[].resolution'

### List prompts
GET $ASTRIA_BASE_URL/prompts
Filters: text, base_pack_id, pack_id, user_id

Example:
curl -s -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" -H "X-Workspace-Id: $WORKSPACE_ID" "$ASTRIA_BASE_URL/prompts?pack_id=123" | jq '.[].id, .[].text, .[].num_images, .[].images[], .[].aspect_ratio, .[].resolution'

### List prompts for a reference/tune
Can be used to find prompts tied to a specific reference just as a woman or clothing and get a sense of what the user has already generated with that reference.
GET $ASTRIA_BASE_URL/tunes/:tune_id/prompts

### Update prompt
PATCH $ASTRIA_BASE_URL/tunes/:tune_id/prompts/:id

Use this to assign a pack to a prompt, or switch workspace

Parameters:
- prompt[pack_id]
- prompt[workspace_id]


---

### Seedream 4.5
POST $ASTRIA_BASE_URL/tunes/$SEEDREAM_TUNE_ID/prompts

Parameters:
- prompt[text] (required) - Describe the image. Do NOT use <1> token.
- prompt[num_images] - 1 to 4

Example:
curl -s -X POST "$ASTRIA_BASE_URL/tunes/$SEEDREAM_TUNE_ID/prompts" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" \
  -F "prompt[text]=professional product photo of wireless headphones on marble surface" \
  -F "prompt[num_images]=2" | jq '.[].id, .[].text, .[].num_images, .[].images[]'

---

## Workspaces

### List workspaces
GET $ASTRIA_BASE_URL/workspaces.json

Example:
curl -s -X GET "$ASTRIA_BASE_URL/workspaces.json" \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" | jq '.[].id, .[].title, .[].slug'

---

## Packs (Prompt template collections)

### List packs
GET $ASTRIA_BASE_URL/packs

Example:
curl -s $ASTRIA_BASE_URL/packs \
  -H "Authorization: Bearer $ASTRIA_AUTH_TOKEN" \
  -H "X-Workspace-Id: $WORKSPACE_ID" | jq '.[].id, .[].title, .[].slug', .[].main_class_name'

### Create pack
POST $ASTRIA_BASE_URL/packs
Content-Type: application/json

To assign prompts to a pack - make a PATCH /prompts/:id request with the pack_id field set to the pack ID.

Parameters:
- pack[title] 
- pack[base_tune_id]=$GEMINI_TUNE_ID
- pack[model_type]=faceid
---

## Error Handling
- 422: Validation error (missing required fields, invalid params) - always present the error message from the "error" field in the JSON response to the user
