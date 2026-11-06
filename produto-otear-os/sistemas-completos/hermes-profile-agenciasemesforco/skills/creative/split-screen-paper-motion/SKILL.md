---
name: split-screen-paper-motion

description: Use when turning talking-head videos into paper motion.
version: 0.1.0
author: Marlon, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [video, motion-graphics, paper-cut, retention]
    related_skills: []
---

# Split-Screen Paper Motion

Create or plan high-retention vertical videos that keep a talking head in the lower zone while an evolving paper-cut infographic explains the argument above it. Use this for editorial explainers, business commentary, philosophical narratives, and social critique. Do not reduce the result to subtitles over stock footage.

## When to Use

- The user provides a talking-head video and wants animated visual explanations.
- The user provides a reference Reel/TikTok with split-screen infographic editing.
- A script needs paper-cut characters, metaphors, diagrams, labels, and retention edits.
- The desired result resembles an animated editorial collage or visual essay.
- Do not use for cinematic B-roll-only edits, realistic 3D animation, or simple subtitle burning.

## Prerequisites

- A local video file or downloadable video URL.
- `ffmpeg` and `ffprobe` for media processing.
- A vision-capable model for frame analysis. Test one real image before processing the full video.
- A rendering engine such as Drift MCP, Hyperframes/HTML/GSAP, Remotion, After Effects automation, or FFmpeg compositing.
- Optional transcription with Whisper/WhisperX when no transcript exists.

Never expose keys, cookies, passwords, or access tokens. Refer to them as `[REDACTED]`.

## Core Visual System

### Screen architecture

- Canvas: 9:16, normally 1080×1920 or 720×1280, 30 fps.
- Upper visual zone: 42–48% of height.
- Lower presenter zone: 52–58% of height.
- Keep the presenter in medium close-up, usually chest or waist up.
- Place short emphasis captions near the boundary or within the lower zone.
- Keep critical elements away from platform UI: approximately 10% from top, 12% from bottom, and 6% from sides.

### Graphic language

- Base background: warm off-white, beige, kraft, or aged paper.
- Build objects from layered cutouts with irregular torn edges.
- Use soft drop shadows, slight texture, and restrained parallax to simulate physical depth.
- Prefer simple symbolic objects: house, clock, phone, desk, document, contract, money, arrows, chains, conveyor belt, finish line, organization chart.
- Characters may be illustrated cutouts, monochrome portraits, or simplified paper figures.
- Use realistic photos only when identity is essential; remove backgrounds cleanly.

### Color semantics

- Black/white: primary statements and neutral information.
- Yellow: central concept, advantage, insight, or emphasis.
- Red: conflict, risk, contradiction, loss, or reveal.
- Green: solution, salary, security, progress, or positive outcome.
- Blue: institutions, systems, technology, or secondary structure.
- Keep most of the frame neutral so semantic colors remain meaningful.

### Typography

- Use bold condensed or heavy sans-serif in uppercase for fast reading.
- Display one idea per caption, usually 1–5 words.
- Use white on black, black on paper, or a single semantic accent.
- Do not display full verbatim subtitles unless requested.
- Preserve exact spelling and accents in Brazilian Portuguese.
- Never let generated video models render final text when deterministic text rendering is available.

## Procedure

### 1. Acquire and inspect the source

1. Download or locate the original video.
2. Use `ffprobe` through `terminal` to confirm duration, resolution, fps, audio, and rotation.
3. Extract representative frames across the whole timeline, plus denser frames around cuts.
4. Create numbered contact sheets.
5. Test one frame against candidate vision models and record which model actually returns a grounded description.

Completion criterion: the full duration is represented by timestamped frames and at least one vision model has passed a real-image test.

### 2. Transcribe and segment the argument

1. Obtain a timestamped transcript.
2. Correct names, punctuation, and obvious recognition errors.
3. Divide the speech into semantic beats, not arbitrary equal durations.
4. For every beat, record:
   - start and end time;
   - spoken claim;
   - emotional function;
   - concrete visual metaphor;
   - retained elements from the previous beat;
   - new element introduced;
   - exact on-screen phrase, if any.

Completion criterion: every spoken beat has one visual job and one timestamp range.

### 3. Build the visual grammar

Create a compact style specification before animating:

- canvas and fps;
- upper/lower split ratio;
- paper texture and edge style;
- font families and weights;
- five-color semantic palette;
- shadow direction and intensity;
- standard entrance, exit, and emphasis motions;
- caption placement;
- safe zones;
- grain and color treatment.

Completion criterion: all scenes can reuse the same tokens without inventing a new style.

### 4. Convert speech into an evolving diagram

For each beat:

1. Identify the noun: person, company, money, time, risk, family, system.
2. Identify the action: loses, inherits, delegates, waits, pays, scales, breaks.
3. Choose one concrete object that represents the noun/action.
4. Preserve useful objects from earlier beats so the scene grows like a map.
5. Add only one main object or conceptual change every 0.8–1.5 seconds.
6. Use labels to name characters and objects when identification is not obvious.
7. Reserve large color changes for pivots and conclusions.

Completion criterion: the upper zone explains the argument even with audio muted, without becoming a duplicate transcript.

### 5. Create the storyboard

Use this schema for every shot:

```text
SCENE [number] — [start–end]
Spoken beat:
Visual thesis:
Presenter crop/scale:
Upper-zone background:
Persistent elements:
New elements:
Exact on-screen text:
Entrance motion:
Internal motion:
Exit/transition:
Accent color:
Sound cue, if requested:
```

Use these narrative stages:

1. Hook or contrast.
2. Metaphor setup.
3. Concrete example.
4. Diagram expansion.
5. Contradiction or reversal.
6. Explanation.
7. Final synthesis or CTA.

Completion criterion: every frame of the final duration belongs to exactly one storyboard scene.

### 6. Prepare assets

- Use transparent PNG/WebP or SVG for deterministic layering.
- Name assets by scene and role, such as `s03_house_base.png` or `s07_risk_label.svg`.
- Keep photos, cutouts, backgrounds, fonts, and textures in separate folders.
- Generate complex objects separately; do not ask one video model to create the full final composition with exact text.
- Verify identity, period accuracy, and licensing/source for public figures.
- Inspect alpha edges and remove halos before animation.

Completion criterion: every storyboard element has a real asset path or an explicit generation task.

### 7. Animate with restraint

Use a small reusable motion vocabulary:

- Paper pop-in: 92% to 100% scale with slight overshoot.
- Slide-in: 24–60 px over 6–12 frames.
- Stamp: quick scale-down and 1–2 degree rotation.
- Torn-paper reveal: mask wipe following an irregular edge.
- Diagram growth: line draws first, node appears second, label appears last.
- Presenter emphasis: 3–7% digital punch-in on rhetorical pivots.
- Parallax: foreground moves 1.4×, middle 1×, background 0.5×.
- Hold important compositions for at least 0.5–1 second after settling.

Avoid constant bouncing, elastic motion on every object, random transitions, excessive blur, and generated lip-sync.

Completion criterion: a visual state changes approximately every 0.8–1.5 seconds, but the viewer can still read every phrase.

### 8. Composite and synchronize

- Lock all graphic changes to spoken beats, stressed words, pauses, or sentence turns.
- Preserve original audio unless replacement was requested.
- Duck music under speech if music exists.
- Keep the speaker visible during authority, emotion, and punchline moments.
- Allow full-screen infographics only when the explanation benefits from extra space.
- Render text separately from generated imagery for spelling stability.

Completion criterion: every major graphic entrance has a clear audio or narrative trigger.

### 9. Render and verify

1. Render a low-resolution proof first.
2. Review the proof at normal speed and muted.
3. Correct text, timing, unsafe placement, visual overload, and dead sections.
4. Render the delivery file.
5. Use `ffprobe` to verify resolution, fps, duration, codecs, and audio.
6. Extract a final contact sheet and inspect the whole visual arc.

Completion criterion: the final file plays, matches source duration within an intentional tolerance, contains audio when expected, and has no misspelled or clipped text.

## Creating New Scripts in This Style

When the user asks for a new script rather than an edit of existing footage, deliver both the spoken copy and the visual execution plan. Build around an evolving metaphor instead of writing a generic talking-head script first and decorating it afterward.

### Argument map

Organize the script into:

1. Opening belief or uncomfortable tension.
2. Concrete example with identifiable actors.
3. Escalation through consequences.
4. Diagnostic turn: the apparent problem becomes the real problem.
5. Practical mechanism or solution.
6. Responsible boundary: what the tool does not decide.
7. Specific CTA or closing question.

Do not mistake the provocative opening example for the video's complete thesis.

### Script table

Use this default output:

| Time | Spoken line | Visual thesis | Persistent objects | New object/change | On-screen phrase | Semantic color |
|---|---|---|---|---|---|---|

After the table, provide:

- full clean narration;
- asset list grouped by scene;
- allowed motion vocabulary;
- prompts for Flow/Veo or image generation when requested;
- editor notes for captions, paper edge, presenter crop, resets, and final hold.

### Observed high-retention rhythm

Use these defaults unless the current brief overrides them:

- one new visual idea every 1–2 seconds;
- one evolving metaphor for 6–12 seconds;
- title → actor → object → label → stamp/punchline → reset;
- short caption blocks of 2–5 words near the paper boundary;
- reset only when the thesis changes, not after every sentence;
- preserve the presenter during authority, emotion, and punchline moments;
- hold the final composition for 1.5–2 seconds.

### Concrete metaphor library

| Concept | Fast visual representation |
|---|---|
| AI | blue robot or technical core |
| company | office building |
| government | institutional building |
| decision-maker | suited figure |
| workers / citizens | small diverse figures |
| firing / rejection | red stamp |
| approval / benefit | green seal |
| speed | rocket |
| investigation | magnifying glass |
| time / deadline | calendar |
| identity | badge |
| failure | stamp over the original object |
| tool | wrench |
| software error | bugs or marked document |
| message | envelope |
| comparison | dotted divider + VS |
| scattered reports | separated cards or phones |
| organization | funnel or converging paths |
| priority | ordered bars or ranked stack |
| source | document with origin marker |
| human review | hand checking and signing |

Extend the library when needed, but every symbol must be understood in under one second.

### Public, legal, financial, or reputational subjects

Always separate automated signal from human judgment. Show the checkpoint explicitly and use language such as “alert,” “preliminary analysis,” or “item to investigate,” never “proof” unless verified evidence establishes it.

## Reference Analysis Output

When the user asks to copy a reference style, produce:

1. Technical metadata.
2. Timeline by scene.
3. Screen-zone map.
4. Asset inventory.
5. Typography and palette.
6. Motion vocabulary.
7. Cut/change frequency.
8. Retention mechanisms.
9. What is deterministic compositing versus generative imagery.
10. A recreation plan using available tools.

Do not infer unreadable text. Mark uncertainty plainly. If frames were sampled rather than exhaustively decoded, state the exact sample count and approximate interval; never call sampled analysis “every frame.” Distinguish hard cuts from graphic state changes inside one persistent composition.

## Quality Gates

- Hook is visually clear within the first 2 seconds.
- One dominant idea per moment.
- Upper graphics explain rather than merely decorate.
- Presenter remains readable and is not covered by platform UI.
- Text is exact, stable, and on screen long enough to read.
- Accent colors retain consistent meaning.
- Visual changes follow speech, not arbitrary time intervals.
- The infographic accumulates logically across scenes.
- Final frame synthesizes the argument or presents the CTA.
- Output was actually rendered and probed before delivery.

## Pitfalls

- Do not claim a video was visually analyzed from metadata, title, transcript, or captions alone.
- Do not call a slideshow with stock images equivalent to paper-motion editing.
- Do not let a generated model invent Brazilian Portuguese text.
- Do not change all elements simultaneously; preserve continuity.
- Do not crowd both zones with equal detail at the same moment.
- Do not recommend a model merely because its catalog says `vision`; verify it with one real frame.
- Do not report an artifact as available without confirming the file exists and is non-empty.
- Do not expose API keys or authentication material in commands, logs, or reports.

## Verification

A successful delivery includes:

- timestamped storyboard;
- reusable style specification;
- asset manifest;
- rendered video file;
- `ffprobe` verification;
- final contact sheet review;
- concise report of what was rendered, what was verified, and any remaining limitation.
