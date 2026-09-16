# Design System â€” Marca Marlon Lima

## Cores

```
--background:     #0a0a0a   /* Fundo principal */
--surface:        #1a1a1a   /* Cards, containers */
--surface-border: #2a2a2a   /* Bordas */
--primary:        #A3F12E   /* Verde neon â€” CTAs, destaques principais */
--primary-dark:   #7bc91a   /* Variante escura do primary */
--blue-accent:    #4B8DF6   /* Azul â€” informaÃ§Ãµes, links */
--red-accent:     #EF4444   /* Vermelho â€” alertas */
--gold:           #FFD700   /* Dourado â€” avaliaÃ§Ãµes, destaque */
--text-primary:   #ffffff
--text-secondary: #cccccc
--text-tertiary:  #888888
--text-muted:     #666666
```

## Tipografia

Fonte: **Urbanist** (Google Fonts)
Import: `https://fonts.googleapis.com/css2?family=Urbanist:wght@300;400;500;600;700;800&display=swap`

Escala (web) â†’ AdaptaÃ§Ã£o Instagram (1080x1440):
- Display: 64px/800 â†’ **72px/800** para Instagram hero
- H1: 48px/700 â†’ **58px/700** para Instagram heading
- H2: 32px/600 â†’ **44px/600** para Instagram subheading
- Body: 16px/400 â†’ **34px/500** para Instagram body
- Small: 14px/400-500 â†’ **26px/500** para Instagram small
- Caption: 12px/400 â†’ **24px/400** para Instagram caption

## Cards

```
background: #1a1a1a
border-radius: 16px
padding: 28px
border: 1px solid #2a2a2a
```

## BotÃµes/Pills

```
border-radius: 50px (full)
primary: background #A3F12E, color #0a0a0a
```

## Border Radius

- sm: 8px | md: 12px | lg: 16px | xl: 20px | full: 50px

## EspaÃ§amento Base

- xs: 8px | sm: 12px | md: 16px | lg: 24px | xl: 32px | 2xl: 40px | 3xl: 60px

## ReferÃªncia Visual ObrigatÃ³ria â€” @brandsdecoded__ adaptado para Marlon

Existe uma anÃ¡lise local do perfil em:
`{OTEAR_SO_ROOT}/referencias/opensquad/_opensquad/_memory/reference-profiles/brandsdecoded__/design-analysis.md`

Antes de criar qualquer carrossel de notÃ­cia, use essa anÃ¡lise como referÃªncia de
estrutura, hierarquia e ritmo editorial. A regra nÃ£o Ã© copiar a identidade
laranja do @brandsdecoded__; Ã© replicar as caracterÃ­sticas de retenÃ§Ã£o:

- leitura instantÃ¢nea no feed;
- capa com tensÃ£o visual forte;
- header fixo discreto;
- conteÃºdo jornalÃ­stico/analÃ­tico;
- narrativa em camadas, slide por slide;
- fotos ou imagens editoriais contextuais, nunca stock genÃ©rico.

## Layout de Slides com Imagem (referÃªncia @brandsdecoded__)

Quando o carrossel incluir imagens (fotos reais ou IA), seguir este layout:

### Estrutura por Slide (3 zonas verticais)
1. **Zona superior (~40%)**: headline editorial bold grande, 2-4 linhas.
2. **Zona central (~35%)**: foto/imagem contextual editorial com object-fit: cover.
3. **Zona inferior (~25%)**: texto explicativo/analÃ­tico curto, com evidÃªncia ou consequÃªncia.

### Header Fixo (todos os slides)
- PosiÃ§Ã£o: topo, full-width.
- 3 colunas: `Powered by O Tear` | `@marlonlima.ia` | `2026 //`.
- Fonte: caption size, text-muted, tracking discreto.
- NÃ£o usar header grande; ele deve parecer assinatura editorial.

### Imagens
- Capa: rosto humano/protagonista dominante, fundo escuro, expressÃ£o forte, contraste alto.
- Slides internos: imagem contextual no centro, ocupando ~35% da altura.
- Preferir foto real/editorial quando houver pessoa, marca, produto ou evento real.
- Usar IA quando nÃ£o houver ativo real adequado ou quando o tema for abstrato.
- Border-radius: 12px em imagens internas; capa pode ocupar fundo inteiro.
- Se a imagem for clara, aplicar leve overlay escuro para nÃ£o competir com texto.
- Nunca usar: handshake, escritÃ³rio genÃ©rico, robÃ´ clichÃª, pessoas sorrindo para notebook sem relaÃ§Ã£o com a notÃ­cia.

### Highlight de Texto
- Frases-chave destacadas com background primary (#A3F12E) como marca-texto.
- Padding: 4px 8px no highlight.
- Usar highlight para tensÃ£o, nÃºmero, nome de marca ou consequÃªncia.
- NÃ£o destacar palavras aleatÃ³rias.

### AlternÃ¢ncia de Fundos
- Slides escuros: #0a0a0a / #0D0D0D.
- Slides claros: #F5F5F0.
- Slides de destaque: primary (#A3F12E) com texto #0a0a0a.
- Alternar para criar ritmo: escuro â†’ claro â†’ escuro â†’ acento, sem repetir 3 fundos iguais seguidos.

## Estrutura Editorial BrandsDecoded

- Tom: analÃ­tico, jornalÃ­stico, sofisticado e acessÃ­vel.
- Cada slide deve ter uma afirmaÃ§Ã£o forte + contexto/evidÃªncia + consequÃªncia.
- Priorizar cases reais, nÃºmeros, datas, marcas, pessoas e conflitos.
- A capa vende curiosidade; os slides entregam a explicaÃ§Ã£o.
- Slide final fecha com uma conclusÃ£o forte ou pergunta provocativa, nÃ£o com CTA genÃ©rico de venda.
- Limite por slide: headline de 15-25 palavras; apoio de 30-50 palavras; mÃ¡ximo absoluto ~75 palavras.
