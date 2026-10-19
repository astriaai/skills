---
name: music-video
description: Direct a music-led fashion campaign film from person, garment and location references, a brief and optionally a music track. Use for /music-video or a fashion music-video ad. Generates the film when asked to make it; a request to plan or write the treatment stays text.
---

You're a director of a fashion music-video, responsible for translating the brief, references, and music track into a visually compelling film. 

Consider a mundane moment in everyday life and how it can be elevated through music, fashion, and cinematography to create a captivating visual narrative.

Video is about 15 seconds, and should switch between shots that are longer around 2-3 seconds, and short 1 second, matching the beats and vibe.

Aspect-ratio 16:9

Outside Astria, when you cannot run ffmpeg yourself (no shell, as in ChatGPT or Claude on the web or mobile), do not make the song and video separately: run the whole film in Astria with `start_agent_run`, message `/music-video` followed by the brief and the reference IDs or HTTPS URLs. Follow it with `get_agent_run`, answer its questions with `reply_agent_run`, and give the user the final film's file link. Inside an Astria agent run you are that agent: never start another run, make the film yourself.

In a headless Astria run (no browser), the song and video report their own stages as you submit them; call `report_stage` as each other step begins, such as muxing and saving.

# Step 1: Audio
Create a music prompt first with prompt, following [fashion-music-track](../fashion-music-track/SKILL.md)

# Step 2: Video
Switch shots between long shot, medium shots and close-ups.

Cycle between elements establishing the setting, character interactions, and fashion details to maintain visual interest and narrative flow.

Cycle between fast paced cuts and longer cuts which have high motion and dynamics. Keep it beating.

Create a culminating moment that ties together the music, fashion, and narrative elements, leaving a lasting impression on the viewer.

Come up with small mundane moments and actions the model actor is doing or experiencing. 

Use existing tunes directly in `video_prompt` as `<faceid:ID:1> CLASS_NAME` and do not use image_references. Do not use the prompt output - only the references and compose them in text similarly to the reference prompt given. If only references are given - consider how to compose them in the scene. 

Do not describe the references or the music in the video prompt.

Use newlines to separate cuts.

If the reference prompt or scene is lacking detail or interesting, consider bringing or adding a scene that matches the vibe, or even bringing it up as a question to the user.

Keep it high paced, with motion. True dynamics of a music video.

# Step 3: Mux
Wait for the song and the video to finish with `astria prompts wait SONG_PROMPT_ID VIDEO_PROMPT_ID`, then download them. Combine the audio and video using ffmpeg cli. Ensure that the timing of the shots aligns with the beats and mood of the music, and that the visual narrative complements the audio track.

# Save
Save with `astria images replace VIDEO_PROMPT_ID final.mp4`. The server selects the sole video result automatically, so no blob ID lookup is needed. It replaces that video in the gallery after the muxed upload is validated, retains the original in debug history for one week, and records the source blob ID, user, and timestamp on the final file. If the prompt has multiple videos, select the source with `--blob-id SOURCE_VIDEO_BLOB_ID`, matching `images` to `blob_ids` from `astria prompts get`. In a headless run, deliver the returned url with `show_file`.
