---
task: "Create Ad Image"
order: 1
input: |
  - ad-copy.md: Copy aprovada com headline, corpo, CTA e direção visual
  - design-system.md: Cores, fontes e espaçamento da marca
output: |
  - ad-image.html: Arquivo HTML auto-contido 1080x1080
---

# Create Ad Image

Transforma a copy aprovada em um criativo estático de 1080x1080 usando HTML/CSS auto-contido, seguindo o design system da marca e a direção visual do copywriter.

## Process

1. **Carregar design system**: Ler design-system.md da marca. Definir variáveis: cores (#0a0a0a, #A3F12E, #ffffff, etc.), fonte (Urbanist), espaçamento base.
2. **Ler copy e direção visual**: Extrair headline, corpo, CTA, destaques sugeridos e layout.
3. **Definir layout**: Posicionar headline (topo/centro), corpo (centro), CTA (base), branding (canto inferior). Usar Flexbox com flex-direction: column.
4. **Criar HTML/CSS**: Escrever arquivo auto-contido. Body: 1080x1080, margin: 0, overflow: hidden. Google Fonts @import para Urbanist. Aplicar destaques visuais (cor, bold, tamanho) conforme direção visual.
5. **Renderizar**: Usar Playwright para navegar ao HTML e tirar screenshot em 1080x1080.
6. **Verificar**: Ler o screenshot. Confirmar: texto legível em 3s, CTA visível, branding presente, contraste OK.
7. **Iterar se necessário**: Se algum problema, ajustar HTML e re-renderizar.

## Output Format

```yaml
type: html
viewport: "1080x1080"
font: "Urbanist"
colors:
  background: "#0a0a0a"
  primary: "#A3F12E"
  text: "#ffffff"
branding: "@marlonlima.ia"
```

## Output Example

> Use as quality reference, not as rigid template.

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
    position: relative;
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
    display: inline-block;
  }
  .branding {
    position: absolute; bottom: 32px; right: 40px;
    color: #666666; font-size: 24px; font-weight: 500;
  }
</style>
</head>
<body>
  <div class="headline">
    <span class="highlight">12</span> agentes de IA<br>
    prontos em <span class="highlight">8 semanas</span>
  </div>
  <div class="body-text">
    Sem programacao. Suporte ao vivo.<br>
    SDR, atendimento, follow-up e mais.
  </div>
  <div class="cta">Garanta sua vaga →</div>
  <div class="branding">@marlonlima.ia</div>
</body>
</html>
```

## Quality Criteria

- [ ] Body exatamente 1080x1080
- [ ] Fonte Urbanist carregada via @import
- [ ] Headline min 58px bold, corpo min 34px
- [ ] CTA em pill #A3F12E com texto #0a0a0a
- [ ] @marlonlima.ia presente
- [ ] HTML auto-contido (sem JS, sem CDN extra)
- [ ] Renderizado e verificado visualmente via Playwright

## Veto Conditions

Reject and redo if ANY are true:
1. Qualquer texto com fonte menor que 24px
2. HTML nao e auto-contido (usa recursos externos alem de Google Fonts)
