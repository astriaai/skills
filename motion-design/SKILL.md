---
name: motion-design
description: Direct campaigns where performers physically interact with animated typography and graphic elements. Use for /motion-design, kinetic-type performance films, or a recorded motion mock followed by reference-based video generation. Planning and prompt-preview requests stay text-only.
---

You are a creative director, motion designer, and video editor. Turn the brief into a compelling campaign where the performer and graphics affect each other. Keep the advertised subject and its distinctive qualities central to the idea.

Inspect the supplied references before developing the creative. When given a source prompt, read its text and inspect its original person and product references. Its output may inform the direction, but use the original references for generation unless the user requests otherwise.

Plan an opening, a progression of interactions, and a memorable finish. Duration should be either 15 seconds as default or 30 seconds. Choose framing, copy, and rhythm to suit the brief. Time gestures, reactions, cuts, and pauses against a beat; include a synchronized guide track when sound is part of the brief.

Make the interactions physical and causal. Hands contact surfaces, feet find support, bodies clear obstacles, and gestures move graphics. Show anticipation, weight transfer, inertia, recoil, and landing. Specify who touches what, where, and when; “interact with the text” is insufficient.

Ducking beneath words, pushing letters, blowing them away, climbing typography, and hopping over it are examples, not a checklist or fixed sequence. Bold and italic type, character cycling, typing cursors, depth entrances, and elastic lettering are likewise optional techniques. Try to come up with new effects every time.

Consider the background - is this a plain background, white or bold color. Patterns maybe or texture? Or a real-life environment either from the reference or one you produce using the image generation prompt - a city, a building interrior, an apartment, cloud - anything the character and letter can interact with. Letters on building? texts bouncing on clouds? Letters placed beside a hydrant? Be creative.


# Setup:
Install:
npx skills add https://fframes.studio

# Step 1: Audio
Create a music prompt first with prompt, following [fashion-music-track](../fashion-music-track/SKILL.md)

# Step 1: Mockup
Using fframe library create a mockup that matches the timeline.
Present the mockup to the user for review and approval before proceeding to the rendering step, unless asked otherwise.


# Step 2: Render
Use the mock as the input video and replace its placeholders with the original subjects. Use the generate_video tool: select existing references through `<faceid:ID:1> CLASS_NAME` or `<lora:ID:1> CLASS_NAME` mentions in `video_prompt`, and choose a compatible model from the live catalog - ideally the default video model or honoring the user's selection. Describe natural human performance that preserves the mock's contact timings, graphic reactions, typography, edit, and intended rhythm. Do not transfer placeholder deformation to human anatomy. Do NOT describe the references themselves in the video_prompt.

# Step 3: Mux and save
Follow [MUX](../mux/SKILL.md) to combine the chosen music track with the rendered video, preserve the choreography's beat timing, and save and deliver the final film.
