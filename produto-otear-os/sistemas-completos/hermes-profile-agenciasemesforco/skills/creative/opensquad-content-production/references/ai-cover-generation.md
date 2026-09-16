# OpenSquad `noticias-carrossel-ia` AI cover path

Use this when a carousel needs the squad’s designed/AI-generated cover rather than a text-only fallback.

## Key lesson

Do not jump straight to fallback PNG slides just because the local renderer/dashboard is down. The cover image generation path can still work independently through Gemini if `GEMINI_API_KEY` is configured.

## Current checkpoint mapping

From `squads/noticias-carrossel-ia/pipeline/steps/04b-checkpoint-imagens.md`:

- Option 1: use image bank/R2.
- Option 2: generate with IA/Gemini.
- Option 3: no images/text-only.

If a helper script such as `run-local.bat` says “opcao 1 (Sem imagens...)”, treat it as stale and patch/override it to match the pipeline.

## Minimal manual workflow

1. Write `visual-concept.md` into the run output directory.
2. Make the cover prompt follow the squad direction from `agents/conceituador-visual.agent.md`:
   - intaglio engraving protagonist, fine parallel lines, cross-hatching, black/white engraved character;
   - modern colorful digital/news elements around it;
   - high contrast and enough negative space for headline overlay;
   - no readable text/logos/watermarks in the generated image.
3. Call Gemini image generation with `gemini-2.5-flash-image:generateContent` and `generationConfig.responseModalities = ["TEXT", "IMAGE"]`.
4. Decode the `inlineData.data` image and save it as `images/img-slide-01-ai-cover.png`.
5. Write/update `image-brief.md` with `Slide 1: images/img-slide-01-ai-cover.png — ...` and null for slides without image.
6. Update `slides-data.json` slide 1:
   - `theme: "black"`
   - `imageFile: "images/img-slide-01-ai-cover.png"`
   - keep the text elements concise so the image can carry the visual impact.
7. If the renderer is unavailable, create a temporary composite preview from the generated cover with dark gradient overlay + readable headline; label it as a fallback preview, not the full OpenSquad renderer output.

## Verification

- Confirm generated image is non-zero bytes and visually inspect it.
- Inspect the final cover/contact sheet before delivery.
- If the user complains about design quality, prioritize running/regenerating the IA cover path before explaining limitations.
