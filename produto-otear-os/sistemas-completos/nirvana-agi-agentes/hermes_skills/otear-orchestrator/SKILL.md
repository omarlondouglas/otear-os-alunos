---
name: otear-orchestrator
description: "Delegue pedidos de criacao, pesquisa, roteiro, visual, video, referencias e memoria para O Tear Agentes via API."
version: 1.0.0
author: O Tear
license: MIT
metadata:
  hermes:
    tags: [otear, whatsapp, orchestration, content, agents]
    category: productivity
---

# otear-orchestrator

## Quando usar

Use esta skill quando o usuario pedir trabalho que deve aparecer ou ser executado
no O Tear Agentes:

- pesquisar temas, noticias, tendencias ou fontes;
- analisar referencias, criadores, perfis, imagens ou videos;
- extrair modelo de voz, visual, hooks ou estrutura;
- criar roteiro, copy, legenda, anuncio ou carrossel;
- gerar imagem, thumbnail, capa ou asset visual;
- editar video, transcrever, cortar, legendar ou renderizar;
- salvar ou consultar memoria, biblioteca e resultados do projeto.

Nao use para conversa simples, confirmacoes ou perguntas que o Hermes consegue
responder sem acionar o Tear.

## Contrato

A skill chama:

```text
POST {OTEAR_API_URL}/api/v1/chat
```

Headers:

```text
X-API-Key: {OTEAR_API_KEY}
Content-Type: application/json
```

Body:

```json
{
  "message": "pedido completo do usuario",
  "context": {
    "session_id": "whatsapp_...",
    "source": "whatsapp",
    "channel": "hermes"
  },
  "brand_id": "opcional"
}
```

## Variaveis obrigatorias

```env
OTEAR_API_URL=http://localhost:8000
OTEAR_API_KEY=...
```

Variavel opcional:

```env
OTEAR_DEFAULT_BRAND_ID=...
```

## Procedimento

1. Reescreva o pedido do usuario de forma auto-contida.
2. Preserve contexto importante da conversa: marca, publico, formato, prazo,
   canal e links.
3. Chame:

```bash
python {SKILL_DIR}/script.py "<pedido>" --session-id "<id-da-conversa>" --source whatsapp
```

4. Leia o JSON retornado.
5. Devolva ao usuario o campo `response`, nao o JSON cru.
6. Se houver `data.job_id`, `data.asset_url`, `data.download_url` ou campos
   equivalentes, mencione que o resultado tambem ficou disponivel na interface.

## Exemplos

```bash
python {SKILL_DIR}/script.py "Crie um roteiro de Reels sobre IA para dentistas, tom direto e provocativo" --session-id whatsapp_5511999999999
```

```bash
python {SKILL_DIR}/script.py "Analise esse perfil como referencia visual: https://instagram.com/exemplo" --session-id whatsapp_5511999999999
```

## Falhas

Se a API retornar erro ou timeout:

- avise o usuario que o Tear nao respondeu;
- sugira tentar novamente com um pedido mais curto;
- nao invente que o asset foi criado.

