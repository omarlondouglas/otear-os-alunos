# O Tear — Prospecção WhatsApp + ClickUp Pipeline

## Quando Usar

Use este fluxo quando o usuário:
- Receber uma lista de leads (JSON ou colado) de uma ferramenta de prospecção (ex: Prospect Pro, Google Maps scraper)
- Quiser **enviar mensagens de WhatsApp** em lote para leads (com delay de 3 min entre cada)
- Quiser **salvar cada lead como task no ClickUp** (lista Tiktok, status "concept")
- Quiser **rastrear quem recebeu e quem não recebeu**

## Arquitetura do Fluxo

```
Lista de leads (JSON/arquivo)
       ↓
  [1] Criar task no ClickUp (lista Tiktok, status "concept")
       ↓
  [2] Enviar mensagem via Evolution API (agi instance)
       ↓
  [3] Atualizar task → status "enviou"
```

## Configuração

### Evolution API (O Tear)
- **URL:** `https://evo2.otear.com.br`
- **Instance:** `agi`
- **Auth:** header `apikey: <KEY>`
- **Endpoint:** POST `/message/sendText/agi`
- **Delay entre mensagens:** 180s (3 min) — **obrigatório, não reduzir**

### ClickUp
- **Space ID:** 90142498572 (O Tear CRM)
- **Pasta:** Marketing
- **Lista Tiktok:** ID 901415273387
- **Token:** ver memória

## Script Padrão de Disparo em Lote

```python
import requests, time, json, os, sys

EVOLUTION_URL = "https://evo2.otear.com.br"
EVOLUTION_INSTANCE = "agi"
EVOLUTION_KEY = "<sua-key>"

leads = [
    ("Nome da Empresa", "5521999999999",
     "Olá! Tudo bem?\n\nSou especialista em marketing digital..."),
    # ... mais leads
]

total = len(leads)
enviados = 0
falhas = 0
resultados = []

for idx, (nome, telefone, msg) in enumerate(leads):
    seq = idx + 1
    sys.stdout.write(f"\n[{seq}/{total}] {nome}...\n")
    sys.stdout.flush()
    
    endpoint = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_KEY
    }
    payload = {
        "number": telefone,
        "text": msg,
        "options": {
            "delay": 1000,
            "presence": "composing",
            "linkPreview": True
        }
    }
    
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        status_code = resp.status_code
        if status_code in [200, 201]:
            enviados += 1
            sys.stdout.write(f"  → ENVIADO (HTTP {status_code})\n")
        else:
            falhas += 1
            sys.stdout.write(f"  → FALHOU (HTTP {status_code})\n")
        resultados.append({"seq": seq, "nome": nome, "telefone": telefone, "http_status": status_code, "success": status_code in [200, 201]})
    except Exception as e:
        falhas += 1
        sys.stdout.write(f"  → FALHOU ({str(e)[:80]})\n")
        resultados.append({"seq": seq, "nome": nome, "telefone": telefone, "http_status": "error", "success": False})
    
    # Salvar log incremental
    with open("/tmp/disparos_log/resultado.json", 'w') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    # Delay de 3 min entre mensagens
    if idx < total - 1:
        time.sleep(180)

print(f"\nFINALIZADO: {enviados} enviados, {falhas} falhas de {total}")
```

## Formato do Telefone

A Evolution API espera números no formato brasileiro **sem formatação**:
- Entrada: `(21) 99608-0083` ou `0800 878 2200`
- Formato correto: `5521996080083` (código do país + DDD + número, sem espaços/parênteses)
- Para 0800: `5508008782200` (pode não funcionar — 0800 geralmente não aceita WhatsApp)

## Estrutura da Task no ClickUp

```json
{
  "name": "🎯 Disparo: {Nome da Empresa}",
  "markdown_description": "**Lead:** {Nome}\n**Telefone:** {formatado}\n**Categoria:** {categoria}\n**Status Prospecção:** {hot/warm} (score {N})\n**Site:** {url ou 'Não possui'}\n**Instagram:** {@handle ou 'Não possui'}\n**Rating:** {nota}\n**Endereço:** {endereço}\n**Script de Abordagem:**\n\n{script completo}\n\n---\n**Instrução:** Enviar mensagem via Evolution API. Atualizar status para 'enviou' após confirmação.",
  "status": "concept",
  "tags": ["disparo", "prospeccao", "whatsapp", "hot/warm", "energia-solar", "sem-site/sem-instagram"]
}
```

## Pitfalls

### ⚠️ Cache de script no terminal persistente
O terminal Hermes mantém versão antiga de scripts Python em cache mesmo após edição no disco. Se receber `NameError` para variáveis que você sabe que estão definidas:
- **Solução:** Execute via heredoc inline: `python3 -u - << 'PYEOF' ... PYEOF`
- **Alternativa:** Renomeie o arquivo (ex: `send_disparos_v2.py`) para forçar nova leitura

### ⚠️ Timeout do execute_code
O `execute_code` tem limite de 300s. Para scripts com delay de 3 min entre itens, **sempre use `terminal(background=true)`**.

### ⚠️ Telefones 0800
Números 0800 geralmente não aceitam WhatsApp. Marque a task como "skipped" e não tente enviar.

### ⚠️ Delay mínimo de 3 min
A Patricia (O Tear) prefere delay de 3 min entre mensagens. **Não reduza** sem autorização — é preferência do cliente, não requis técnico.

### ⚠️ Atualização de status no ClickUp
Após confirmar envio, atualizar task de "concept" para status customizado "enviou" (se existir na space) ou manter "concept" e adicionar tag "enviou". Verificar space statuses disponíveis antes de atualizar.

## Fluxo Completo (passo a passo)

1. Receber lista de leads (JSON ou colado na conversa)
2. Extrair nome, telefone, categoria, script de abordagem de cada lead
3. Para cada lead:
   a. Criar task no ClickUp (lista Tiktok, status "concept")
   b. Adicionar ID da task no array de controle
4. Executar script de disparo em lote (background, com delay de 3 min)
5. Após conclusão, para cada envio bem-sucedido:
   a. Atualizar task correspondente → adicionar tag "enviou"
6. Relatório final: X enviados, Y falhas, Z skipped
