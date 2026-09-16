---
id: gerador-imagens
type: step
execution: inline
agent: gerador-imagens
label: "Gerar imagens com IA via Codex / GPT Image 2"
inputFile: "squads/noticias-carrossel-ia/output/visual-concept.md"
outputFile: "squads/noticias-carrossel-ia/output/images/"
---

# Gerador de Imagens â€” Gerar imagens via Codex / GPT Image 2

## Contexto

Voce recebeu o visual-concept.md com prompts prontos para geracao de imagem (ou mensagem de banco R2).

## Processo

### FAST EXIT (verificar ANTES de qualquer trabalho)

1. Ler o visual-concept.md
2. Se contiver "banco R2 em uso" ou "nenhuma geraÃ§Ã£o de IA necessÃ¡ria":
   Escrever APENAS: `GERADOR: banco R2 em uso â€” sem geraÃ§Ã£o de imagens.`
   E PARAR. NÃ£o chamar nenhuma API. NÃ£o carregar .env. Apenas salvar e sair.

### GERAÃ‡ÃƒO (sÃ³ se visual-concept.md tiver prompts reais)

1. Carregar variaveis: `[ -f .env ] && set -a && source .env && set +a || true`
2. Verificar se o Codex local esta autenticado. Nao exigir `.env` quando o usuario ja esta logado no Codex.
   - Comando util: `codex doctor` ou `codex login status` quando disponivel
   - `CHATGPT_BRIDGE_URL` e opcional; nao deve ser requisito quando existe sessao Codex local
3. Para cada prompt no visual-concept.md, verificar se tem "Foto referencia:" com caminho valido

### PROVIDER OBRIGATÃ“RIO

1. **Codex/ChatGPT Image 2** pela sessao local autenticada do Codex. O usuÃ¡rio definiu esse fluxo como padrÃ£o para imagens.
2. Se o Codex local nao estiver autenticado/disponivel, PARAR e registrar: `Codex/gpt-image-2 indisponÃ­vel: reautentique o Codex local`.
3. NÃ£o usar Gemini automaticamente. Gemini/OpenAI sÃ³ entram se o usuÃ¡rio pedir fallback explicitamente naquela execuÃ§Ã£o.

Se nÃ£o houver `.env`, isso nÃ£o Ã© erro. O critÃ©rio Ã© a sessÃ£o Codex local estar logada. NÃ£o gere imagem com Gemini apenas para "terminar".

#### Template 0 â€” Provider compartilhado do agi-agentes (preferido quando disponÃ­vel)

Se o repositÃ³rio `{OTEAR_SO_ROOT}/referencias/nirvana-agi-agentes` estiver disponÃ­vel, o gerador pode reaproveitar o padrÃ£o jÃ¡ implementado em `app/agents/agno_tools.py`, funÃ§Ã£o `generate_image_tool`, que tenta:
`chatgpt-bridge/gpt-image-2 -> OpenAI -> Google`.

Use esse padrÃ£o antes de cair nos templates manuais abaixo.

#### Template A â€” SEM foto de referencia (apenas texto)

Usar quando o slide NAO tem foto de referencia ou o campo diz "NENHUMA":

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "PROMPT_AQUI"}]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
  }' | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
for part in data.get('candidates', [{}])[0].get('content', {}).get('parts', []):
    if 'inlineData' in part:
        img_data = base64.b64decode(part['inlineData']['data'])
        with open('OUTPUT_PATH', 'wb') as f:
            f.write(img_data)
        print('Image saved')
        break
"
```

#### Template B â€” COM foto de referencia (texto + imagem multimodal)

Usar quando o slide TEM foto de referencia valida (URL do Supabase Storage retornada pelo conceituador-visual).
A foto e enviada como inlineData junto com o prompt para o Gemini reconhecer a pessoa e manter semelhanca.

```bash
# Baixar foto de referencia do Supabase Storage e converter para base64
REF_URL="https://xxx.supabase.co/storage/v1/object/public/banco-pessoas/SLUG/reference.jpg"
curl -sL -o /tmp/ref_photo.jpg "$REF_URL"
REF_BASE64=$(base64 -w 0 /tmp/ref_photo.jpg 2>/dev/null || base64 -i /tmp/ref_photo.jpg 2>/dev/null)

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"contents\": [{\"parts\": [
      {\"text\": \"Use this reference photo of the person to maintain physical resemblance. PROMPT_AQUI\"},
      {\"inlineData\": {\"mimeType\": \"image/jpeg\", \"data\": \"$REF_BASE64\"}}
    ]}],
    \"generationConfig\": {\"responseModalities\": [\"TEXT\", \"IMAGE\"]}
  }" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
for part in data.get('candidates', [{}])[0].get('content', {}).get('parts', []):
    if 'inlineData' in part:
        img_data = base64.b64decode(part['inlineData']['data'])
        with open('OUTPUT_PATH', 'wb') as f:
            f.write(img_data)
        print('Image saved with reference')
        break
"
```

**IMPORTANTE**: No prompt enviado com foto de referencia, incluir no inicio:
`"Use this reference photo of the person to maintain accurate physical resemblance in the generated image. The person should look like the reference but in the style described below: "`
seguido do prompt original do conceito visual.

4. Verificar tamanho > 0, ler imagem para verificacao visual
5. Esperar 2 segundos entre chamadas (rate limit)
6. Se qualidade ruim, ajustar prompt e regenerar (max 2 tentativas)
7. Listar todas as imagens geradas ao final

## Veto Conditions

- Nenhuma imagem gerada (quando prompts existiam)
- Imagem com artefatos visuais obvios nao corrigidos
- Arquivo de imagem com 0 bytes
