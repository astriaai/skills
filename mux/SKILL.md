---
name: mux
description: Combine video with music track, and save the final film.
---

Use ffmpeg in an available shell. If not possible, consider using MCP `start_agent_run`. Follow it with `get_agent_run`, answer its questions with `reply_agent_run`, and give the user the final film's file link. Inside an Astria agent run you are that agent: never start another run, make the film yourself.

Wait for the song and video to finish, then download them. Existing local files can be used directly. Align the soundtrack with the intended beats and shot timings, then mux with ffmpeg. Choose whether to replace or mix existing audio from the brief; preserve intentional dialogue or effects. Check the final duration, audio playback, and synchronization before saving.

When saving back to Astria, use `astria images replace VIDEO_PROMPT_ID final.mp4`. The server selects the sole video result automatically; no blob ID lookup is needed. It replaces that video in the gallery after validating the muxed upload, retains the original in debug history for one week, and records the source blob ID, user, and timestamp on the final file. If the prompt has multiple videos, select the source with `--blob-id SOURCE_VIDEO_BLOB_ID`, matching `images` to `blob_ids` from `astria prompts get`.

Deliver the saved final film. In a headless Astria run, call `report_stage` when muxing and saving begin, then pass the returned URL to `show_file`. For a local-only deliverable, return the final file without replacing an Astria gallery result.
