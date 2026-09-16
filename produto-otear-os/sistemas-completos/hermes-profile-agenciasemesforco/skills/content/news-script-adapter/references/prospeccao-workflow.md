# Workflow: Prospecção → ClickUp → Disparo em Massa

## Visão geral

Pipeline completo de prospecção do O Tear CRM:

```
Lista de leads (JSON/Supabase/Google Maps)
        ↓
    Scoring (hot/warm/cold)
        ↓
  Script de abordagem (gerado por lead)
        ↓
  Task no ClickUp (lista Tiktok, status "concept")
        ↓
  Disparo via Evolution API (delay 3 min)
        ↓
  Atualização ClickUp ("enviou")
```

## Componentes

### 1. Entrada

- **Formato:** JSON com campos: `nome`, `telefone`, `categoria`, `rating`, `endereço`, `script`
- **Fonte típica:** Google Maps (scraper/prospect-pro), Supabase, ou input manual
- **Exemplo de scoring:**
  - `hot` (score 5-8): sem site, sem Instagram, ou ambos
  - `warm` (score 3-5): têm site mas não têm Instagram (ou Instagram fraco)
  - `cold` (score 0-2): já têm presença digital estabelecida

### 2. ClickUp

- **Lista:** Tiktok (ID: `901415273387`)
- **Pasta:** Marketing
- **Espaço:** O Tear CRM (space ID: `90142498572`)
- **Status:** `concept` (inicial), atualizar para "enviou" após disparo
- **Task tags:** `disparo`, `prospeccao`, `whatsapp`, `hot/warm`, categoria
- **Task body:** dados do lead + script de abordagem + instrução

### 3. Evolution API

- **URL:** https://evo2.otear.com.br
- **Instância:** agi
- **Key:** SUA_EVOLUTION_API_KEY (ou variável EVOLUTION_API_KEY)
- **Endpoint:** POST `/message/sendText/agi`
- **Headers:** `Content-Type: application/json`, `apikey: KEY`
- **Delay:** 180s (3 min) entre disparos — preferência da Patricia
- **Rate limit:** não documentado; 3 min é o mínimo seguro

### 4. Script de disparo

Local: `scripts/bulk_disparo.py`

```bash
python3 scripts/bulk_disparo.py \
  --leads /tmp/leads_disparo.json \
  --delay 180
```

Features:
- Limpa telefone automaticamente (remove formatação)
- Valida números 0800 (pula)
- Salva log incremental
- Modo `--dry-run` para testar

## Sessão 2026-06-25

- 14 leads processados de `Relatório de Prospecção - 20260620_202347_leads`
- 14 tasks criadas no ClickUp (wdu9v75nvx até wdu9v75nwb)
- 14 disparos enviados via Evolution API
- 1 lead (Green Solar) com telefone 0800 — skipped/especial
- 1 lead (Geração Inteligente) com telefone potencialmente incorreto (placeholder `99999-9999` no dado original)
- Resultado: processamento completo, aguardando confirmação de entregas

## Pitfalls encontrados

1. **Erro de escopo em script shell** — `logs_dir` definido depois de usar `os.makedirs(logs_dir)`. Em Python, definir ANTES de usar.
2. **Telefone 0800** — Green Solar usa 0800 878 2200; não aceita WhatsApp
3. **Telefone placeholder** — prospecção às vezes gera números inválidos (`99999-9999`); verificar no Maps
4. **Delay obrigatório** — sem delay de 3 min, Evolution API pode rate-limitar silenciosamente
5. **Formato do número** — sempre `55DDDNumero` sem formatação; parênteses/traços causam falha silenciosa
