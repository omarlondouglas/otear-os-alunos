---
name: seo-auditor-full-audit
agent: seo-auditor
description: Executar audit completo de SEO e gerar relatÃ³rio PDF
---

# Full SEO Audit

## Inputs
- `vercel_url`: URL do site live na Vercel
- `client_name`: Nome do cliente/negÃ³cio
- `target_keywords`: Lista de keywords alvo
- `design_tokens`: Cores e fontes do design system (para estilizar o PDF)

## Steps

### 1. Google PageSpeed Insights
```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
  ?url={vercel_url}
  &strategy=mobile
  &category=performance
  &category=seo
  &category=accessibility
  &category=best-practices
  &key={PAGESPEED_API_KEY}
```

Coletar:
- Performance score (0-100)
- SEO score (0-100)
- Accessibility score (0-100)
- Best Practices score (0-100)
- LCP (Largest Contentful Paint)
- FID (First Input Delay) / INP
- CLS (Cumulative Layout Shift)
- FCP (First Contentful Paint)
- TBT (Total Blocking Time)
- Speed Index

Repetir com `strategy=desktop`.

### 2. Meta Tags & Schema Check
Fazer fetch da pÃ¡gina e verificar:
- [ ] `<title>` presente e < 60 chars
- [ ] `<meta name="description">` presente e 120-160 chars
- [ ] `<meta name="viewport">` presente
- [ ] Open Graph tags (og:title, og:description, og:image)
- [ ] Twitter Card tags
- [ ] Schema.org JSON-LD (LocalBusiness, Article, etc)
- [ ] Canonical URL
- [ ] robots.txt acessÃ­vel
- [ ] sitemap.xml acessÃ­vel
- [ ] favicon presente
- [ ] lang attribute no HTML

### 3. Moz API (Domain Authority)
```
GET https://lsapi.seomoz.com/v2/url_metrics
  Body: { "targets": ["{vercel_url}"] }
  Auth: Basic {MOZ_ACCESS_ID}:{MOZ_SECRET_KEY}
```

Coletar:
- Domain Authority (DA)
- Page Authority (PA)
- Spam Score

### 4. Gerar PDF
Usar biblioteca de geraÃ§Ã£o de PDF (puppeteer, jspdf, ou react-pdf) para criar relatÃ³rio visual:

#### Layout do PDF:
- **PÃ¡gina 1: Capa**
  - Nome do cliente
  - URL do site
  - Data do audit
  - "RelatÃ³rio de SEO & Performance"

- **PÃ¡gina 2: Scores Overview**
  - 4 cÃ­rculos grandes (Performance, SEO, Accessibility, Best Practices)
  - Cores: verde (90+), laranja (50-89), vermelho (0-49)
  - Mobile vs Desktop side-by-side

- **PÃ¡gina 3: Core Web Vitals**
  - LCP, FID/INP, CLS com indicadores verde/amarelo/vermelho
  - Barra de comparaÃ§Ã£o com thresholds do Google
  - FCP, TBT, Speed Index

- **PÃ¡gina 4: Checklist SEO TÃ©cnico**
  - Tabela com âœ…/âŒ para cada item verificado
  - Meta tags, Schema, OG, sitemap, robots, etc

- **PÃ¡gina 5: Keywords & PrÃ³ximos Passos**
  - Keywords target definidas
  - PosiÃ§Ã£o atual (se Search Console disponÃ­vel)
  - RecomendaÃ§Ãµes de melhoria priorizadas

### 5. Salvar Artefatos
- `artifacts/seo-report.pdf` â€” RelatÃ³rio visual para o cliente
- `artifacts/seo-audit-raw.json` â€” Dados brutos para histÃ³rico
- `artifacts/seo-scores.json` â€” Scores resumidos para comparaÃ§Ã£o futura

## Output
```json
{
  "scores": {
    "mobile": { "performance": 95, "seo": 98, "accessibility": 92, "bestPractices": 100 },
    "desktop": { "performance": 99, "seo": 98, "accessibility": 92, "bestPractices": 100 }
  },
  "core_web_vitals": {
    "lcp": "1.2s",
    "fid": "12ms",
    "cls": "0.05"
  },
  "domain_authority": 0,
  "checklist_passed": 14,
  "checklist_total": 16,
  "pdf_path": "artifacts/seo-report.pdf"
}
```

