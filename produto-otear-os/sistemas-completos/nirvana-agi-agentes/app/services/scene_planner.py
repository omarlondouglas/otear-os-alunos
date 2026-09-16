"""
Scene Planner — Uses Claude/Gemini to analyze transcription and generate
a visual scene plan for Remotion rendering.

The AI receives numbered words (not timestamps!) and returns scene types
pointing to word indices. Code then converts indices to exact frames.
This avoids LLM arithmetic errors — the "pulo do gato" from the reference pipeline.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

SCENE_TYPES_DESCRIPTION = """
Available scene types (each has its own animation in the video):

A (fullscreen) — Full-screen impact phrase. Use for central affirmations, shocking statements.
B (lower-third) — Text at bottom, face stays visible. Use for context, presentation, introductions.
C (split) — Panel above + face below. Use for points that need development, explanations.
D (split-vertical) — Side-by-side comparison. Use for contrasts, before/after, myths vs facts.
E (card) — Numbered card with icon. Use for lists, sequential tips, features.
F (message) — WhatsApp-style message bubble. Use for dialogues, simulated conversations, objections.
G (number) — Big animated number/stat. Use for statistics, results, percentages, data points.
H (flow) — Vertical step flow. Use for processes, sequences, step-by-step instructions.
I (cta) — Call to action with pulsing keyword. Use for closing, invitation, engagement prompt.
J (stickfigure) — Stick figure illustration. Use for situations, narratives, humor, analogies.
"""

SYSTEM_PROMPT = """You are a video scene planner. You analyze transcriptions and create visual scene plans.

You receive a numbered list of transcription words and must decide:
1. The NARRATIVE FORMAT of the video (tutorial, story, list, opinion, debate, motivational, sales)
2. A COLOR PALETTE that fits the content mood
3. Which SCENES to create and WHERE to place them (by word index, NOT timestamp)

RULES:
- Point to word indices, never to timestamps. The code will calculate exact frames.
- Each scene should appear at a natural breakpoint (new topic, emphasis, data point, etc.)
- Don't over-do it: 4-8 scenes for a 5-minute video, 2-4 for a 1-minute clip
- Scenes should ENHANCE the video, not overwhelm it. Most of the time the face should be visible.
- Use "fullscreen" sparingly (only for the most impactful phrases)
- Use "number" only when there's an actual number/stat being mentioned
- Use "split-vertical" only for genuine comparisons
- Scene duration: 3-8 seconds typically (90-240 frames at 30fps)
- Leave breathing room between scenes (not every second needs a visual)

""" + SCENE_TYPES_DESCRIPTION + """

RESPONSE FORMAT (JSON only, no markdown):
{
  "narrativeFormat": "tutorial|story|list|opinion|debate|motivational|sales",
  "palette": {
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "rgba(r,g,b,a)",
    "text": "#hex"
  },
  "scenes": [
    {
      "type": "fullscreen|lower-third|split|split-vertical|card|message|number|flow|cta|stickfigure",
      "wordIndex": 0,
      "durationSeconds": 5,
      "text": "Main text for the scene",
      "secondaryText": "Optional secondary text",
      "items": ["Optional", "list", "items"],
      "number": 1000,
      "numberSuffix": "%",
      "icon": "🚀",
      "animation": "spring"
    }
  ]
}
"""


def plan_scenes(
    words: List[Dict[str, Any]],
    fps: int = 30,
    provider: str = "auto",
    custom_prompt: str = "",
) -> Dict[str, Any]:
    """
    Analyze transcription words and generate a scene plan.

    Args:
        words: List of {"word": str, "start": float, "end": float}
        fps: Video frame rate
        provider: "claude", "gemini", or "auto" (tries claude first)
        custom_prompt: Additional context/instructions for the AI

    Returns:
        {
            "scenes": [SceneOverlay objects with startFrame/durationFrames calculated],
            "palette": ColorPalette,
            "narrativeFormat": str
        }
    """
    if not words:
        return {"scenes": [], "palette": _default_palette(), "narrativeFormat": "unknown"}

    # Build numbered word list for the AI (no timestamps — just index + word)
    numbered_words = []
    for i, w in enumerate(words):
        numbered_words.append(f"[{i}] {w['word']}")

    # Group into lines of ~15 words for readability
    word_lines = []
    for i in range(0, len(numbered_words), 15):
        word_lines.append(" ".join(numbered_words[i:i+15]))

    user_message = "Here are the transcription words (numbered):\n\n"
    user_message += "\n".join(word_lines)
    user_message += f"\n\nTotal words: {len(words)}"
    user_message += f"\nVideo duration: {words[-1]['end']:.1f} seconds"

    if custom_prompt:
        user_message += f"\n\nAdditional context: {custom_prompt}"

    user_message += "\n\nAnalyze this content and create a scene plan. Return ONLY valid JSON."

    # Call AI provider
    raw_plan = _call_ai(user_message, provider)

    if not raw_plan:
        logger.warning("[ScenePlanner] AI returned empty plan, using fallback")
        return {"scenes": [], "palette": _default_palette(), "narrativeFormat": "unknown"}

    # Convert word indices to frame positions
    scenes = []
    for scene_data in raw_plan.get("scenes", []):
        word_idx = scene_data.get("wordIndex", 0)
        duration_sec = scene_data.get("durationSeconds", 5)

        # Clamp word index to valid range
        word_idx = max(0, min(word_idx, len(words) - 1))

        # Get exact start time from word timestamp
        start_time = words[word_idx]["start"]
        start_frame = int(start_time * fps)
        duration_frames = int(duration_sec * fps)

        scene = {
            "type": scene_data.get("type", "lower-third"),
            "wordIndex": word_idx,
            "startFrame": start_frame,
            "durationFrames": duration_frames,
            "text": scene_data.get("text", ""),
            "secondaryText": scene_data.get("secondaryText"),
            "items": scene_data.get("items"),
            "number": scene_data.get("number"),
            "numberSuffix": scene_data.get("numberSuffix"),
            "icon": scene_data.get("icon"),
            "accentColor": scene_data.get("accentColor"),
            "backgroundColor": scene_data.get("backgroundColor"),
            "animation": scene_data.get("animation", "spring"),
        }
        scenes.append(scene)

    palette = raw_plan.get("palette", _default_palette())
    narrative_format = raw_plan.get("narrativeFormat", "unknown")

    logger.info(f"[ScenePlanner] Generated {len(scenes)} scenes, format: {narrative_format}")

    return {
        "scenes": scenes,
        "palette": palette,
        "narrativeFormat": narrative_format,
    }


def _call_ai(user_message: str, provider: str = "auto") -> Optional[Dict]:
    """Call Claude or Gemini to generate scene plan."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if provider == "auto":
        if openrouter_key:
            provider = "openrouter"
        elif anthropic_key:
            provider = "claude"
        elif google_key:
            provider = "gemini"
        else:
            logger.error("[ScenePlanner] No AI provider configured")
            return None

    try:
        if provider == "openrouter" and openrouter_key:
            return _call_openrouter(user_message, openrouter_key)
        elif provider == "claude" and anthropic_key:
            return _call_claude(user_message, anthropic_key)
        elif provider == "gemini" and google_key:
            return _call_gemini(user_message, google_key)
        else:
            logger.error(f"[ScenePlanner] Provider '{provider}' not available")
            return None
    except Exception as e:
        logger.error(f"[ScenePlanner] AI call failed: {e}")
        return None


def _call_openrouter(user_message: str, api_key: str) -> Optional[Dict]:
    from openai import OpenAI

    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers=headers or None,
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL_SMART", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")),
        max_tokens=2048,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    return _parse_json_response(text)


def _call_claude(user_message: str, api_key: str) -> Optional[Dict]:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    model = os.getenv("MODEL_SMART", "claude-sonnet-4-20250514")

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    text = response.content[0].text.strip()
    return _parse_json_response(text)


def _call_gemini(user_message: str, api_key: str) -> Optional[Dict]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))

    response = model.generate_content(f"{SYSTEM_PROMPT}\n\n{user_message}")
    text = response.text.strip()
    return _parse_json_response(text)


def _parse_json_response(text: str) -> Optional[Dict]:
    """Parse JSON from AI response, handling markdown code blocks."""
    # Strip markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (``` markers)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
        if text.startswith("json"):
            text = text[4:]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"[ScenePlanner] Failed to parse AI response: {e}\nResponse: {text[:500]}")
        return None


def _default_palette() -> Dict[str, str]:
    return {
        "primary": "#FFFFFF",
        "secondary": "#CCCCCC",
        "accent": "#FFFF00",
        "background": "rgba(0,0,0,0.85)",
        "text": "#FFFFFF",
    }
