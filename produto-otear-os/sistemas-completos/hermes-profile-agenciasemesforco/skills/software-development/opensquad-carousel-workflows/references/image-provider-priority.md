# Image Provider Priority for OpenSquad Carousels

Use when the user asks why a carousel is using Gemini instead of Codex/ChatGPT image generation, or when improving the `noticias-carrossel-ia` image generation flow.

## Preferred order

1. **Codex/ChatGPT Image 2** via `CHATGPT_BRIDGE_URL` / `gpt-image-2`.
2. **OpenAI Images API** via `OPENAI_API_KEY`.
3. **Google Gemini/Imagen** via `GEMINI_API_KEY` or `GOOGLE_API_KEY`.

Do not silently use Gemini first if the user expects â€œImage 2 do Codex/ChatGPT.â€ If the preferred provider is not configured, report that explicitly and state the fallback.

Suggested status line:

```txt
gpt-image-2 indisponÃ­vel: CHATGPT_BRIDGE_URL ausente; usando fallback Gemini.
```

## Where this showed up

In the userâ€™s codebases, the older OpenSquad `noticias-carrossel-ia` pipeline had its generator step hardcoded to Gemini, while `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes/app/agents/agno_tools.py` already had a more capable `generate_image_tool` pattern:

```txt
chatgpt-bridge/gpt-image-2 -> OpenAI Images -> Google Gemini/Imagen
```

When updating OpenSquad, patch both:

- `squads/noticias-carrossel-ia/agents/gerador-imagens.agent.md`
- `squads/noticias-carrossel-ia/pipeline/steps/*gerador-imagens.md`

If a runner script drives checkpoint answers, also check it for mismatches (for example, sending â€œsem imagensâ€ while the user expects generated cover art).

## Durable warning

Do not encode â€œGemini is wrongâ€ as a blanket rule. Gemini is a valid fallback. The durable lesson is provider order and transparency: prefer the userâ€™s requested provider when configured, otherwise say which fallback is being used.
