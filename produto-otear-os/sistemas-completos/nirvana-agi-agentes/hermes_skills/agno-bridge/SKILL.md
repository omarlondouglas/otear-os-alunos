---
name: agno-bridge
description: "Delegue uma tarefa para um dos agentes especialistas do O Tear via API HTTP."
version: 1.1.0
author: O Tear
license: MIT
metadata:
  hermes:
    tags: [otear, delegation, multi-agent, api]
    category: productivity
---

# agno-bridge - Delegacao para agentes via API

Esta skill chama os endpoints HTTP do O Tear. Ela nao importa codigo Python do
app diretamente. O Hermes opera como cliente/orquestrador externo, enquanto o
O Tear continua responsavel por autenticacao, contexto multiusuario, logs,
execucao de tools e armazenamento.

## Quando usar

Use quando a solicitacao do cliente exigir um agente especialista:

- Edicao/analise de video -> `beast` ou `nolan`
- Roteiro de video viral -> `olivetto`
- Copy, textos e hooks -> `ogilvy`
- Carrossel Instagram -> `garyv`
- Geracao de imagem/design -> `scher`
- Modelagem de estilo de criador -> `erico`
- Branding/PDF/PPTX -> `neumeier`
- Anuncio Meta Ads -> `clara_copy`
- News-to-carousel -> `news_carousel`
- Thumbnail YouTube -> `youtuber_thumbnail`
- Capa neuro-visual -> `neuro_cover`
- Moodboard/análise visual Instagram -> `insta_visual_ref`

Nao use para conversa simples, confirmacoes ou tarefas que o Hermes consegue
resolver com memoria local.

## Contrato

O script chama:

```text
POST {OTEAR_API_URL}/api/v1/agents/{agent_name}/run
X-API-Key: {OTEAR_API_KEY}
Content-Type: application/json
```

Body:

```json
{
  "task": "instrucao auto-contida",
  "user_id": "opcional",
  "context": {
    "org_id": "opcional",
    "brand_id": "opcional"
  }
}
```

## Variaveis

```env
OTEAR_API_URL=http://localhost:8000
OTEAR_API_KEY=...
OTEAR_DEFAULT_USER_ID=
OTEAR_DEFAULT_ORG_ID=
OTEAR_DEFAULT_BRAND_ID=
OTEAR_TIMEOUT_S=150
```

## Procedimento

1. Escolha o agente correto.
2. Reescreva o pedido como uma instrucao clara e auto-contida.
3. Chame:

```bash
python {SKILL_DIR}/script.py <agent_name> "<task>"
```

Exemplo:

```bash
python {SKILL_DIR}/script.py beast "Encontre 5 clipes virais no video em https://example.com/video.mp4 com hook forte"
```

4. Leia o JSON retornado.
5. Apresente o campo `result` ao cliente, nao o JSON cru.

## Cuidados

- Use apenas os nomes canonicos listados acima.
- Nao chame multiplos agentes em sequencia sem necessidade.
- Nao injete USER.md/MEMORY.md manualmente; o servidor injeta contexto quando aplicavel.
- Se o endpoint demorar ou falhar, informe que o O Tear nao respondeu e peça para tentar novamente.
