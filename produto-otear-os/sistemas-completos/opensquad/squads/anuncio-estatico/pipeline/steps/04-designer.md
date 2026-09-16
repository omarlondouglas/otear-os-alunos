---
execution: inline
agent: designer
inputFile: squads/anuncio-estatico/output/ad-copy.md
outputFile: squads/anuncio-estatico/output/ad-image.html
---

# Step 04: Design do Criativo Estático

## Context Loading

Load these files before executing:
- `squads/anuncio-estatico/output/ad-copy.md` — Copy aprovada com direção visual
- `squads/noticias-carrossel-ia/agents/design-system.md` — Design system da marca Marlon Lima
- `squads/anuncio-estatico/pipeline/data/quality-criteria.md` — Critérios de qualidade de design
- `squads/anuncio-estatico/pipeline/data/anti-patterns.md` — Erros de design a evitar
- `_opensquad/_memory/company.md` — Contexto da empresa

## Instructions

### Process
1. Ler a copy aprovada e a direção visual sugerida pelo copywriter
2. Carregar o design system da marca (cores, fontes, espaçamento)
3. Definir o layout do anúncio 1080x1080:
   - Posição da headline (topo ou centro)
   - Posição do corpo (centro)
   - Posição do CTA (base, pill verde neon)
   - Posição do branding (@marlonlima.ia)
4. Criar HTML/CSS auto-contido seguindo o design system
5. Aplicar destaques visuais conforme direção visual (cores, negrito, tamanho)
6. Renderizar com Playwright (1080x1080) e verificar visualmente
7. Ajustar se necessário até passar no teste de 3 segundos

## Output Format

Um arquivo HTML auto-contido com:
- Body: 1080x1080, margin: 0, padding: 0, overflow: hidden
- Fonte: Urbanist via Google Fonts @import
- Cores: paleta da marca (#0a0a0a, #A3F12E, #ffffff, etc.)
- Headline: min 58px bold
- Corpo: min 34px regular
- CTA: pill com fundo #A3F12E e texto #0a0a0a
- Branding: @marlonlima.ia no canto inferior

## Output Example

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    width: 1080px; height: 1080px;
    background: #0a0a0a;
    font-family: 'Urbanist', sans-serif;
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    padding: 80px; overflow: hidden;
  }
  .headline {
    font-size: 64px; font-weight: 800;
    color: #ffffff; text-align: center;
    line-height: 1.15; margin-bottom: 40px;
  }
  .headline .highlight { color: #A3F12E; }
  .body-text {
    font-size: 34px; font-weight: 500;
    color: #cccccc; text-align: center;
    line-height: 1.5; margin-bottom: 48px;
  }
  .cta {
    background: #A3F12E; color: #0a0a0a;
    font-size: 36px; font-weight: 700;
    padding: 20px 48px; border-radius: 50px;
  }
  .branding {
    position: absolute; bottom: 32px; right: 40px;
    color: #666666; font-size: 24px; font-weight: 500;
  }
</style>
</head>
<body>
  <div class="headline"><span class="highlight">12</span> agentes de IA<br>prontos em <span class="highlight">8 semanas</span></div>
  <div class="body-text">Sem programação. Suporte ao vivo.<br>SDR, atendimento, follow-up e mais.</div>
  <div class="cta">Garanta sua vaga →</div>
  <div class="branding">@marlonlima.ia</div>
</body>
</html>
```

## Veto Conditions

1. Qualquer texto com fonte menor que 24px
2. CTA sem contraste suficiente (não se destaca do fundo)
3. HTML não é auto-contido (usa recursos externos além de Google Fonts)
4. Dimensões diferentes de 1080x1080

## Quality Criteria

- [ ] Body 1080x1080 com margin: 0, overflow: hidden
- [ ] Fonte Urbanist carregada via @import
- [ ] Headline min 58px, corpo min 34px
- [ ] CTA em pill verde neon, destaque máximo
- [ ] Branding @marlonlima.ia presente
- [ ] HTML auto-contido (sem JS, sem CDN além de Google Fonts)
- [ ] Legível em 3 segundos
