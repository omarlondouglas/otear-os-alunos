---
name: youtube-highlight-clipper
description: Select high-retention short-form clips from long YouTube videos, podcasts, interviews, lectures, or timestamped transcripts. Use when user says "clip this YouTube video", "find highlights", "make shorts", "extract viral clips", "turn this podcast into reels", provides a YouTube URL, or provides transcript JSON/text and wants timestamps, hooks, reasons, FFmpeg-ready JSON, or Remotion-ready clip data.
---

# YouTube Highlight Clipper

Turn long-form YouTube content into short, high-impact vertical clips for TikTok, Instagram Reels, and YouTube Shorts.

## When to Use This Skill

Use this skill for:

- YouTube URL to Shorts/Reels/TikTok clip planning
- podcast, interview, lecture, or talking-head highlight selection
- timestamped transcript analysis
- strict JSON clip output for FFmpeg or Remotion
- hook rewriting and retention reasoning

Do not use this skill for generic video editing requests that do not involve selecting highlight moments from spoken long-form content.

## CRITICAL: When to Read CODEX.md

Before planning or executing the full YouTube clipping pipeline from a URL, read [CODEX.md](CODEX.md).

Use `CODEX.md` when the task includes transcript fetching, user timestamp review, video download, FFmpeg extraction, Remotion rendering, folder structure, environment variables, or implementation work in this repository.

For a simple transcript-only clip selection task, this `SKILL.md` is enough unless the user mentions the project pipeline.

## Input Contract

Accept:

- full transcript, ideally timestamped
- YouTube URL when the pipeline will fetch the transcript
- optional video title
- optional topic or niche
- optional target audience

If timestamps are missing, identify the best quote ranges textually and state that exact `start` and `end` seconds require timestamped transcript data.

## Step 1: Classify the Request

Choose one path:

- Transcript-only selection: use this `SKILL.md` and return clip JSON or review notes.
- Full project pipeline from URL: read `CODEX.md` before doing implementation or execution.
- App/backend integration: use `app/knowledge/youtube-highlight-clipper/CODEX.md` as the product knowledge source.

## Step 2: Select Candidate Moments

Select multiple short-form clips that:

- capture attention within the first 1-3 seconds
- deliver a complete, self-contained idea
- emphasize emotional, controversial, surprising, or insight-driven moments
- work without relying heavily on previous context

Prioritize transcript moments with at least one of these qualities:

- strong hooks: bold statements, surprising claims, contrarian opinions
- emotional peaks: passion, frustration, excitement, personal turning points
- insight density: clear takeaways, advice, frameworks, useful mental models
- controversy or tension: disagreement, challenge to common beliefs, stakes

Avoid:

- long explanations without payoff
- low-energy or filler dialogue
- segments requiring prior context
- generic or obvious statements

## Step 3: Enforce Clip Constraints

- Keep each clip between 10 and 25 seconds.
- Prefer roughly 15 seconds when possible.
- Include a strong hook in the first sentence.
- Avoid segments that need missing setup.

## Step 4: Build the Clip JSON

1. Scan the transcript for candidate moments with timestamps.
2. Reject candidates that need too much prior context.
3. Prefer complete ideas that can stand alone in 10-25 seconds.
4. Choose exact `start` and `end` timestamps in seconds.
5. Extract or rewrite the first line into a stronger short-form hook.
6. Explain why the clip would retain attention.
7. Return only strict JSON unless the user asks for analysis.

## Step 5: Optimize Hooks

For each clip, make the hook:

- direct
- clear
- emotionally charged
- specific enough to create curiosity

Example rewrite:

- Original: `I think consistency is important`
- Optimized: `Most people fail because they're not consistent`

Do not invent claims that are unsupported by the transcript. Rewrite only to sharpen the speaker's existing point.

## Output Format: Production JSON

Return strict machine-readable JSON:

```json
{
  "clips": [
    {
      "title": "Short descriptive title",
      "start": 123,
      "end": 138,
      "hook": "Compelling opening line",
      "reason": "Why this clip works for retention"
    }
  ]
}
```

Do not include Markdown fences when the user requests production JSON.

## Output Rules

- Use numbers for `start` and `end`, measured in seconds.
- Keep `title` short and descriptive.
- Keep `reason` concise, but explain the retention intent.
- Ensure `end - start` is between 10 and 25 whenever timestamp data allows it.
- Make the output compatible with FFmpeg and Remotion downstream workflows.

## Examples

User says: `clip this YouTube video into shorts`

Actions:

1. Read `CODEX.md`.
2. Fetch or request a timestamped transcript.
3. Create a review `.md` with timestamps and excerpts before any download or cuts.
4. Wait for user approval before FFmpeg extraction or Remotion rendering.

User says: `here is the transcript, find viral clips`

Actions:

1. Use this `SKILL.md`.
2. Select 10-25 second complete moments.
3. Return strict JSON with `title`, `start`, `end`, `hook`, and `reason`.

## Troubleshooting

### Missing timestamps

Cause: Transcript text has no timing data.

Solution: Return candidate excerpts and ask for timestamped transcript data before promising FFmpeg-ready `start` and `end` values.

### Clip depends on previous context

Cause: The selected moment starts after the setup.

Solution: Expand the start slightly if it still fits 10-25 seconds, or reject the candidate.

### Pipeline is requested before user approval

Cause: The request includes extraction or rendering from a URL.

Solution: Read `CODEX.md` and create the mandatory review `.md` before download, FFmpeg cuts, or Remotion rendering.

## Quality Checklist

Before finishing, verify:

- The skill path was chosen correctly: transcript-only or full pipeline.
- `CODEX.md` was read when the task involved URL, download, FFmpeg, Remotion, or repository implementation.
- Every timestamped clip is 10-25 seconds when timestamp data allows it.
- Every clip has a hook, title, reason, start, and end.
- The final machine output is strict JSON when the user needs pipeline compatibility.
