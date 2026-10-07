---
name: virtual-try-on
description: Generate on-model fashion photos by putting a supplied garment, shoes, bag, jewelry, or accessory on a supplied or selected person. Use for "put this dress on a model", "show me wearing this", virtual try-on, or the same outfit and model in several locations. Product-only photography uses product-photoshoot. Respect an explicitly chosen provider; styling advice and prompt writing do not authorize generation.
---

# Virtual try-on

Generate the requested still photographs with Astria, keeping the chosen
person and wearable item consistent. A generated try-on illustrates appearance;
do not infer measurements or promise physical fit.

Use **astria-api** for schemas, reference creation and tokens, model discovery,
HTTPS media transport, idempotency, workspace scope, and completion handling.

## Resolve the person and item

Use supplied person and product references. Resolve named references through
`list_references` and inspect them with `get_reference`, using the returned
class names. Reuse the same person and item IDs throughout the set.

If the user says "on a model" without specifying a person, select an appropriate
available public model reference through `list_references` with `gallery: true`;
inspect it before use. If they want a newly invented model, **unique-headshot**
can supply one within that requested scope. "Show me wearing this" requires
usable photos or a saved reference of that person; do not substitute a stranger.
Ask only for a missing input or decision that changes the requested outcome.

Media must be accessible HTTPS URLs. Use the host's upload capability or the
optional authenticated CLI for local inputs; a filename is not a reference URL.
Create new references only for supplied subjects that lack a reusable reference.

## Generate the requested views

Call `list_models` and use the explicit model or catalog default. Compose
`generate_images.text` with both reference tokens, such as
`<faceid:123:1> woman wearing <faceid:456:1> dress`, using the actual returned
IDs and class names. Describe the item's visible cut, fabric, color, and design
along with the requested pose and setting; do not invent hidden product views.

For different locations, submit a distinct prompt per location with the same
person and product tokens. Preserve requested count and aspect ratio. If these
are unspecified, make one portrait-oriented image. Use a fresh idempotency key
per distinct submission and retain it for an identical retry.

A request for a video should use **astria-api**'s supported video workflow with
these same references; do not silently deliver still images instead.

## Finish the set

Check every returned prompt with `get_prompt` using its ID and tune ID. Present
the requested completed assets and clearly identify failures or pending work.
When inspection is available, compare identity, garment details, and placement
with the sources. Do not claim exact fit or submit unrequested correction jobs.
