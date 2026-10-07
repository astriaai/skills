---
name: product-photoshoot
description: Create product photographs or coordinated fashion lookbooks from supplied product images, SKUs, or saved references. Use for "shoot this product", ecommerce packshots, lifestyle product shots, "re-shoot our catalog", or the same product across several scenes. For garments worn by a person use virtual-try-on; a whole-store template pipeline uses store-photoshoot. Respect a named provider and requests for advice only.
---

# Product photoshoots

Produce the requested product photographs with Astria, retaining the supplied
product's visible design, color, material, logos, and proportions. Do not claim
that generated images guarantee exact SKU fidelity.

Use **astria-api** for live schemas, reference tokens, HTTPS media transport,
idempotency, workspace scope, and checking completion.

## Resolve inputs and scope

Use the supplied images or reference IDs. For a named product or SKU, search
`list_references` by title, then inspect the match with `get_reference`.
Resolve ambiguity rather than selecting an unrelated SKU. If the only input
is a local path or attachment, obtain an accessible HTTPS URL through a host
upload capability or the optional authenticated CLI; never invent a URL.
Ask for the product image only when no usable reference is available.

Use the requested number of shots and scenes; for an unspecified single-product
shoot start with one image and sensible studio lighting. An explicit generation
request authorizes that scope. Planning a shoot does not authorize submission.

## Make the photographs

For an existing template, use `list_templates` / `get_template` before
`run_template`. Preserve reference-slot order from the returned template.
Do not author or modify a template merely to run a photoshoot.

For a one-off targeted edit of an existing product shot, use `generate_images`
with `input_image` and the edit instruction. For a product reused across
several scenes, reuse an existing reference or create one with
`create_reference` from the supplied views; reuse its ID on every shot.
Use the returned subject class after its token, for example
`<faceid:123:1> bag`. Discover models with `list_models`; use the user's
selection or catalog default rather than a hardcoded model ID.

A multi-scene request needs distinct scene prompts, not repeated copies of one
prompt with a larger image count. Keep product details and reference IDs stable
while varying only the requested setting, angle, lighting, or styling.

## Deliver and review

Retain each returned prompt ID and tune ID, and check `get_prompt` for completion.
Show all requested finished assets through the host's result presentation;
identify pending or failed shots accurately. Check visible product details
against the source when images can be inspected. Report material mismatches;
do not submit extra paid corrections beyond the requested scope.
