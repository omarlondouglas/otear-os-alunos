---
name: image-generation-providers
description: "Use when generating/testing images via Hermes providers."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [image-generation, xai, grok-imagine, hermes-tools, creative]
---

# Image Generation Providers

## When to Use

Use this skill when the user asks to test an image provider connection, generate a one-off image through Hermes, configure provider-specific image generation, or turn a creative concept into a provider-ready prompt.

## Core workflow

1. **Confirm the active provider path** when needed: Hermes image generation is routed through `image_gen.provider` and provider-specific config/env/OAuth.
2. **Write the creative prompt first**, with:
   - subject and visual metaphor;
   - brand/context;
   - composition and mood;
   - style references and palette;
   - explicit text constraints if the image must contain words;
   - negative constraints such as `no slide numbers`, `no clutter`, or `no extra text`.
3. **Run a real provider call** rather than only describing the prompt when the user asks to test generation.
4. **Verify the output visually** before reporting success. Check whether the required visual elements actually appeared and whether any text was misspelled.
5. **Return both artifact and prompt** so the user can reuse or refine it.

## Hermes direct-provider probe pattern

When the normal `image_generate` tool surface is not directly available in the current tool list, a Hermes image provider can be smoke-tested from the repo with Python by importing its provider class and calling `generate()` directly.

For xAI/Grok Imagine, see `references/xai-grok-imagine.md`.

## Prompting notes

- For Agência Sem Esforço concepts, imagery should connect automation/AI to margin, freedom from operations, and reduced manual effort — not generic replacement fear.
- Use premium dark/editorial aesthetics when appropriate: high contrast, black/charcoal background, controlled neon green highlights, cinematic lighting.
- For public-facing Agência Sem Esforço material, avoid internal engine names and keep the brand visible only when it improves the composition.
- If the concept includes a sign/poster/text in-image, keep the text short and uppercase. Portuguese text should be checked visually because image models may misspell accents or words.

## Verification checklist

- [ ] Provider credentials are available or OAuth works.
- [ ] The provider returned `success: true` or an equivalent successful response.
- [ ] A stable URL or local image path was returned.
- [ ] The image was inspected visually.
- [ ] The final answer includes the generated image/link and the exact prompt used.
