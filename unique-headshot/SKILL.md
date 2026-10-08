---
name: unique-headshot
description: Generate new, unique AI headshot/model faces from text, including a similar vibe inspired by an attached person photo. Describe visible traits; never use the photo or a reference tune in generation. Portraits preserving the actual person use headshots-from-photos.
---

# Unique Headshot Generator

Generate realistic, unique face headshots for AI model creation. The prompt alone defines a new person through detailed physical trait descriptions.

## Attached photos are inspiration only

**NEVER send a reference image to generation in this skill**, even when the user attaches a person photo or the composer already contains a reference. Do not create or reuse a subject tune, add `<faceid:...>` / `<lora:...>` tokens, edit the attached image, or pass its URL/path as any generation media input. This includes `references`, `input_image`, `mask_image`, raw image references, and their UI/CLI equivalents.

When a person photo is attached:
1. View it and describe the visible characteristics that make the headshot distinctive: skin tone and texture, eye shape and color, eyebrows, nose, lips, face shape, cheekbones, jaw, hair color and texture, expression, and overall casting vibe. Describe only what you can see; do not infer ethnicity or heritage from appearance.
2. Give a brief trait description and turn it into a self-contained English headshot prompt for a **new person with a similar vibe**. Carry the distinctive visual traits into words rather than writing "the attached person" or "use this reference". Apply the headshot framing, pulled-back hair, background, and lighting below.
3. Generate from that text alone. The attachment is for visual analysis only; never upload it, train it, or bind it to the generation. Do not use reference-removing inspection such as `astria inspect --name woman`, which would erase the facial characteristics you need to describe.

Without an attachment, invent the traits from the user's brief. If the user wants portraits of the actual person with their identity preserved, use **headshots-from-photos** instead; do not turn unique-headshot into a reference-based workflow.

## Prompt Template

```
Close-up studio headshot of a [age]-year-old [optional user-specified ethnicity/heritage] [gender] with [skin_tone] skin, [skin_details], [eye_description], [nose_description], [face_structure], [unique_feature], [hair_description]. Bare shoulders, no clothing visible, no jewelry. [expression], looking at the camera. Clean white background #fff, [lighting], fine natural skin texture and an even, unmarked complexion, beauty headshot
```

## Slot Definitions

### Age
- Range: 18–35 for young models, 35–55 for mature
- Always specify exact age (e.g., "22-year-old")

### Ethnicity / Heritage
Heritage is an optional casting choice, not something to infer from a photo.
- Include it when the user specifies it. For photo-inspired faces, describe visible skin tone, hair, and facial geometry instead of guessing heritage.
- Never infer heritage from a brand's country, language, store name, or currency.
- For an unconstrained invented batch, vary casting backgrounds and visible traits across regions rather than applying a house default. For a photo-inspired batch, keep the requested vibe while varying facial geometry and expression.
- Single origin: "Nigerian", "Korean", "Irish", "Mexican", "Filipina", "Norwegian",
  "Egyptian", "Peruvian", "Punjabi", "Vietnamese"
- Hyphenated heritage: "Brazilian-Japanese", "Ghanaian-British", "Lebanese-Italian",
  "Maori-Polynesian", "Colombian-Korean", "Turkish-German", "Somali-Swedish"
- Regional descent: "of Eastern European descent", "of West African descent",
  "of Andean descent", "of Han Chinese descent"

### Skin
Pair a **tone** with subtle **texture/detail**. Default to an even complexion with fine natural pore texture; distinctive skin markings are optional and only included when requested:
- **Tones**: porcelain, fair, light olive, olive-tan, warm golden-tan, cinnamon-brown, warm caramel, olive-bronze, coppery-bronze, warm umber, deep dark, dark mahogany, ebony
- **Undertones**: pink flush, cool blue-black undertone, warm golden undertone, cool undertone
- **Default details** (pick 1): fine natural pore texture, subtle natural sheen, soft peach fuzz on jawline
- **Optional markings** (only when requested): freckles, beauty marks, moles, scars, hyperpigmentation

### Eyes
Combine **shape**, **color**, and **distinguishing trait**:
- **Shapes**: almond-shaped, deep-set, round, wide-set, monolid, hooded, large expressive, doe eyes, heavy-lidded
- **Colors**: steel-blue, hazel, green-hazel, dark brown, dark walnut, amber, blue-grey, rose-tinted
- **Traits**: slight upward tilt at outer corners, thick lashes, heavily-lashed, barely-there pale lashes, set close together, spaced wide apart

### Nose
- narrow straight nose, petite button nose with flared nostrils, prominent Roman nose with defined bridge bump, aquiline nose, aquiline hooked nose, broad flat nose, long narrow nose turning slightly downward at tip, small upturned nose, strong nose, narrow bridge nose

### Face Structure
Combine **shape** with **defining bone structure**:
- **Shapes**: angular, heart-shaped tapering to pointed chin, round, narrow, oval, elongated
- **Bones**: sharp cheekbones casting slight shadows, high rounded forehead, strong square jaw, sharp defined jawline wider than forehead, prominent cheekbones, soft jawline, strong angular jawline, delicate pointed chin, small rounded chin

### Unique Features (pick 1-2 for distinctiveness)
These are critical for making each face unique:
- pronounced dimple on left cheek only
- one eyebrow set slightly higher than the other
- thick arched eyebrows that nearly meet
- asymmetric face with one slightly higher cheekbone
- slightly asymmetric smile
- a pronounced cupid's bow
- thin elegant neck / long neck / impossibly high forehead / elongated swan neck
- visible peach fuzz on jawline

### Hair
Always pulled back to keep face clear. Vary the style:
- sandy-blonde fine hair brushed back flat behind ears into a low knot
- black hair smoothed back into a neat low chignon
- dark curly hair tamed back into a tight bun
- dark espresso hair slicked back into a sleek low ponytail
- jet-black coarse hair pulled tightly into a high sculptural bun
- auburn red hair slicked back into a neat low chignon
- ash blonde hair brushed back behind ears
- straight black hair pulled back into a sleek tight ponytail
- glossy black hair swept back into a sleek twisted bun at the nape
- dark brown hair in a clean slicked-back low chignon
- dark hair slicked back into a tight oiled ballerina bun
- hair braided flat against scalp into a sleek gathered bun at nape
- hair in a severe slicked-back low knot

### Expression
- Poised neutral expression
- Gentle closed-mouth smile
- Calm direct gaze
- Natural relaxed expression
- Direct confident gaze
- Slight closed-mouth smile
- Composed knowing expression
- Soft parted lips, steady gaze
- Relaxed self-assured expression
- Quiet intensity, lips slightly pressed
- Unblinking confrontational stare
- Defiant half-squint

### Lighting
Vary lighting for natural diversity:
- soft ring light
- soft butterfly lighting
- soft diffused studio lighting
- soft even studio lighting
- flat diffused studio lighting
- even soft studio lighting

## Generation Rules

1. **Text-only generation, always**. No subject reference tunes or tokens, image editing, or generation media inputs. Remove inherited subject tokens, image-input CLI flags, media fields, and replacement lineage from a composer draft: this is a new face, not an edit of the source person. An existing attachment never changes this rule.
2. **Use Recraft 4.1 Pro**. Resolve its current name/title and tune ID with `list_models` through the connected MCP server (see **astria-api**), or `astria models` in the CLI-only embedded sandbox. The catalog may call it `recraft-4-1` / `Recraft V4.1`. Never hard-code or infer a numeric tune ID or silently use the composer default. For an embedded draft, also check that the resolved ID is available in the current image model contract; catalog availability alone does not prove composer support. If unavailable, report the limitation instead of substituting another model.
3. **Validate embedded drafts before presenting or generating**. When `validate_generation` is available, call it with the exact complete `schema_version: 2`, `prompts` collection intended for `present_generation`. Use the resolved integer `tune_id`, English `text`, integer `num_images: 2` unless another count was requested, `aspect_ratio: "1:1"`, `resolution: null`, `image_reference_urls: []`, and null for every image input, mask, video, and source-media field. Leave replacement lineage null. Do not copy a resolution or image input from the current composer. Fix all reported errors using `allowed_values` and repair instructions, then validate the revised collection before proceeding. Never repair a unique-headshot by attaching images, creating reference tunes, or adding subject tokens. `valid: null` is not a pass: obtain the current composer/model contract; if settings remain unavailable, report that limitation. Present only the validated collection, without subsequent changes. The validator checks draft settings; it does not guarantee file availability, permissions, or successful submission.
4. **Never use face inpainting**, including retries and repairs. Clear inherited face-inpainting settings and `--inpaint_faces` / `--inpaint_preset` prompt directives. Fix facial defects by revising the text prompt and regenerating with face inpainting disabled. For MCP `generate_images`, send the discovered model ID, English `text`, `num_images: "2"` unless another count was requested, `aspect_ratio: "1:1"`, `inpaint_faces: false`, and a fresh `idempotency_key`. Omit `resolution` and every reference/media argument. In a CLI-only sandbox use `astria generate --model <resolved-model> --text "<headshot prompt>" --num-images 2 --aspect-ratio 1:1 --no-inpaint-faces`, with no image/reference flags. Embedded tools share a draft schema, not the MCP generation schema: include `inpaint_faces: false` only if their live schema exposes it; never invent unsupported arguments. Otherwise use Recraft's disabled face-inpainting default for the card, and explicitly disable it on direct submission. An embedded validation failure must be repaired before direct CLI generation; do not bypass it by submitting through another route.
5. **Every prompt must have at least one unique distinguishing feature** in facial geometry or expression (dimple, brow shape, asymmetric smile, cupid's bow, etc.). Do not use a skin mark to satisfy this rule. Unless the user requests one, omit moles, beauty marks, freckles, and other localized pigmentation from the prompt. Describe natural texture with pores or sheen without implying pigmented spots. If a skin marking is explicitly requested, adapt the default suffix to accommodate it.
6. **Hair is always pulled back** — no hair framing or covering the face
7. **Default suffix**: `Bare shoulders, no clothing visible, no jewelry. [expression], looking at the camera. Clean white background #fff, [lighting], fine natural skin texture and an even, unmarked complexion, beauty headshot`
8. **No photographer references or magazine names** in the prompt — keep it clean and generic

Example MCP arguments after resolving the actual Recraft model ID (replace
the example ID and key; do not copy them into a live request):

```json
{"tool":"generate_images","arguments":{"model":"123","text":"Close-up studio headshot of a 25-year-old Irish woman with an asymmetric smile, hair pulled back, bare shoulders, clean white background, beauty headshot","num_images":"2","aspect_ratio":"1:1","inpaint_faces":false,"idempotency_key":"headshot-unique-key"}}
```

## Batch Generation

When generating multiple unique headshots, maximize diversity:
- For unconstrained casting, vary heritage, skin tone, eye color, face shape, and unique features across the batch
- For attached-photo inspiration, preserve the described vibe and vary facial geometry or expression; do not override the brief merely to diversify heritage
- Mix age range (don't make them all the same age)
- Vary expressions and lighting setups
- Each face should be immediately distinguishable from the others

## Example Prompts

**Prompt 1:**
Close-up studio headshot of a 25-year-old Irish woman with cool-toned fair skin and fine natural pore texture, deep-set hazel eyes, strong square jaw and a pronounced cupid's bow, auburn red hair slicked back into a neat low chignon. Bare shoulders, no clothing visible, no jewelry. Composed knowing expression, looking at the camera. Clean white background #fff, soft diffused studio lighting, fine natural skin texture and an even, unmarked complexion, beauty headshot

**Prompt 2:**
Close-up studio headshot of a 22-year-old Ethiopian woman with warm umber skin, large expressive round eyes, narrow bridge nose, defined cupid's bow, long neck, dark hair pulled into a smooth high ballerina bun. Bare shoulders, no clothing visible, no jewelry. Soft parted lips, steady gaze, looking at the camera. Clean white background #fff, even soft studio lighting, fine natural skin texture and an even, unmarked complexion, beauty headshot

**Prompt 3:**
Close-up studio headshot of a 27-year-old Mexican woman of Zapotec descent with warm caramel skin and fine natural pore texture, wide-set dark brown almond eyes with thick lashes, a strong straight nose, an oval face with high rounded cheekbones and a small rounded chin, a pronounced dimple on the left cheek only, glossy black hair swept back into a sleek twisted bun at the nape. Bare shoulders, no clothing visible, no jewelry. Poised neutral expression, looking at the camera. Clean white background #fff, soft ring light, fine natural skin texture and an even, unmarked complexion, beauty headshot

**Prompt 4:**
Close-up studio headshot of a 24-year-old Korean woman with pale milky skin and subtle natural sheen, small monolid eyes, round face, soft jawline and naturally arched eyebrows, straight black hair pulled back into a sleek tight ponytail. Bare shoulders, no clothing visible, no jewelry. Slight closed-mouth smile, looking at the camera. Clean white background #fff, flat diffused studio lighting, fine natural skin texture and an even, unmarked complexion, beauty headshot

**Prompt 5:**
Close-up studio headshot of a 31-year-old Norwegian man with cool-toned fair skin and light stubble, hooded blue-grey eyes with pale lashes, a prominent Roman nose with a defined bridge bump, an angular face with a strong square jaw, one eyebrow set slightly higher than the other, ash-blonde hair brushed back flat. Bare shoulders, no clothing visible, no jewelry. Calm direct gaze, looking at the camera. Clean white background #fff, soft butterfly lighting, fine natural skin texture and an even, unmarked complexion, beauty headshot
