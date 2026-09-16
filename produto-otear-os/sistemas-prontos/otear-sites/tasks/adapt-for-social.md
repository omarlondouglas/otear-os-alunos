---
task: adaptForSocial()
responsavel: "SocialAdapter"
responsavel_type: Agente
atomic_layer: Organism
elicit: false

Entrada:
  - campo: longFormContent
    tipo: file
    origen: "writeLongForm() â€” conteÃºdo original"
    obrigatorio: true
  - campo: platforms
    tipo: array
    origen: "content-strategist ou UsuÃ¡rio â€” instagram, linkedin, twitter, tiktok"
    obrigatorio: false

Saida:
  - campo: socialPosts
    tipo: array
    destino: "publishing-scheduler, image-brief-generator"
    persistido: true
  - campo: platformVariations
    tipo: object
    destino: "publishing-scheduler"
    persistido: true

Checklist:
  pre-conditions:
    - "[ ] ConteÃºdo longo disponÃ­vel"
    - "[ ] Ao menos uma plataforma alvo"
  post-conditions:
    - "[ ] Posts adaptados para cada plataforma"
    - "[ ] Hooks e hashtags incluÃ­dos"
    - "[ ] Formatos especÃ­ficos respeitados"
  acceptance-criteria:
    - blocker: true
      criteria: "Post adaptado para ao menos 2 plataformas"
    - blocker: true
      criteria: "Limites de caracteres respeitados por plataforma"
    - blocker: false
      criteria: "VariaÃ§Ãµes A/B para teste"

Performance:
  duration_expected: "10-20 minutos"
  cost_estimated: "~0 (adaptaÃ§Ã£o de conteÃºdo)"
  cacheable: false
  parallelizable: true

Error Handling:
  strategy: retry
  retry:
    max_attempts: 2
    delay: "exponential(base=5s, max=30s)"
  fallback: "Se conteÃºdo longo indisponÃ­vel, adaptar a partir do briefing do strategist"
  notification: "social-media-adapter"

Metadata:
  version: "1.0.0"
  dependencies: []
  author: "content-factory-squad"
  created_at: "2026-02-24T00:00:00Z"
---

# Adapt For Social

## Flow

```
1. Receber conteÃºdo longo do long-form-writer
2. Identificar pontos-chave e quotes impactantes
3. Adaptar para LinkedIn (post profissional com dados)
4. Adaptar para Instagram (carrossel/caption visual)
5. Adaptar para Twitter/X (thread concisa e impactante)
6. Adaptar para TikTok (script com hook nos primeiros 3s)
7. Adicionar hashtags e CTAs especÃ­ficos por plataforma
8. Gerar variaÃ§Ãµes A/B para teste de performance
9. Enviar para publishing-scheduler e image-brief-generator
```

## Elicitation

- "Qual o conteÃºdo original a ser adaptado?"
- "Para quais plataformas deseja adaptar? (Instagram, LinkedIn, Twitter/X, TikTok)"
- "HÃ¡ tom ou estilo especÃ­fico para alguma plataforma?"
- "Deseja variaÃ§Ãµes A/B para teste?"

