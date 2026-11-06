---
name: codex-terminal-videos
description: "Use when creating sci-fi HUD videos with blueprints."
version: 1.0.0
category: creative
tags: [video, sci-fi, hud, blueprint, codex-terminal, motion-design]
---

# Codex Terminal Video Production Skill

Use this skill to produce polished sci-fi / technical HUD overlay videos featuring telemetry, radar sweeps, blueprints, and terminal aesthetics (inspired by the "Os Três Saltos" style).

## Video Structure & Narrative (3-Act Framework)

1. **Act I: Introduction / Scan (0s - 30s)**
   - **Aesthetic:** Minimalist dark/red (`BIOMA://DARK`), Codex Terminal V.2060.4 header.
   - **Visuals:** Radar sweep (360°), target indicators, system telemetry, live camera feed (`CAM-01`).
   - **Copy / Hook:** Philosophical or technical setup establishing the challenge.

2. **Act II: Technical Breakdown / Simulation (30s - 60s)**
   - **Aesthetic:** Blueprint style (`BIOMA://DEEP-BLUE`), engineering wireframes.
   - **Visuals:** Technical annotations, safety factors, distance metrics, component breakdowns.
   - **Copy:** Engineering analysis or operational breakdown.

3. **Act III: Extreme Scenario / Climax (60s - end)**
   - **Aesthetic:** Abyssal green HUD (`BIOMA://ABISSAL`), critical warning states.
   - **Visuals:** Error logs (`CHÃO NÃO DETECTADO`), attitude/pitch/roll telemetry, high-stakes simulation.
   - **Copy:** Final resolution and takeaway.

## Production Pipeline

1. **Script & Audio Generation:**
   - Write script divided into 3 temporal blocks.
   - Record or synthesize voiceover narration.

2. **HUD & Graphics Generation:**
   - Build HTML/CSS canvas templates using the Codex Terminal design system (monospaced fonts, radar animations, telemetry bars, blueprint SVG graphics).
   - Capture video frames or render animation frames via Puppeteer/Playwright or canvas export.

3. **Compositing & Editing (FFmpeg):**
   - Overlay the HUD animations and live video feed onto the background video.
   - Merge audio track with precise timing markers.
   - Export final MP4 video.
