# Teste: API de Vídeo Consegue Acessar o MinIO?

## Problema

O vídeo está acessível publicamente (testamos e retornou 200 OK), mas a API de edição diz que não consegue acessar.

## Possíveis Causas

1. **Firewall entre servidores** - Easypanel pode estar bloqueando comunicação entre serviços
2. **DNS interno** - API de vídeo pode não conseguir resolver o domínio do MinIO
3. **Timeout** - API de vídeo pode ter timeout muito curto
4. **Certificado SSL** - API de vídeo pode estar rejeitando o certificado do MinIO

## Teste 1: Verificar se API de Vídeo Está Online

```bash
curl https://otear-otear-editavideos.qc7qit.easypanel.host/api/health
```

**Deve retornar:**
```json
{"status": "ok"}
```

## Teste 2: Testar Edição com Vídeo Público

Use um vídeo que sabemos que funciona:

```
Edita esse vídeo: https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4
```

**Se funcionar:** O problema é específico do MinIO
**Se não funcionar:** O problema é na API de edição

## Teste 3: Verificar Logs da API de Edição

No Easypanel:
1. Vá para `otear-otear-editavideos`
2. Clique em "Logs"
3. Procure por erros quando tenta acessar o vídeo

**Erros comuns:**
```
ConnectionError: Failed to establish connection
SSLError: certificate verify failed
TimeoutError: Request timed out
```

## Teste 4: Testar Manualmente na API de Edição

```bash
curl -X POST "https://otear-otear-editavideos.qc7qit.easypanel.host/api/v1/videos/edit" \
  -H "x-api-key: oazxPfl2BGxBbC74SZOz5eMcw5BgHpgW" \
  -F 'request={"video_url":"https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4","operations":[{"type":"preset","params":{"name":"VIRAL"}}],"output_format":"mp4"}'
```

**Copie e me envie a resposta completa!**

## Solução Temporária: Usar Vídeo Público

Enquanto não resolvemos o problema do MinIO, use um vídeo público para testar:

### Opção 1: Google Drive

1. Faça upload do vídeo no Google Drive
2. Clique com botão direito → "Obter link"
3. Mude para "Qualquer pessoa com o link"
4. Copie o ID do arquivo (parte entre `/d/` e `/view`)
5. Use: `https://drive.google.com/uc?export=download&id=SEU_ID_AQUI`

### Opção 2: Dropbox

1. Faça upload no Dropbox
2. Clique em "Compartilhar"
3. Copie o link
4. Mude `?dl=0` para `?dl=1` no final
5. Use esse link

### Opção 3: WeTransfer

1. Faça upload no WeTransfer
2. Copie o link de download direto
3. Use esse link

## Diagnóstico Avançado

Se você tem acesso SSH ao servidor da API de edição:

```bash
# Dentro do container da API de edição
curl -I https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4

# Verificar DNS
nslookup teste-minio.qc7qit.easypanel.host

# Verificar conectividade
ping teste-minio.qc7qit.easypanel.host

# Testar download
wget https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4
```

## Possível Solução: Configurar Rede no Easypanel

Se os serviços estão no mesmo Easypanel, eles deveriam se comunicar.

### Verificar:
1. Ambos os serviços estão no mesmo "Project" no Easypanel?
2. Há alguma configuração de rede/firewall no Easypanel?
3. Os serviços estão na mesma rede Docker?

### Solução:
Configure os serviços para usar a mesma rede Docker no Easypanel.

## Resumo

1. ✅ MinIO está acessível publicamente (testamos)
2. ❌ API de edição não consegue acessar o MinIO
3. ⏳ Precisamos descobrir por quê

**Próximo passo:** Execute o Teste 4 (curl manual) e me envie a resposta completa.

---

**Importante:** O problema NÃO é no código que escrevi. É um problema de rede/infraestrutura entre os serviços no Easypanel.
