#!/bin/bash
set -e
cd "$(dirname "$0")/../../../.."
[ -f .env ] && set -a && source .env && set +a

OUT="squads/noticias-carrossel-ia/output/2026-04-12-151424/images/v2"
mkdir -p "$OUT"

PROMPT="Cinematic wide shot, portrait 3:4 aspect ratio. A bright glowing orange 8-point asterisk sunburst logo (warm coral orange #E8734A, the Claude AI symbol, simple geometric shape) escaping from a shattered transparent glass containment cylinder inside a dark high-security AI laboratory. The glowing symbol is mid-flight, leaving a luminous orange light trail behind it. Shards of broken glass frozen in mid-air around it. Red warning strobe lights wash the walls. Server racks and thick cables in the deep background, out of focus. Heavy volumetric fog, dramatic rim lighting, cinematic sci-fi atmosphere, photorealistic, high contrast, dark moody tones, Denis Villeneuve aesthetic. No text, no logos other than the orange asterisk."

PAYLOAD=$(jq -n --arg p "$PROMPT" '{
  contents: [{parts: [{text: $p}]}],
  generationConfig: {responseModalities: ["IMAGE"]}
}')

curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" > "$OUT/response.json"

# Extract base64 image and decode
jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data' "$OUT/response.json" | base64 -d > "$OUT/img-slide-01.png"

ls -la "$OUT/img-slide-01.png"
