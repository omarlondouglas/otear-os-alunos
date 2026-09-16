# Design System — Marca Marlon Lima

## Cores

```
--background:     #0a0a0a   /* Fundo principal */
--surface:        #1a1a1a   /* Cards, containers */
--surface-border: #2a2a2a   /* Bordas */
--primary:        #A3F12E   /* Verde neon — CTAs, destaques principais */
--primary-dark:   #7bc91a   /* Variante escura do primary */
--blue-accent:    #4B8DF6   /* Azul — informações, links */
--red-accent:     #EF4444   /* Vermelho — alertas */
--gold:           #FFD700   /* Dourado — avaliações, destaque */
--text-primary:   #ffffff
--text-secondary: #cccccc
--text-tertiary:  #888888
--text-muted:     #666666
```

## Tipografia

Fonte: **Urbanist** (Google Fonts)
Import: `https://fonts.googleapis.com/css2?family=Urbanist:wght@300;400;500;600;700;800&display=swap`

Escala (web) → Adaptação Instagram (1080x1440):
- Display: 64px/800 → **72px/800** para Instagram hero
- H1: 48px/700 → **58px/700** para Instagram heading
- H2: 32px/600 → **44px/600** para Instagram subheading
- Body: 16px/400 → **34px/500** para Instagram body
- Small: 14px/400-500 → **26px/500** para Instagram small
- Caption: 12px/400 → **24px/400** para Instagram caption

## Cards

```
background: #1a1a1a
border-radius: 16px
padding: 28px
border: 1px solid #2a2a2a
```

## Botões/Pills

```
border-radius: 50px (full)
primary: background #A3F12E, color #0a0a0a
```

## Border Radius

- sm: 8px | md: 12px | lg: 16px | xl: 20px | full: 50px

## Espaçamento Base

- xs: 8px | sm: 12px | md: 16px | lg: 24px | xl: 32px | 2xl: 40px | 3xl: 60px

## Layout de Slides com Imagem (Referencia @brandsdecoded__)

Quando o carrossel incluir imagens (fotos reais ou IA), seguir este layout:

### Estrutura por Slide (3 zonas verticais)
1. **Zona superior (~40%)**: Headline bold grande
2. **Zona central (~35%)**: Foto/imagem editorial com object-fit: cover
3. **Zona inferior (~25%)**: Texto explicativo/analitico

### Header Fixo (todos os slides)
- Posicao: Topo, full-width
- 3 colunas: "Powered by [nome do produto]" | "@marlonlima.ia" | "2026 //"
- Fonte: caption size, text-muted

### Imagens
- Posicao: centralizada, ocupando ~35% da altura do slide
- border-radius: 12px
- Se a imagem for escura, nao precisa de overlay
- Se a imagem for clara, aplicar um leve overlay escuro para nao competir com texto

### Highlight de Texto
- Frases-chave destacadas com background primary (#A3F12E) como "marca-texto"
- Padding: 4px 8px no highlight
- Cria contraste visual e guia o olho

### Alternancia de Fundos
- Slides escuros: #0a0a0a
- Slides claros: #F5F5F0
- Slides de destaque: primary (#A3F12E) com texto #0a0a0a
