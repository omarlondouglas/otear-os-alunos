# Hermes + WhatsApp orquestrando O Tear Agentes

## Objetivo

Fluxo desejado:

```text
Usuario no WhatsApp/celular
  -> Hermes
  -> skill otear-orchestrator
  -> O Tear Agentes FastAPI
  -> ProjectOrchestrator/capabilities/tools/agentes
  -> resposta para Hermes
  -> resposta para WhatsApp
  -> interface do Tear mostra logs, biblioteca e resultados
```

O Hermes deve ser o orquestrador conversacional. O Tear deve ser a bancada de
execucao e visualizacao: pesquisa, referencias, roteiros, criacao, video,
biblioteca, memoria e logs.

## Endpoint principal para o Hermes

Use o endpoint de chat do Tear como porta de entrada padrao:

```http
POST /api/v1/chat
X-API-Key: <API_KEY>
Content-Type: application/json

{
  "message": "Crie um roteiro curto sobre IA para Instagram",
  "context": {
    "session_id": "whatsapp_5511999999999",
    "source": "whatsapp",
    "channel": "hermes"
  },
  "brand_id": "opcional"
}
```

Resposta:

```json
{
  "response": "texto de resposta para devolver ao usuario",
  "data": {
    "session_id": "whatsapp_5511999999999",
    "llm_provider": "claude-cli",
    "llm_label": "Claude CLI (OAuth - Conta Max)"
  }
}
```

Esse endpoint ja:

- aceita `X-API-Key` para integracoes como WhatsApp;
- passa pelo `ProjectOrchestrator`;
- registra logs em `/api/v1/logs`;
- salva assets detectados na biblioteca quando aplicavel;
- aceita `brand_id` e headers multi-tenant quando houver JWT/contexto.

## Endpoints auxiliares

### Health

```http
GET /api/v1/health
GET /api/v1/health/llm
```

Use antes de colocar o bot em producao.

### Logs para a interface

```http
GET /api/v1/logs?limit=100
```

A interface do Tear pode mostrar o desenvolvimento do trabalho por esse caminho.

### Biblioteca

```http
GET /api/v1/library
```

Use para listar assets gerados, roteiros salvos e resultados reutilizaveis.

### Agentes diretos, apenas como fallback

```http
POST /api/v1/agents/{agent_name}/run
```

Use somente quando o Hermes realmente precisar chamar um especialista especifico.
Para o WhatsApp, prefira `/api/v1/chat`, porque ele preserva a orquestracao do
Tear.

## Variaveis de ambiente no Hermes

```env
OTEAR_API_URL=https://seu-dominio.com
OTEAR_API_KEY=chave-da-integracao
OTEAR_DEFAULT_BRAND_ID=
```

Em desenvolvimento local:

```env
OTEAR_API_URL=http://localhost:8000
OTEAR_API_KEY=dev-secret-key
```

## Skill Hermes recomendada

A skill fica em:

```text
hermes_skills/otear-orchestrator/
  SKILL.md
  script.py
```

Uso esperado pelo Hermes:

```bash
python {SKILL_DIR}/script.py "Crie 5 ideias de carrossel para minha marca" \
  --session-id whatsapp_5511999999999 \
  --source whatsapp
```

Saida:

```json
{
  "response": "...",
  "data": {
    "session_id": "...",
    "llm_provider": "..."
  },
  "duration_ms": 1234
}
```

## Regra de orquestracao

O Hermes deve chamar o Tear quando o pedido envolver:

- pesquisa de tema/noticias;
- analise de referencias;
- extracao de modelo de criador/marca;
- roteiro, copy, legenda ou anuncios;
- carrossel, imagem, thumbnail ou capa;
- video, corte, legenda, transcricao ou render;
- memoria, biblioteca ou assets do projeto.

O Hermes pode responder sozinho quando for apenas conversa, alinhamento,
pergunta simples ou confirmacao.

## Observabilidade

Depois de cada pedido pelo WhatsApp:

1. a resposta volta para o usuario pelo Hermes;
2. o Tear registra a conversa em logs;
3. assets gerados aparecem na biblioteca quando a tool salvar ou retornar URL;
4. a interface React serve como painel de acompanhamento.

