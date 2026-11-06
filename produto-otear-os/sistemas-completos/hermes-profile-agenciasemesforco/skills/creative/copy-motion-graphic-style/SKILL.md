---
name: copy-motion-graphic-style
description: "Use when cloning or analyzing motion graphic video styles."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [motion-graphics, video-analysis, prompt-engineering, omni-flash, style-transfer, video]
---

# Copy Motion Graphic Style (Motion Director & Prompt Engineer)

## When to use
Use this skill when analyzing a motion graphics, 2D/3D animation, product demo, or SaaS explainer video to reverse-engineer its visual style, composition, pacing, and motion language, and generate ready-to-paste Google Omni Flash generation prompts.

## Core Workflow

### 1. Frame Extraction & Visual Inspection
- Extract representative frames across the entire video duration (not just opening seconds) using `ffmpeg` or video frame inspection.
- Inspect composition, lighting, typography, and motion transitions across all beats.

### 2. Shot-by-Shot Breakdown
For each scene/beat, document:
- **Timestamp Range:** Start and end time.
- **Composition & Camera:** Framing (wide/close-up), aspect ratio, camera movement (pan, zoom, orbit), depth of field, focal points.
- **Visual Elements:** Every subject, 3D element, illustration, icon, and UI component (shapes, positioning, scale).
- **Text & Typography:** Exact wording, font style/weight, hierarchy, colors, entrance/exit animations.
- **Color Palette:** Hex codes for backgrounds, primary accents, secondary accents, and gradients.
- **Lighting, Texture & Finish:** Specular highlights, shadows, ambient occlusion, grain, metallic/matte shaders.
- **Motion & Transitions:** Easing curves, motion paths, morphs, cuts, match cuts into the next beat.
- **Audio & SFX:** Sound design mood, beat alignment, whooshes, clicks, voiceover pacing.
- **Top-Line Summary:** Total duration, resolution, frame rate, 1-line style definition, and recurring visual motifs.

### 3. Google Omni Flash Prompt Generation
Convert the breakdown into a single direct, ready-to-paste generation block containing:
- **Dense Style Line:** Mood, lighting, color grading, camera finish, rendering quality in one punchy sentence.
- **Technical Specifications:** Resolution, aspect ratio, fps, and duration (proportionally scaled to 10s if source is longer).
- **Beat-by-Beat Timeline:** Exact color hexes, font specs, icon geometry, and object motion per second.
- **Locked Typography Spec:** Definite font rules, tracking, placement.
- **Sound Design Guide:** Visual beat-synced audio cues.
- **Final-Frame Spec:** Description of the final held frame.
- **Custom Overrides:** Apply requested brand names, logos, color overrides, copy changes, or duration adjustments while keeping unspecified elements faithful to the analyzed source.
