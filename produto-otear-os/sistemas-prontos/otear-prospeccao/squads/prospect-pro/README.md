# ProspectPro — Prospecção Ativa para Marketing Digital

Sistema completo de prospecção ativa que busca empresas no Google Maps, enriquece com dados do Instagram, analisa engajamento e gera relatórios com scoring e scripts de abordagem personalizados.

## Stack

- **Python 3.10+** + **FastAPI**
- **Playwright** (web scraping com anti-detecção)
- **JSON/CSV** (armazenamento de leads)
- **AIOS Framework** (orquestração de agentes)

---

## Instalação

```bash
cd squads/prospect-pro

# Instalar dependências
pip install -r requirements.txt

# Instalar navegador para scraping
playwright install chromium
```

## Iniciar API

```bash
cd squads/prospect-pro
uvicorn app.main:app --reload --port 8000
```

Acesse:
- **API**: http://localhost:8000
- **Swagger (docs interativos)**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

---

## Pipeline de Prospecção

```
🔍 Scout          💎 Enricher         📸 Stalker          📝 Reporter
Google Maps   →   Busca Instagram  →  Analisa perfis  →  Relatório final
(leads brutos)    + scoring inicial   + engagement        + scripts abordagem
```

---

## Endpoints da API

### 1. Scrape Google Maps

Busca empresas no Google Maps por categoria e localização.

**`POST /api/scrape/maps/sync`** — Síncrono (aguarda resultado)

```bash
curl -X POST http://localhost:8000/api/scrape/maps/sync \
  -H "Content-Type: application/json" \
  -d '{
    "query": "restaurantes",
    "location": "São Paulo",
    "limit": 10
  }'
```

**Resposta:**

```json
{
  "status": "completed",
  "total": 10,
  "json_path": "data/leads/20260305_143022_leads.json",
  "csv_path": "data/leads/20260305_143022_leads.csv",
  "leads": [
    {
      "google": {
        "name": "Restaurante Fasano",
        "address": "R. Vitório Fasano, 88 - Cerqueira César, São Paulo",
        "phone": "(11) 3896-4000",
        "website": "https://www.fasano.com.br",
        "rating": 4.6,
        "reviews_count": 4521,
        "category": "Restaurante italiano",
        "maps_url": "https://www.google.com/maps/place/..."
      },
      "status": "raw"
    }
  ]
}
```

**`POST /api/scrape/maps`** — Assíncrono (roda em background)

```bash
curl -X POST http://localhost:8000/api/scrape/maps \
  -H "Content-Type: application/json" \
  -d '{
    "query": "salões de beleza",
    "location": "Campinas",
    "limit": 20
  }'
```

**Resposta:**

```json
{
  "job_id": "job_1",
  "status": "started",
  "query": "salões de beleza",
  "location": "Campinas"
}
```

**`GET /api/scrape/status/{job_id}`** — Verificar status do job

```bash
curl http://localhost:8000/api/scrape/status/job_1
```

**Resposta (em andamento):**

```json
{
  "status": "running",
  "result": null
}
```

**Resposta (concluído):**

```json
{
  "status": "completed",
  "result": {
    "total": 20,
    "json_path": "data/leads/20260305_150112_leads.json",
    "csv_path": "data/leads/20260305_150112_leads.csv",
    "leads": [...]
  }
}
```

---

### 2. Enriquecer Leads

Busca o Instagram de cada lead (via website e Google) e calcula scoring inicial.

**`POST /api/enrich`** — Enriquecer último arquivo de leads

```bash
curl -X POST http://localhost:8000/api/enrich \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Com arquivo específico:**

```bash
curl -X POST http://localhost:8000/api/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "leads_file": "data/leads/20260305_143022_leads.json"
  }'
```

**Resposta:**

```json
{
  "status": "completed",
  "total": 10,
  "json_path": "data/enriched/20260305_151530_enriched.json"
}
```

---

### 3. Analisar Instagram

Scrape dos perfis Instagram: followers, engagement, frequência de posts.

**`POST /api/analyze`** — Analisar último arquivo enriquecido

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Com opções:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "leads_file": "data/enriched/20260305_151530_enriched.json",
    "posts_to_analyze": 12
  }'
```

**Resposta:**

```json
{
  "status": "completed",
  "total": 10,
  "hot": 3,
  "warm": 4,
  "cold": 3,
  "json_path": "data/enriched/20260305_152045_enriched.json"
}
```

---

### 4. Listar Leads

**`GET /api/leads`** — Todos os leads

```bash
curl http://localhost:8000/api/leads
```

**Com filtros:**

```bash
# Apenas leads hot
curl "http://localhost:8000/api/leads?classification=hot"

# Leads com score >= 8
curl "http://localhost:8000/api/leads?min_score=8"

# Leads brutos (não enriquecidos)
curl "http://localhost:8000/api/leads?status=raw"

# De um arquivo específico
curl "http://localhost:8000/api/leads?file=data/enriched/20260305_152045_enriched.json"
```

**Resposta:**

```json
{
  "total": 10,
  "hot": 3,
  "warm": 4,
  "cold": 3,
  "leads": [
    {
      "google": {
        "name": "Barbearia Old School",
        "address": "R. Augusta, 1200 - São Paulo",
        "phone": "(11) 99999-0000",
        "website": null,
        "rating": 4.2,
        "reviews_count": 8,
        "category": "Barbearia"
      },
      "instagram": {
        "handle": "barbearia_oldschool",
        "profile_url": "https://www.instagram.com/barbearia_oldschool/",
        "followers": 320,
        "engagement_rate": 1.2,
        "posts_count": 45,
        "posting_frequency_days": 12.5
      },
      "score": {
        "no_website": 3,
        "no_instagram": 0,
        "low_engagement": 3,
        "irregular_posting": 2,
        "few_reviews": 1,
        "low_rating": 0,
        "no_professional_bio": 1,
        "no_bio_link": 1,
        "total": 11,
        "classification": "hot"
      },
      "approach_script": "Olá! Tudo bem? 👋\n\nSou especialista em marketing digital para Barbearia e notei que o Barbearia Old School não tem um site profissional e o engajamento nas redes está abaixo do ideal.\n\nTenho algumas ideias rápidas que podem trazer resultados já no primeiro mês.\n\nPosso te enviar mais detalhes?",
      "status": "analyzed"
    }
  ]
}
```

---

### 5. Gerar Relatório

**`POST /api/reports/generate`** — Gerar relatório de prospecção

```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prospecção Restaurantes SP - Março 2026"
  }'
```

**Com arquivo específico:**

```bash
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "leads_file": "data/enriched/20260305_152045_enriched.json",
    "title": "Salões de Beleza Campinas",
    "include_approach_scripts": true
  }'
```

**Resposta:**

```json
{
  "status": "completed",
  "report_path": "data/reports/20260305_153000_report.md",
  "csv_path": "data/reports/20260305_153000_reports.csv",
  "summary": {
    "total": 10,
    "hot": 3,
    "warm": 4,
    "cold": 3
  }
}
```

**`GET /api/reports/`** — Listar relatórios gerados

```bash
curl http://localhost:8000/api/reports/
```

**Resposta:**

```json
{
  "total": 2,
  "reports": [
    {
      "id": "20260305_153000_report",
      "title": "Prospecção Restaurantes SP - Março 2026",
      "generated_at": "2026-03-05T15:30:00",
      "summary": { "total": 10, "hot": 3, "warm": 4, "cold": 3 },
      "path": "data/reports/20260305_153000_report.json"
    }
  ]
}
```

**`GET /api/reports/{report_id}`** — Ver relatório completo

```bash
curl http://localhost:8000/api/reports/20260305_153000_report
```

**`GET /api/reports/{report_id}/download?format=md`** — Download do relatório

```bash
# Markdown
curl -O http://localhost:8000/api/reports/20260305_153000_report/download?format=md

# JSON
curl -O http://localhost:8000/api/reports/20260305_153000_report/download?format=json
```

---

## Fluxo Completo — Exemplo Prático

### Cenário: Prospectar barbearias em São Paulo

```bash
# 1. Buscar 15 barbearias no Google Maps
curl -X POST http://localhost:8000/api/scrape/maps/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "barbearias", "location": "São Paulo, Zona Sul", "limit": 15}'

# 2. Encontrar Instagram de cada barbearia
curl -X POST http://localhost:8000/api/enrich \
  -H "Content-Type: application/json" -d '{}'

# 3. Analisar os perfis do Instagram (últimos 12 posts)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" -d '{"posts_to_analyze": 12}'

# 4. Gerar relatório com scripts de abordagem
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"title": "Barbearias Zona Sul SP - Março 2026"}'

# 5. Ver apenas leads hot (prontos para abordar)
curl "http://localhost:8000/api/leads?classification=hot"
```

---

## Uso via Scripts (sem API)

```bash
cd squads/prospect-pro

# Scrape Google Maps
python -m scripts.google_maps_scraper "academias" "Rio de Janeiro" 10

# Enriquecer leads (usa último arquivo de data/leads/)
python -m scripts.lead_enricher

# Enriquecer arquivo específico
python -m scripts.lead_enricher "data/leads/20260305_143022_leads.json"

# Analisar Instagram (usa último arquivo de data/enriched/)
python -m scripts.instagram_scraper

# Gerar relatório
python -m scripts.report_generator
python -m scripts.report_generator "data/enriched/20260305_152045_enriched.json" "Academias RJ"
```

---

## Scoring de Leads (0-16 pontos)

Cada lead recebe uma pontuação baseada em indicadores de que **precisa de marketing digital**:

| Critério | Pontos | O que indica |
|----------|--------|-------------|
| Sem website | +3 | Precisa de presença digital |
| Sem Instagram | +4 | Oportunidade enorme de gestão de redes |
| Engagement < 2% | +3 | Conteúdo não está performando |
| Posts irregulares (> 7 dias) | +2 | Não tem estratégia de conteúdo |
| Poucos reviews Google (< 10) | +1 | Pouca visibilidade online |
| Rating Google < 4.0 | +1 | Precisa de gestão de reputação |
| Bio não profissional | +1 | Perfil amador no Instagram |
| Sem link na bio | +1 | Não converte seguidores em clientes |

### Classificação

| Classe | Score | Ação |
|--------|-------|------|
| 🔥 **Hot** | ≥ 8 | Abordar imediatamente |
| 🌡️ **Warm** | 5-7 | Abordar em 1-3 dias |
| ❄️ **Cold** | < 5 | Monitorar para futuro |

---

## Estrutura de Dados

### Lead (JSON)

```json
{
  "id": "a1b2c3d4",
  "google": {
    "name": "Pizza do Zé",
    "address": "R. das Flores, 100 - Vila Madalena, São Paulo",
    "phone": "(11) 3000-1234",
    "website": null,
    "rating": 4.3,
    "reviews_count": 7,
    "category": "Pizzaria",
    "maps_url": "https://www.google.com/maps/place/..."
  },
  "instagram": {
    "handle": "pizzadoze",
    "profile_url": "https://www.instagram.com/pizzadoze/",
    "bio": "🍕 A melhor pizza da Vila Madalena",
    "bio_link": null,
    "followers": 850,
    "following": 320,
    "posts_count": 62,
    "is_business": true,
    "is_verified": false,
    "engagement_rate": 1.4,
    "avg_likes": 10.2,
    "avg_comments": 1.8,
    "posting_frequency_days": 9.3,
    "recent_posts": [
      { "url": "https://www.instagram.com/p/abc123/", "likes": 12, "comments": 2 },
      { "url": "https://www.instagram.com/p/def456/", "likes": 8, "comments": 1 }
    ]
  },
  "score": {
    "no_website": 3,
    "no_instagram": 0,
    "low_engagement": 3,
    "irregular_posting": 2,
    "few_reviews": 1,
    "low_rating": 0,
    "no_professional_bio": 0,
    "no_bio_link": 1,
    "total": 10,
    "classification": "hot"
  },
  "approach_script": "Olá! Tudo bem? 👋\n\nSou especialista em marketing digital para Pizzaria e notei que o Pizza do Zé não tem um site profissional e o engajamento nas redes está abaixo do ideal.\n\nTenho algumas ideias rápidas que podem trazer resultados já no primeiro mês.\n\nPosso te enviar mais detalhes?",
  "status": "analyzed",
  "created_at": "2026-03-05T14:30:22",
  "updated_at": "2026-03-05T15:20:45"
}
```

### CSV Exportado (relatório)

```csv
nome,categoria,telefone,website,endereco,rating_google,reviews_google,instagram,followers,engagement_rate,score,classificacao,script_abordagem
Pizza do Zé,Pizzaria,(11) 3000-1234,,R. das Flores 100,4.3,7,pizzadoze,850,1.4,10,hot,"Olá! Tudo bem? 👋 | Sou especialista em..."
```

---

## Configuração

### Público-alvo (`config/target_audience.yaml`)

Edite para definir suas categorias de interesse:

```yaml
target_audience:
  categories:
    - restaurantes
    - barbearias
    - salões de beleza
    - academias
    # adicione suas categorias...

  locations:
    default: "São Paulo, Brasil"
    radius_km: 10
```

### Scoring (`config/scoring_rules.yaml`)

Ajuste os pontos de cada critério:

```yaml
scoring:
  criteria:
    no_website:
      points: 3          # altere o peso
    low_engagement:
      threshold: 2.0     # altere o limite de engagement
    few_reviews:
      threshold: 10      # altere o mínimo de reviews
```

### Scraper (`config/scraper_config.yaml`)

Configure delays e limites:

```yaml
scraper:
  browser:
    headless: true       # false para ver o navegador em ação
  delays:
    between_actions_min: 2.0
    between_actions_max: 5.0
  limits:
    max_leads_per_session: 50
```

---

## Estrutura de Diretórios

```
squads/prospect-pro/
├── app/                        # FastAPI API
│   ├── main.py                 # Aplicação principal
│   ├── routers/
│   │   ├── scrape.py           # POST /api/scrape/maps
│   │   ├── prospects.py        # GET /api/leads, POST /api/enrich, /api/analyze
│   │   └── reports.py          # POST/GET /api/reports
│   ├── models/
│   │   └── lead.py             # Modelos Pydantic
│   └── services/
│       ├── maps_service.py     # Serviço Google Maps
│       ├── instagram_service.py # Serviço Instagram
│       └── report_service.py   # Serviço Relatórios
├── scripts/                    # Scripts executáveis diretamente
│   ├── google_maps_scraper.py
│   ├── instagram_scraper.py
│   ├── lead_enricher.py
│   ├── report_generator.py
│   └── utils/
│       ├── browser.py          # Playwright helpers + anti-detecção
│       ├── csv_handler.py      # Leitura/escrita JSON/CSV
│       └── scoring.py          # Algoritmo de scoring
├── data/                       # Dados gerados (gitignore)
│   ├── leads/                  # Leads brutos do Google Maps
│   ├── enriched/               # Leads enriquecidos com Instagram
│   └── reports/                # Relatórios (MD, JSON, CSV)
├── config/                     # Configurações editáveis
│   ├── scoring_rules.yaml
│   ├── target_audience.yaml
│   └── scraper_config.yaml
├── agents/                     # Agentes AIOS
├── tasks/                      # Tasks AIOS
├── workflows/                  # Pipeline de prospecção
├── checklists/                 # Validação de dados
├── templates/                  # Templates de relatório
├── squad.yaml                  # Manifesto do squad
└── requirements.txt
```

---

## Agentes AIOS

| Agente | ID | Função | Comando |
|--------|----|--------|---------|
| 🔍 Scout | pp-scout | Scraping Google Maps | `/SQUADS:prospect-pro:pp-scout` |
| 💎 Enricher | pp-enricher | Enriquecimento + Scoring | `/SQUADS:prospect-pro:pp-enricher` |
| 📸 Stalker | pp-stalker | Análise Instagram | `/SQUADS:prospect-pro:pp-stalker` |
| 📝 Reporter | pp-reporter | Relatórios + Abordagem | `/SQUADS:prospect-pro:pp-reporter` |

---

## Dicas

- **Comece com poucos leads** (`limit: 5`) para testar antes de escalar
- **Use `headless: false`** no `scraper_config.yaml` para ver o navegador em ação
- **Leads hot** são os que mais precisam dos seus serviços — aborde primeiro
- **Os scripts de abordagem** são sugestões — personalize com base no contexto do lead
- **O CSV exportado** pode ser importado em qualquer CRM ou planilha Google Sheets
- **Respeite rate limits** — o scraper tem delays configuráveis para evitar bloqueios
