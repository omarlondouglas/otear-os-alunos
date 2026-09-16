# xAI Grok Imagine via Hermes image_gen provider

Use this reference when testing image generation through xAI/Grok Imagine inside a Hermes environment.

## Credentials and model selection

- API key env var: `XAI_API_KEY`.
- OAuth alternative: configure xAI Grok OAuth through `hermes model` or `hermes auth add xai-oauth`.
- Text-to-image models exposed by the Hermes provider:
  - `grok-imagine-image` — faster default.
  - `grok-imagine-image-quality` — higher fidelity, slower.
- Override for a one-off shell run: `XAI_IMAGE_MODEL=grok-imagine-image-quality`.
- Provider supports `portrait`, `square`, and `landscape`; xAI maps these to `9:16`, `1:1`, and `16:9`.

## Direct smoke test from the Hermes repo

If the chat session does not expose a direct `image_generate` tool, test the provider by importing the plugin:

```bash
XAI_IMAGE_MODEL=grok-imagine-image-quality python - <<'PY'
import sys, json
sys.path.insert(0, 'D:/Hermes/hermes-agent')
from plugins.image_gen.xai import XAIImageGenProvider

prompt = 'Premium editorial poster, dark cinematic lighting, neon green accents, a clear simple subject.'
res = XAIImageGenProvider().generate(prompt, aspect_ratio='portrait')
print(json.dumps(res, ensure_ascii=False, indent=2))
PY
```

Expected success response includes:

```json
{
  "success": true,
  "image": "https://... or local path",
  "model": "grok-imagine-image-quality",
  "provider": "xai",
  "resolution": "1k"
}
```

## Output handling

- xAI may return a reusable `public_url` when Hermes xAI Imagine storage is enabled.
- Storage-enabled responses can include a notice that xAI may bill for stored files/public URL hosting.
- If public storage is not enabled, Hermes provider code may cache returned image bytes/URLs locally to avoid ephemeral xAI temp URLs expiring before delivery.

## Agência Sem Esforço prompt pattern

A successful concept prompt for the brand can combine:

- mythic/manual-effort metaphor, e.g. Sisyphus pushing a boulder;
- explicit reversal: automation/robotic arms/AI holds or removes the burden;
- sign text: `É PROIBIDO SE ESFORÇAR` or `PROIBIDO SE ESFORÇAR`;
- visual mood: premium editorial, cinematic, dark volcanic mountain, neon green highlights `#A3F12E`;
- composition: one modern entrepreneur, one boulder, one prohibition sign, no clutter;
- constraints: no slide numbers, no extra text beyond the sign and optional subtle brand mark.

Always visually inspect the generated image because in-image Portuguese text can be misspelled or omit accents.
