# YT Clipper - System Prompt & Guidelines

This project is a reusable, modular, and cheap content engine for clipping YouTube videos into shorts.

## Final Stack

- Intelligence Layer: Claude for clip selection, hooks, and reasoning.
- Transcript Layer: `youtube-transcript-api` receives a YouTube URL and outputs timestamped transcript JSON.
- Extraction Layer: `yt-dlp` plus FFmpeg downloads and cuts clips automatically.
- Rendering Layer: Remotion plus Node.js handles captions, motion, and vertical formatting.

## Pipeline

1. Receive a YouTube URL.
2. Use Python and `youtube-transcript-api` to fetch the transcript and output clean JSON.
3. Use Claude to read transcript JSON and output selected clips with timestamps and hooks.
4. Before downloading or cutting video, output timestamps and excerpts in an `.md` review file for user approval.
5. After user approval, use Node.js to call `yt-dlp` and FFmpeg for download and extraction.
6. Pass clips to Remotion for vertical shorts with captions and motion graphics.

## Required Structure

Keep the project structure clean and minimal:

```text
project_root/
├── python/
│   └── transcript.py
├── data/
│   ├── transcript.json
│   └── clips.json
├── video/
│   └── full.mp4
├── assets/
├── Outputs/
├── projects/
├── remotion/
├── scripts/
│   ├── extract.js
│   └── render.js
└── main.js
```

## Responsibility Split

- Python is responsible only for fetching transcripts and outputting clean JSON.
- Claude is responsible for turning transcript JSON into `clips.json`.
- Node.js is responsible for infrastructure: `yt-dlp`, FFmpeg, and Remotion.

## Critical Rules

- Use structured JSON for the final pipeline timestamps.
- Do not use Markdown as the machine input for FFmpeg or Remotion.
- Always create a human-readable `.md` review file with timestamps and excerpts before video download or FFmpeg cuts.
- Do not proceed to download or clipping until the user approves the review file.
- Do not use Playwright.
- Do not build manual upload/download steps.
- Ensure `Outputs/`, `projects/`, and `assets/` exist and are used for their respective purposes.

## Clips JSON

Use this structure for `data/clips.json`:

```json
{
  "clips": [
    {
      "start": 120,
      "end": 135,
      "hook": "This is why most people fail",
      "title": "Discipline Truth"
    }
  ]
}
```

Include `reason` when clip selection is being reviewed or debugged, but keep downstream extraction compatible with `start`, `end`, `hook`, and `title`.

## Environment

Store sensitive credentials in `.env` at the project root and keep `.env` ignored by git.

```env
ELEVENLABS_API_KEY=your_api_key_here
```

ElevenLabs is optional. If integrated, read `ELEVENLABS_API_KEY` from `.env` and read the chosen Voice ID from `config.json`, because the Voice ID is not sensitive.

