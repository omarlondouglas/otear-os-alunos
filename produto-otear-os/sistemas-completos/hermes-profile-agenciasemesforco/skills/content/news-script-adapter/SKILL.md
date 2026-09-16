---
name: news-script-adapter
description: "Transforma notícia, manchete, briefing ou artigo em roteiro curto para TikTok/Reels/Shorts usando padrões de hook, desenvolvimento, gatilhos, edição de tela e estilo de fala inspirados em creators analisados no projeto."
version: 1.1.0
author: O Tear
license: MIT
metadata:
  hermes:
    tags: [otear, news, script, tiktok, reels, shorts]
---

# news-script-adapter

## When to Use

Use esta skill quando o cliente:
- mandar uma notícia e quiser transformar em roteiro
- pedir adaptação para TikTok, Reels ou Shorts
- quiser separar `hook`, `desenvolvimento`, `gatilho`, `edição/tela` e `delivery`
- quiser versões em estilos diferentes de creators
- quiser criar **hooks/ganchos isolados** (sem script completo) para uma série de conteúdo
- quiser um **formato de série recorrente** — ex: "Esse é um novo começo para [tema]"
- quiser salvar o roteiro pronto no ClickUp como task
- quiser **conteúdo de storytelling pessoal** baseado na história do próprio cliente (não notícia)
- quiser **tom pessoal e autêntico**, sem gatilhos genéricos de IA
- **receber uma lista de leads e quiser enviar mensagens de WhatsApp em lote** → ver `references/prospeccao-whatsapp-pipeline.md`
## Archetypes Disponíveis

Leia `references/creator-patterns.md` quando precisar da análise completa.

- `v_daily_journal` -> boletim factual, rotina, clareza
- `dylan_page` -> breaking news, urgência, crise
- `rpn` -> oportunidade prática, ferramenta, leverage
- `gabrieladamuchi` -> ruptura, obsolescência, monetização
- `gigaqian` -> explicação técnica com metáfora
- `dr_cintas` -> roundup comprimido, muita informação
- `kanekallaway` -> futuro, surpresa, mudança de paradigma

## Content Series Format: "Esse é um novo começo"

Um formato recorrente que inverte o medo da IA: em vez de "IA vai te substituir" (ameaça), o ângulo é **"isso é um novo começo"** (esperança + ação acionável).

### Estrutura do hook padrão
- **Frase-tipo:** "Se você [situação de medo/dor]... calma. Isso não é o fim de [X]. É o começo de um novo [Y]."
- **Trigger:** Obsolescência → Oportunidade
- **Arquétipo:** gabrieladamuchi (abertura) + rpn (desenvolvimento) + kanekallaway (fechamento)
- **Desenvolvimento:** Mostra que a IA elimina a parte burocrática — o que sobra é o que realmente importa (estratégia, conexão humana, julgamento, criatividade)
- **Profissão-agnóstico:** O hook funciona sem profissão específica; a profissão entra no desenvolvimento

### Quando este formato se aplica
- O cliente pedir conteúdo sobre IA sem notícia específica
- O cliente quiser criar uma **semana temática** (ex: 5 dias, 5 profissões)
- Conteúdo de posicionamento (não factual/noticioso)
- Resposta ao medo do público sobre substituição por IA

### Hook-Only Output (alternativa ao Output Padrão)

Use quando o cliente pedir **apenas hooks/templates**, sem script completo ou profissão específica:

```md
## Hook (completo)
## Trigger
## Quando usar (que público/dor atinge)
## Variação curta (15s)
## Edição de tela
```

Cada hook vira uma task separada no ClickUp (ver seção Workflow Integration > Hook Templates).

Leia `references/hook-templates-novo-comeco.md` para o banco de hooks prontos.

## Data Sources

### Primária: Supabase (O Tear CRM)

As notícias e temas vêm do Supabase. Consulte `references/supabase-tables.md` para os detalhes de cada tabela, colunas e fluxo.

Tabelas disponíveis: `noticias`, `noticias_perplexity`, `posts_do_reddit`, `videos_do_youtube`, `ideias_de_conteudo`.

**⚠️ Schema mudou:** As tabelas têm colunas diferentes do que a documentação original descrevia. Sempre consulte `references/supabase-tables.md` antes de montar queries. Em caso de 400, teste sem `order` primeiro (`?limit=3`) para ver o retorno cru.

**Padrão recomendado — use o script pronto (NÃO pipe curl→python):**
```bash
python3 ~/.hermes/skills/content/news-script-adapter/scripts/query_supabase.py noticias 10
python3 ~/.hermes/skills/content/news-script-adapter/scripts/query_supabase.py videos_do_youtube 10
```

**NUNCA** use `curl ... | python3 -c "..."` — chaves JWT quebram o quoting do shell e pipes causam timeout/block. Use Python com `urllib` ou salve em arquivo primeiro.

Ordem de preferência: notícias recentes → verificar se já foram roteirizadas → puxar da tabela mais relevante ao tema pedido.

### Fallback 1: News API (newsapi.org)

Se o Supabase retornar tabelas VAZIAS, use a News API. Consulte `references/news-api.md` para detalhes completos, queries e limitações.

**Padrão rápido:**
```bash
# Tech headlines (funciona no free tier)
curl -s --max-time 20 "https://newsapi.org/v2/top-headlines?apiKey=4102fa76d3e6430b893bc272c6225fb3&category=technology&pageSize=10" > /tmp/news.json

# Específico (queries com nomes próprios)
curl -s --max-time 20 "https://newsapi.org/v2/everything?apiKey=4102fa76d3e6430b893bc272c6225fb3&q=OpenAI+OR+Anthropic+OR+Google+DeepMind+OR+DeepSeek&sortBy=publishedAt&pageSize=10" > /tmp/news.json
### Fallback 1: News API

Quando o Supabase estiver vazio ou inacessível, use a **News API**. Consulte `references/news-api-guide.md` para endpoints, queries que funcionam e padrão de código.

**Chave:** `NEWS_API_KEY=4102fa76d3e6430b893bc272c6225fb3`

Recomendação: use `top-headlines` para busca geral e `everything` com queries OR específicas para temas de IA. Se `articles` voltar vazio mas `totalResults > 0`, refaça a query com termos mais específicos.

### Fallback 2: Hacker News (deprecated — use News API primeiro)

Quando News API não bastar:
```
curl -s "https://hn.algolia.com/api/v1/search?query=AI+OR+LLM+OR+agent+OR+artificial+intelligence&tags=story&hitsPerPage=30"
curl -s "https://hn.algolia.com/api/v1/search?query=OpenAI+OR+Anthropic+OR+Google+AI+OR+DeepSeek&tags=story&hitsPerPage=20"
curl -s "https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=50"
```

Regras de filtragem:
- Filtrar por data >= últimos 30 dias (campo created_at)
- Priorizar stories com 10+ pontos
- Remover duplicatas por título
- Manter apenas temas conectáveis a IA para negócios

### Fallback 3: Fontes específicas de AI/business

Quando HN Algolia não bastar: anthropic.com/news, OpenAI blog, TechCrunch AI, The Register AI/ML, links das stories do HN.

### Quando NÃO usar fallback

Se Supabase retornar 401 (chave expirada) — avise o usuário, não prossiga sem autorização.

## Procedure

1. Extraia os fatos centrais da notícia da fonte adequada (ver **Data Sources** acima).
   - Se Supabase tiver dados, use as tabelas (via script `scripts/query_supabase.py`).
   - Se Supabase estiver vazio, use os fallbacks de AI/business.
   - **Nunca** busque trending topics genéricos sem filtrar por IA/tech.
2. Se estiver em dúvida entre vários temas, priorize o que tiver conexão mais forte com IA para negócios — esse é o tema fixo do cliente.
3. Escolha o ângulo principal:
   - urgência
   - ameaça
   - oportunidade
   - ruptura
   - explicação
   - futuro
4. Escolha o primeiro gatilho emocional.
5. Escolha o arquétipo mais adequado.
6. Escreva o roteiro no formato abaixo.
7. Salvar no ClickUp: criar task na lista Tiktok com status `concept`, nome descritivo, script completo no body e tags relevantes (ver seção Workflow Integration).

## Output Padrão

```md
## Angle
## Theme
## Primary Trigger
## Script
Hook:
Development:
Closing:
## On-Screen Editing
## Delivery Notes
```

## Drafting Rules

- O hook aparece nas 1-2 primeiras frases.
- Não explique antes de criar interesse.
- O desenvolvimento precisa avançar a história ou esclarecer implicações.
- As instruções de tela devem apoiar o entendimento: headline, screenshots, mapa, gráfico, lista numerada, facecam, demo.
- Para notícia técnica, explique por que importa antes de aprofundar.
- Para crise, priorize status atual e consequência.
- Para IA/negócios, enfatize leverage, obsolescência ou vantagem competitiva.

## Default Blend

Se o cliente disser apenas "adapte com esses fundamentos", use:
- tensão de abertura de `dylan_page` ou `gabrieladamuchi`
- clareza de explicação de `gigaqian`
- consequência prática de `rpn`
- compressão de `dr_cintas`
- framing de futuro de `kanekallaway`
- disciplina factual de `v_daily_journal`

## Storytelling Mode (Conteúdo de Marca Pessoal)

Use quando o cliente quiser criar roteiros baseados na **própria história, valores e visão de mundo** — não em notícias externas. O objetivo é autenticidade e conexão, não viralização por factual.

Leia `references/marlon-brand-guide.md` antes de escrever — contém história, golden circle, valores e ICP completos.

Leia `references/prospeccao-workflow.md` para o pipeline completo de prospecção → ClickUp → disparo em massa.

### Diferenças do Modo Notícia

| Aspecto | Modo Notícia | Modo Storytelling |
|---------|-------------|-------------------|
| Fonte | Supabase/fato externo | História/valores do cliente |
| Tom | Urgência/ameaça/oportunidade | Conexão/identificação/superação |
| Gatilho | Medo de ficar pra trás | "Eu também já passei por isso" |
| Arquétipo base | Dylan/GabrielAdamuchi | RPNews/kanekallaway blend |
| Credibilidade | Dados/fontes | Jornada real + resultado |

### Estrutura Recomendada

```
## Ângulo (a lição que a história ensina)
## Tema (dor do ICP que o roteiro ataca)
## Gatilho Primário
## Script
Hook: [gancho da história pessoal que conecta com a dor do ICP]
Desenvolvimento: [contar a jornada — o que tentou, o que não funcionou, a virada]
Fechamento: [o que aprendeu + call to action sutil]
## Edição de Tela
## Notas de Entrega
```

### Regras de Tom (para conteúdo pessoal)

1. **Nunca soar como robô explicando conceito.** Use frases como "senta aqui que vou te contar", "deixa eu te falar o que aconteceu comigo", "parece piada mas foi assim".
2. **História real primeiro, lição depois.** A credibilidade vem da jornada, não do verbo técnico.
3. **Evite gatilhos genéricos de IA** ("o mercado está mudando", "a revolução chegou", "isso vai transformar tudo"). Prefira gatilhos que nascem da experiência real: "quando eu comecei, achei que era só pagar anúncio e pronto — quebrei a cara".
4. **Profissão-agnóstico no hook, específico no desenvolvimento.** (regra existente, reforçada aqui)
5. **Use EJACA para conectar com o ICP:** Encorajar, Justificar, Aliviar, Confirmar, Apontar (ver referência marlon-brand-guide.md).
6. **Palavras-poder do ICP:** automático, simples, prático, rápido, organizado, controle, tempo livre, sem complicação, funciona.
7. **Frases-poder do ICP:** "Trabalhe menos e ganhe mais", "sua empresa funcionando sozinha", "pare de apagar incêndios", "cresça sem contratar mais gente".

### Quando NÃO usar
- Cliente pediu notícia factual
- Cliente não compartilhou história pessoal ou valores
- O conteúdo é estritamente promocional/sales pitch

## Workflow Integration (ClickUp)

Após gerar o roteiro, salve-o como uma task no ClickUp. O pipeline padrão:

1. Criar task na **lista Tiktok** (pasta Marketing → espaço O Tear CRM)
2. Status inicial: `concept`
3. Nome: `"Roteiro: {tema} - {plataforma}"`
4. Body: o script completo nos campos `name` + `markdown_description`
5. Tags: `roteiro`, `tiktok` (ou a plataforma alvo), mais tags de tema

### Hook Templates (ClickUp naming)

Quando criar tasks **apenas com hooks** (sem profissão específica):

1. Nome: `"Hook: Esse e um novo comeco para [quem/quando/motivo]"`
2. Body: hook completo + trigger + quando usar + variação curta + edição de tela
3. Tags obrigatórias: `roteiro`, `tiktok`, `hook`, `template`, `novo-comeco`
4. Tags opcionais: tema específico (ex: `criatividade`, `demissao`, `inclusao`, `carreira`)
5. Status: `concept`

### ClickUp API (curl)

```bash
# Listar pastas/lists de um espaço
curl -sS -H 'Authorization: pk_TOKEN' \
  'https://api.clickup.com/api/v2/space/{space_id}/folder?archived=false'

# Criar task numa lista
curl -sS -X POST -H 'Authorization: pk_TOKEN' \
  -H 'Content-Type: application/json' \
  'https://api.clickup.com/api/v2/list/{list_id}/task' \
  -d '{
    "name": "Roteiro: Tema - Plataforma",
    "markdown_description": "Hook:\n...\nDevelopment:\n...\nClosing:\n...",
    "status": "concept",
    "tags": ["roteiro", "tiktok", "tema"]
  }'
```

Token e IDs estão salvos em memória para este workspace.

## Disparo em Massa via Evolution API (Prospecção)

Use quando o cliente quiser **enviar mensagens em massa** para uma lista de leads via Evolution API (WhatsApp), com delay configurável entre disparos.

### Configuração (O Tear CRM)

```
URL: https://evo2.otear.com.br
Instância: agi
Key: SUA_EVOLUTION_API_KEY
Endpoint: POST /message/sendText/{instance}
```

### Formato do telefone

Evolution API espera números no formato brasileiro completo sem formatação:
- Fixo: `55DDDNumero` (ex: `552135845000`)
- Celular: `55DDDNumero` (ex: `5521970947009`)
- ⚠️ Remover parênteses, traços, espaços
- ⚠️ Números 0800 geralmente NÃO aceitam WhatsApp — pular ou marcar como "skipped"

### Pipeline completo: Prospecção → ClickUp → Disparo

1. **Receber lista de leads** (JSON do Google Maps / Supabase / manual)
2. **Gerar script de abordagem** por lead (baseado em scoring: hot/warm/cold)
3. **Criar task no ClickUp** para cada lead (lista Tiktok, status "concept")
   - Nome: `"🎯 Disparo: {Nome da Empresa}"`
   - Body: dados do lead + script + instrução
   - Tags: `disparo`, `prospeccao`, `whatsapp`, `hot/warm`, categoria
4. **Enviar mensagem via Evolution API** com delay de 3 min (preferência da Patricia)
5. **Atualizar task no ClickUp** para "enviou" após confirmação

### Script de disparo em massa

Use `scripts/bulk_disparo.py` para disparos automatizados. O script:
- Aceita lista de leads (nome, telefone, mensagem)
- Envia via Evolution API com delay configurável (padrão: 180s)
- Salva log incremental em `/tmp/disparos_log/`
- Imprime status em tempo real

```bash
python3 ~/.hermes/skills/content/news-script-adapter/scripts/bulk_disparo.py \
  --leads /tmp/leads_disparo.json \
  --delay 180 \
  --log-dir /tmp/disparos_log
```

Formato do JSON de entrada:
```json
[
  {
    "nome": "Empresa X",
    "telefone": "5521999999999",
    "mensagem": "Olá! Tudo bem?...",
    "task_id": "wdu9v75nvx"
  }
]
```

### Criar tasks em massa no ClickUp

Para criar múltiplas tasks de uma vez, use `mcp_clickup_manage_task` em loop (até 3 por chamada via `delegate_task` em paralelo). Cada task deve conter:
- Dados do lead (nome, telefone, endereço, categoria, rating)
- Script de abordagem
- Instrução de disparo
- Tags relevantes

### Pitfalls

- **Nunca disparar sem delay** — Evolution API pode rate-limitar; 3 min é o mínimo seguro
- **Sempre salvar log** — falhas de timeout/erro precisam ser rastreáveis
- **Verificar números 0800** — não aceitam WhatsApp, pular antes de enviar
- **Telefone formatado errado** = falha silenciosa; sempre validar formato `55DDDNumero`
- **Green Solar (0800 878 2200)**: exemplo de número que deve ser pulado ou tratado especialmente
- **Geração Inteligente**: telefone no dado original era `99999-9999` (placeholder) — sempre verificar no Maps antes de disparar

## Avoid

- hook genérico sem stakes
- introdução longa
- repetição do mesmo ponto
- notas de tela inúteis
- neutralidade excessiva quando o arquétipo pede tensão
- **assumir que trending topic genérico serve** — o tema do cliente é IA para negócios. Google Trends geral (futebol, política, entretenimento, celebridades) não é fonte válida sem filtro. Sempre verificar antes de criar conteúdo se o tema é conectável a IA/tech.
- assumir que o cliente quer script completo com profissão — pergunte primeiro se ele quer **hooks isolados** ou roteiro fechado
- no formato "novo começo", nunca preencher a profissão no hook — o hook é agnóstico, a profissão entra no desenvolvimento
- **no modo Storytelling, evitar gatilhos genéricos de IA** ("o mercado está mudando", "isso vai transformar tudo") — preferir gatilhos nascidos da experiência real do cliente
- **no modo Storytelling, não soar como explicação técnica** — a conexão vem da história, não do conceito
- **usar `curl | python3 -c`** para queries Supabase ou News API — sempre salve em arquivo ou use Python com `urllib`

## Prospecção WhatsApp + ClickUp Pipeline

Quando o usuário receber uma lista de leads (JSON ou colado) e quiser:
1. Criar tasks no ClickUp para cada lead
2. Enviar mensagens de WhatsApp via Evolution API em lote
3. Rastrear envios

→ Leia `references/prospeccao-whatsapp-pipeline.md` para o fluxo completo, script padrão, formato de task, e pitfalls (incluindo o cache de terminal e delay obrigatório de 3 min).
