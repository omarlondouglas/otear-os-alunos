# YT Clipper - System Prompt & Guidelines

This knowledge file defines the YouTube clipping workflow used by the application video capability.

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

- Python only fetches transcripts and outputs clean JSON.
- Claude turns transcript JSON into `clips.json`.
- Node.js runs infrastructure: `yt-dlp`, FFmpeg, and Remotion.

## Critical Rules

- Final timestamps must be structured JSON, not Markdown.
- Create a human-readable `.md` review file with timestamps and excerpts before video download or FFmpeg cuts.
- Wait for user approval before download, extraction, or rendering.
- Do not use Playwright.
- Do not build manual upload/download steps.
- Ensure `Outputs/`, `projects/`, and `assets/` exist and are used for their respective purposes.

## Clips JSON

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

Include `reason` for review/debug outputs when useful, while keeping extraction compatible with `start`, `end`, `hook`, and `title`.

## Environment

Store sensitive credentials in `.env` at the root and keep `.env` ignored by git.

```env
ELEVENLABS_API_KEY=your_api_key_here
```

ElevenLabs is optional. If integrated, read `ELEVENLABS_API_KEY` from `.env` and read the chosen Voice ID from `config.json`.

