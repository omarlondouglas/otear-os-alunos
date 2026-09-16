# Diagnóstico: Problema com URLs de Vídeo

## Problema Identificado

Você relatou que quando faz um teste manual, a API retorna:
```json
{
  "id": "0af5a60a-8b57-4706-807b-84101c0041fc",
  "download_url": "/static/0af5a60a-8b57-4706-807b-84101c0041fc_final.mp4"
}
```

E você monta a URL completa manualmente:
```
https://otear-otear-editavideos.qc7qit.easypanel.host/static/0af5a60a-8b57-4706-807b-84101c0041fc_final.mp4
```

E funciona! Mas os agentes não estão conseguindo fazer isso.

## Causa Raiz

O código em `app/agents/agno_tools.py` **JÁ TEM** a lógica para converter URLs relativas em absolutas:

```python
if download_url.startswith("/"):
    base_url = VIDEO_SERVICE_URL.rstrip("/")
    full_url = f"{base_url}{download_url}"
```

**PORÉM**, havia dois problemas:

### 1. Barra Final no .env (CORRIGIDO)

**Antes:**
```env
AGIVIDEO_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host/
```

**Depois:**
```env
AGIVIDEO_API_URL=https://otear-otear-editavideos.qc7qit.easypanel.host
```

Agora o código usa `.rstrip("/")` para garantir que não haja barras duplicadas.

### 2. check_video_status_tool não convertia URLs (CORRIGIDO)

A ferramenta `check_video_status_tool` retornava a resposta da API diretamente, sem converter URLs relativas.

**Antes:**
```python
def check_video_status_tool(job_id: str):
    response = httpx.get(url, headers=headers, timeout=10.0)
    return response.json()  # ❌ Retorna URL relativa
```

**Depois:**
```python
def check_video_status_tool(job_id: str):
    response = httpx.get(url, headers=headers, timeout=10.0)
    result = response.json()
    
    # Convert relative download_url to absolute if present
    if result.get("status") == "completed" and result.get("download_url"):
        download_url = result["download_url"]
        if download_url.startswith("/"):
            base_url = VIDEO_SERVICE_URL.rstrip("/")
            result["download_url"] = f"{base_url}{download_url}"
    
    return result  # ✅ Retorna URL absoluta
```

## Fluxo Correto Agora

1. **Usuário pede edição de vídeo**
2. **VideoDirectorAgent chama `edit_video_tool()`**
3. **`edit_video_tool()` faz polling e converte URL relativa → absoluta**
4. **Se timeout, agente usa `check_video_status_tool()` que também converte URL**
5. **Agente retorna URL completa ao usuário**

## Teste de Validação

Execute:
```bash
python test_url_fix.py
```

Resultado esperado:
```
URL original: /static/0af5a60a-8b57-4706-807b-84101c0041fc_final.mp4
URL convertida: https://otear-otear-editavideos.qc7qit.easypanel.host/static/0af5a60a-8b57-4706-807b-84101c0041fc_final.mp4
```

✅ **FUNCIONANDO CORRETAMENTE**

## Próximos Passos

1. **Reinicie os serviços** para aplicar as mudanças:
   ```bash
   docker-compose restart
   ```

2. **Teste com um agente real**:
   - Envie uma URL de vídeo para edição
   - Verifique se o agente retorna a URL completa
   - Teste se a URL funciona no navegador

3. **Verifique os logs** em caso de problema:
   - Procure por `[VIDEO TOOL]` nos logs
   - Verifique se a conversão está sendo feita: "URL relativa convertida: ... -> ..."

## Possíveis Problemas Remanescentes

Se ainda não funcionar, pode ser:

1. **Agente não está retornando a URL ao usuário**
   - Problema nas instruções do agente
   - Agente está "esquecendo" a URL na resposta

2. **Variável de ambiente não está sendo lida**
   - Verifique se `VIDEO_EDITOR_API_URL` está definida
   - Execute: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('VIDEO_EDITOR_API_URL'))"`

3. **Cache do Docker**
   - Reconstrua a imagem: `docker-compose build --no-cache`

## Logs para Monitorar

Procure por estas mensagens nos logs:

✅ **Sucesso:**
```
[VIDEO TOOL] ✓ Job {job_id} COMPLETO! URL relativa convertida: /static/... -> https://...
```

❌ **Problema:**
```
[VIDEO TOOL] Job completo mas sem download_url
```

## Resumo das Mudanças

| Arquivo | Mudança | Status |
|---------|---------|--------|
| `.env` | Removida barra final da URL | ✅ |
| `app/agents/agno_tools.py` (edit_video_tool) | Adicionado `.rstrip("/")` | ✅ |
| `app/agents/agno_tools.py` (check_video_status_tool) | Adicionada conversão de URL | ✅ |

## Conclusão

O código agora está preparado para:
1. ✅ Receber URLs relativas da API (`/static/...`)
2. ✅ Converter para URLs absolutas (`https://...`)
3. ✅ Retornar URLs completas e funcionais aos usuários

**Reinicie os serviços e teste!**
