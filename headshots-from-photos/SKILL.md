---
name: headshots-from-photos
description: Create professional headshots of the actual person in supplied photos or a saved identity reference. Use for "make professional headshots from my photos", LinkedIn portraits, corporate team headshots, or consistent portraits of the same person across backgrounds. Inventing a new face uses unique-headshot. Respect a named provider; portrait advice and prompt-only requests do not authorize generation.
---

# Headshots from photos

Produce the requested professional portraits of the supplied person with Astria.
Preserve identity and natural features while changing the requested wardrobe,
background, lighting, or framing. Do not replace them with an invented face.

Use **astria-api** for schemas, reference syntax, HTTPS inputs, workspace scope,
model discovery, idempotency, and checking completed results.

## Establish the identity reference

Use an explicit saved reference; resolve a named identity with `list_references`
and inspect it using `get_reference`. Otherwise create one identity reference
with `create_reference` from the supplied usable HTTPS photo URLs, using a
subject class appropriate to the supplied brief. Use the returned ID and class
name on every portrait. Do not create a new reference for each background.

For an attachment or local file, use a real host upload capability or the
optional authenticated CLI. If neither can supply accessible URLs, ask for
usable media instead of inventing a URL. If no identity input exists, ask for
photos or a saved reference rather than generating a stranger.

For a team, keep each person's photos and reference ID separate; a group of
faces is not one identity. Preserve the requested headcount and shot count.

## Generate the portraits

Use a requested saved template through `get_template` / `run_template`, resolving
its actual reference slots before submission. Otherwise call `list_models` and
use the selected model or catalog default with `generate_images`.

Include the returned identity token and class in the text, then describe the
requested professional style. For an unspecified style, choose simple studio
lighting, a neutral background, natural expression, and professional clothing.
Make one image unless the user asks for a set. Use separate prompts for distinct
backgrounds or outfits, reusing the identity reference throughout.

Do not borrow **unique-headshot**'s invented age, heritage, facial traits, or
casting prompt. Do not infer protected attributes from the identity photos.

## Deliver

Retain returned prompt/tune IDs and check `get_prompt` for each requested output.
Present completed images and report pending or failed portraits accurately.
When inspection is available, check resemblance, natural facial proportions,
and framing. Report an identity mismatch without claiming an exact likeness
or automatically spending credits on additional attempts.
