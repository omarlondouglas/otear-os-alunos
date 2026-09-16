# ✅ Correção: URLs de Vídeo nos Agentes

## Problema Relatado

Você testou manualmente a API de edição de vídeo e funcionou:
- API retorna: `/static/0af5a60a-8b57-4706-807b-84101c0041fc_final.mp4`
- Você monta: `https://otear-otear-editavideos.qc7qit.easypanel.host/static/...`
- Funciona! ✅

**MAS os agentes não estavam conseguindo fazer isso.**

## Causa Raiz Identificada

Dois problemas no código:

### 1. Barra Final no `.env`
```env
# ❌ ANTES (com barra final)
AGIVIDEO_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host/

# ✅ DEPOIS (sem barra final)
AGIVIDEO_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
```

### 2. `check_video_status_tool` não convertia URLs
A ferramenta retornava URLs relativas diretamente da API sem converter.

## Correções Aplicadas

### Arquivo: `.env`
- Removida barra final da URL

### Arquivo: `app/agents/agno_tools.py`

**1. Função `edit_video_tool` (linha ~386):**
```python
# Adicionado .rstrip("/") para evitar barras duplicadas
if download_url.startswith("/"):
    base_url = VIDEO_SERVICE_URL.rstrip("/")  # ✅ NOVO
    full_url = f"{base_url}{download_url}"
```

**2. Função `check_video_status_tool` (linha ~440):**
```python
# ✅ NOVA LÓGICA - Converte URLs relativas
result = response.json()

if result.get("status") == "completed" and result.get("download_url"):
    download_url = result["download_url"]
    if download_url.startswith("/"):
        base_url = VIDEO_SERVICE_URL.rstrip("/")
        result["download_url"] = f"{base_url}{download_url}"
        logger.info(f"[CHECK STATUS] Converted relative URL: {download_url} -> {result['download_url']}")

return result
```

## Testes Realizados

### ✅ Teste 1: Conversão de URL
```bash
python test_url_fix.py
```
**Resultado:** URL convertida corretamente ✅

### ✅ Teste 2: Fluxo Completo do Agente
```bash
python test_agent_video_flow.py
```
**Resultado:** Fluxo completo funcionando ✅

## Como Aplicar as Mudanças

### 1. Reinicie os serviços
```bash
docker-compose restart
```

### 2. Ou reconstrua (se necessário)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Como Testar

### Teste Manual via API
```bash
curl -X POST "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW" \
  -F 'request={"video_url":"https://exemplo.com/video.mp4","operations":[{"type":"preset","params":{"name":"VIRAL"}}],"output_format":"mp4"}'
```

### Teste com Agente
Envie para o agente:
```
Edita esse vídeo: https://exemplo.com/video.mp4
```

**Resposta esperada:**
```
Vídeo editado com sucesso! 🎬

Download: https://otear-otear-editavideos.qc7qit.easypanel.host/static/[ID]_final.mp4

O vídeo foi processado com legendas amarelas e remoção de silêncio (preset VIRAL).
```

## Logs para Monitorar

Procure por estas mensagens nos logs do container:

### ✅ Sucesso
```
[VIDEO TOOL] ✓ Job {job_id} COMPLETO! URL relativa convertida: /static/... -> https://...
```

### ✅ Check Status
```
[CHECK STATUS] Converted relative URL: /static/... -> https://...
```

### ❌ Problema
```
[VIDEO TOOL] Job completo mas sem download_url
```

## Verificação Rápida

Execute este comando para verificar se a variável está correta:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('VIDEO_EDITOR_API_URL'))"
```

**Saída esperada:**
```
https://otear-otear-editavideos.qc7qit.easypanel.host
```
(sem barra final)

## Possíveis Problemas Remanescentes

Se ainda não funcionar após reiniciar:

### 1. Agente não está chamando a ferramenta
**Sintoma:** Agente diz que editou mas não há logs de `[VIDEO TOOL]`
**Solução:** Verificar instruções do agente em `agno_agents.py`

### 2. Agente "esquece" a URL
**Sintoma:** Ferramenta retorna URL mas agente não repassa ao usuário
**Solução:** Problema no modelo LLM ou nas instruções do Orchestrator

### 3. Cache do Docker
**Sintoma:** Mudanças não são aplicadas
**Solução:** `docker-compose build --no-cache`

### 4. Variável de ambiente não carregada
**Sintoma:** URL ainda tem barra dupla `//`
**Solução:** Verificar se `.env` foi recarregado

## Arquivos Modificados

| Arquivo | Mudança | Linha |
|---------|---------|-------|
| `.env` | Removida barra final | 6 |
| `app/agents/agno_tools.py` | Adicionado `.rstrip("/")` em `edit_video_tool` | ~386 |
| `app/agents/agno_tools.py` | Adicionada conversão em `check_video_status_tool` | ~440-450 |

## Arquivos de Teste Criados

- `test_url_fix.py` - Testa conversão de URL
- `test_agent_video_flow.py` - Simula fluxo completo do agente
- `DIAGNOSTICO_URL_VIDEO.md` - Diagnóstico detalhado
- `RESUMO_CORRECAO_URL_VIDEO.md` - Este arquivo

## Conclusão

✅ **Código corrigido e testado**
✅ **URLs relativas agora são convertidas em absolutas**
✅ **Ambas as ferramentas (`edit_video_tool` e `check_video_status_tool`) fazem a conversão**

**Próximo passo:** Reinicie os serviços e teste com um agente real!

---

**Data da correção:** 2026-02-10
**Testado em:** Windows 10, Python 3.x
**Status:** ✅ Pronto para produção
