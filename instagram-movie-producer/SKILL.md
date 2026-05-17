---
name: instagram-movie-producer
description: Use when creating Instagram Reels, short movie clips, montages, or multi-scene video content with fast-paced keyframe transitions.
allowed-tools: Bash(astria:*)
---

# Instagram Movie Producer

Create engaging 30-second Instagram Reels with fast-paced scene switches using keyframed video prompts.

## Video Format
- Aspect ratio: **9:16** (vertical, Instagram Reels)
- Total duration: ~30 seconds
- Scene switches every **1-3 seconds** for fast, engaging cuts
- 20-30 keyframes total across multiple prompts (max 8 keyframes per prompt)

## The Hook (CRITICAL)
Every video MUST start with a compelling hook in the first keyframe. The hook presents a secret or promise that makes the viewer stay. The hook text should appear as overlay text in the first scene.

Hook formula: **Tease a secret + promise a reveal**

Examples:
- "Want to make money with AI? Let me show you how"
- "Want to learn the secret to making realistic AI models? Here is how"
- "Consistent high quality results - in 3 easy steps"
- "Nobody is talking about this AI trick"
- "Stop scrolling - this will change how you create content"
- "The #1 mistake everyone makes with AI images"

The first keyframe should be an attention-grabbing close-up or dramatic shot that pairs with the hook text.

## Keyframe Syntax
Each prompt uses triple-dash `---` separators between keyframes. Each keyframe generates an image, and video transitions are created between consecutive keyframes. 

Format per keyframe:
```
scene description --video --video_model MODEL --video_prompt "camera/motion description" --duration SECONDS
```

Full prompt example (3 keyframes = 2 video transitions):
```
Close-up of a woman looking directly at camera with surprised expression, text overlay "Want to know the secret?" --video --video_model kling30_standard --video_prompt "slow zoom in on face" --duration 3
---
Wide shot of a modern studio with multiple AI-generated images on screens --video --video_model kling30_standard --video_prompt "camera pans across the studio" --duration 3
---
Close-up of hands typing on keyboard with AI interface visible --video --video_model kling30_standard --video_prompt "dynamic camera movement around the workspace" --duration 3
```

## Recommended Video Models for Reels
| Model | ID | Duration Range | Best For |
|-------|-----|---------------|----------|
| Kling 3.0 Standard | `kling30_standard` | 3-15s | High quality, flexible duration |
| Kling 3.0 Pro | `kling30_pro` | 3-15s | Premium quality |
| Seedance V1.5 720p | `seedance_v15_720p` | 4-12s | Cost-effective, good quality |
| VEO3 Fast 720p | `veo31_fast_720p` | 4/6/8s | Fast generation |

Default recommendation: **kling30_standard** for best balance of quality, flexibility (3s minimum duration for fast cuts), and cost.

## Production Plan (4 prompts x 7-8 keyframes = ~30 seconds)

### Prompt 1: The Hook (keyframes 1-8, ~8-10 seconds)
- Keyframe 1: Hook shot - dramatic close-up with text overlay tease (2-3s)
- Keyframes 2-4: Quick establishing shots that build curiosity (1-2s each)
- Keyframes 5-8: Start revealing the topic with fast cuts (1-2s each)

### Prompt 2: The Build (keyframes 9-16, ~8-10 seconds)
- Show the process/steps/method with varied angles
- Alternate between close-ups and wide shots
- Each keyframe 1-3 seconds for dynamic pacing

### Prompt 3: The Payoff (keyframes 17-24, ~8-10 seconds)
- Reveal results, transformations, or outcomes
- Use impressive/dramatic shots
- Build toward the climax

### Prompt 4: The Finale (keyframes 25-30, ~4-6 seconds)
- Showcase the best result
- End with a strong call-to-action shot
- Final keyframe: logo/branding or "Follow for more"

## Text Overlay Typography Style
When describing text overlays in keyframes, follow this premium editorial typography style:
- **Font style**: Bold, condensed sans-serif (think Oswald, Bebas Neue, Helvetica Condensed Bold) — heavy weight, tight letter-spacing
- **Scale**: Text should be LARGE — filling a significant portion of the frame, hero-level sizing, not small subtitles
- **Color**: White text on dark or moody photographic backgrounds for maximum contrast and readability
- **Visual hierarchy**: Use mixed weight and style — main keywords in heavy bold uppercase, accent words like "AI" in italics, secondary taglines in lighter italic weight
- **Word count**: Keep it minimal — short punchy phrases (2-5 words), not full sentences
- **Aesthetic**: Editorial luxury magazine feel — premium, cinematic, scroll-stopping. NOT generic, templated, or "corporate"
- **Placement**: Position text with intentional negative space, often bottom-left or right-aligned, overlapping the subject for editorial drama
- **Word-by-word pacing**: Text should appear progressively across keyframes in sync with the narration — each keyframe shows only the word(s) being spoken at that moment, not the full sentence at once. This creates a kinetic typography effect where the viewer reads along with the voiceover beat by beat.

Example: For the narration "Want to make money with AI?", split across keyframes:
- Keyframe 1: text overlay "Want to" (1-2s)
- Keyframe 2: text overlay "make money" (1-2s)
- Keyframe 3: text overlay "with AI?" (1-2s)

Example descriptions for keyframes with text:
- `"Close-up of lips with lip pencil, large bold condensed white text 'Premium AI shots' overlaid at bottom-left, italic on 'AI', editorial magazine style"`
- `"Woman in dark sweater with arms crossed, bold condensed white text 'Generate AI Images' with 'for your brand' in light italic below, luxury editorial typography"`

## Scene Composition Tips
1. **Vary shot types**: Alternate close-ups, medium shots, wide shots, and overhead angles
2. **Use motion prompts**: Each `--video_prompt` should describe camera movement (zoom, pan, dolly, orbit)
3. **High contrast**: Use dramatic lighting, bold colors for scroll-stopping visuals
4. **Text overlays**: Describe text in the scene prompt using the editorial typography style above
5. **Consistent style**: Keep a cohesive visual style across all keyframes (same color grading, lighting mood)
6. **People sell**: Include human subjects when relevant - expressions, reactions, hands at work

## Camera Movement Library (for --video_prompt)
- `"slow zoom in on face"` - intimate, attention-grabbing
- `"camera pulls back to reveal"` - dramatic reveal
- `"smooth dolly forward"` - draws viewer in
- `"orbit around subject"` - dynamic, professional
- `"quick pan left to right"` - energetic transition
- `"overhead top-down shot slowly rotating"` - modern, clean
- `"handheld camera following subject"` - authentic, raw feel
- `"slow motion close-up"` - emphasis on detail
- `"camera rises upward dramatically"` - epic feel

## Workflow
1. Ask the user about the topic/niche for their Reel
2. Query the user's tunes with `astria tunes list` to find relevant references for the content
3. Write the hook based on the topic
4. Create 4 sequential prompts with 7-8 keyframes each, all using `--video --video_model kling30_standard` and aspect_ratio 9:16
5. Show each prompt to the user for review before generating
6. Generate the prompts sequentially with `astria generate` (see the `astria-api` skill)
7. Tell the user the 4 video clips can be stitched together in any video editor or Instagram's built-in editor

## API Call Format

Each Reel "prompt" is a single multi-keyframe `astria generate` call — the
keyframe text (with its inline `--video` flags) goes in `--text`:

```
astria generate --model gemini --aspect-ratio 9:16 --num-images 1 \
  --text "KEYFRAME_1_TEXT\r\n---\r\nKEYFRAME_2_TEXT\r\n---\r\nKEYFRAME_3_TEXT"
```

Note: `num_images` is automatically set to the number of keyframes by the system. The `\r\n---\r\n` delimiter is critical — it must be carriage return + newline + three dashes + carriage return + newline.

## Important Constraints
- Max 8 keyframes per prompt (system limit)
- For 30-second videos, split across 3-4 prompts
- Minimum duration per transition: 3 seconds for Kling 3.0, 4 seconds for Seedance V15 and VEO3
- Each keyframe must repeat `--video` and `--video_model` flags
- Use tune references `<faceid:ID:1>` if user has relevant face/product references
