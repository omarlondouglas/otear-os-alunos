# Squad Memory — yt-thumbnails

## Run 2026-04-05

### Preferências do Usuário
- Marlon prefere thumbnails com SUA FOTO REAL + contexto no fundo
- Estilo preferido: cinematográfico (iluminação dramática, premium)
- Quer reação/expressão no rosto, não postura neutra
- Foto referência: D:\imagens\eu.png (cabelo cacheado escuro, pele morena, gola alta preta)
- Prefere texto ("DIA 01") já renderizado na imagem pela IA, não em pós-produção

### Decisões
- Conceito aprovado: close-up com reação + monitores no fundo
- Palette: âmbar/dourado (#D4920B) + navy (#0a1628) + azul monitor (#2196F3)
- Fonte para texto: sans-serif bold branco (gerado pela IA direto na imagem)

### Aprendizados Técnicos — Geração de Imagem

#### Gemini 2.5 Flash Image
- SEMPRE gera imagem quadrada (1:1) — não aceita aspectRatio como parâmetro
- ACEITA imagem de referência via inlineData (base64 no payload)
- Com foto de referência, a semelhança facial melhora dramaticamente
- Renderiza texto curto (2-3 palavras) com boa qualidade
- Modelo: gemini-2.5-flash-image (endpoint generateContent)

#### Imagen 4.0
- SUPORTA aspectRatio: "16:9" via endpoint /predict
- NÃO aceita imagem de referência — só prompt de texto
- Gera rostos mais estilizados/cartoon que o Gemini
- Bom para backgrounds e composições, menos para semelhança facial
- Modelo: imagen-4.0-generate-001

#### Workflow Ideal (descoberto nesta run)
1. Gerar com Gemini + foto de referência (melhor semelhança) — SEM texto no prompt ("DO NOT include any text")
2. Playwright faz TUDO: composição 16:9 com 4 camadas:
   - Camada 1 (bg): mesma imagem com object-fit:cover + blur(25px) + scale(1.15) + brightness(0.75) = fundo estendido sem barras pretas
   - Camada 2 (sharp): imagem nítida com mask-image fade-to-left para transição suave
   - Camada 3 (gradient): gradiente escuro na esquerda para legibilidade do texto
   - Camada 4 (text): Montserrat 900, branco, text-shadow
   - Filtro de cor: saturate(1.35) contrast(1.08) brightness(1.05) na imagem nítida
   - NUNCA usar barras pretas ou cor sólida para preencher — SEMPRE blur da mesma imagem
3. Texto via HTML: fonte Montserrat 900, cor branca, text-shadow, acentos corretos garantidos

#### Playwright como ferramenta de resize
- Criar HTML com img { width: 1280px; height: 720px; object-fit: cover; object-position: center 25% }
- O object-position: center 25% preserva o rosto inteiro (do cabelo ao peito). SEM isso, corta o queixo/boca
- Cor aprovada pelo Marlon: filter: saturate(1.35) contrast(1.08) brightness(1.05) — SEM hue-rotate
- Referência de cor ideal: thumbnail-final-1280x720.png da run "empresa"
- Marlon tem pele morena vibrante, a IA tende a clarear. Sempre aplicar esse filtro
- Servir via http-server (file:// protocol é bloqueado)
- Viewport 1280x720 + screenshot = thumbnail no formato correto

#### Fundo contextual por tema
- O fundo da thumbnail DEVE refletir o tema do vídeo, não repetir o mesmo cenário genérico
- Exemplo: "empresa de 1 homem só" = escritório vazio com mesas desocupadas
- Cada thumbnail é uma mini-história visual — o fundo é parte da narrativa

### Problemas Encontrados
- Subagents (haiku e outros) não tiveram permissão para WebSearch/WebFetch/Playwright
- Tive que fazer pesquisa e geração inline em vez de delegar
- file:// protocol bloqueado no Playwright — precisa http-server local

### Para Próximos Episódios
- Manter mesma palette âmbar/navy para identidade visual da série
- Trocar "DIA 01" por "DIA 02", "DIA 03" etc.
- Usar mesmo workflow: Gemini + foto referência → Playwright resize
- Foto de referência fixa salva em: squads/yt-thumbnails/pipeline/data/reference-photo.png
- Usar SEMPRE essa foto como inlineData no Gemini para todas as runs
