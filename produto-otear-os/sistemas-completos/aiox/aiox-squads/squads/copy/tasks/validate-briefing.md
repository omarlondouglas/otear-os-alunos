# Task: validate-briefing

```yaml
id: validate-briefing
version: "1.0.0"
title: "Validate Copy Briefing"
description: >
  Valida briefing YAML contra schema obrigatório. Converte linguagem
  natural para YAML se necessário. Retorna erro com campos faltantes
  ou briefing validado pronto para routing.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - Briefing YAML validado
  - Ou erro com campos faltantes listados
```

## When This Task Runs

- Usuário ou agente envia briefing para o Copy Squad
- Copy Chief recebe request via *generate
- Briefing em YAML ou linguagem natural

## Validation Steps

### Step 1: Detect Input Format

- SE input contém chaves YAML (produto:, publico:, canal:) → parse YAML direto
- SE input é texto livre → extrair campos via NL-to-YAML rules do Copy Chief
- SE input é ambíguo → solicitar esclarecimento

### Step 2: Validate Required Fields

| Campo | Obrigatório | Validação |
|-------|-------------|-----------|
| `produto` | SIM | String não vazia, descreve produto/serviço |
| `publico` | SIM | String não vazia, específico (não "todos") |
| `canal` | SIM | Enum: ads, email, landing, social |

### Step 3: Validate Optional Fields

| Campo | Obrigatório | Validação |
|-------|-------------|-----------|
| `tom` | NÃO | Enum: urgente, educativo, emocional, autoritativo |
| `copywriter` | NÃO | Enum: halbert, schwartz, ogilvy, kennedy |
| `contexto` | NÃO | String livre |
| `formato_especifico` | NÃO | Enum por canal (ver abaixo) |
| `quantidade` | NÃO | Integer >= 1 (default: 1) |

### Formatos Específicos por Canal

| Canal | Formatos Aceitos |
|-------|-----------------|
| ads | meta-ad, google-ad, tiktok-ad, display-ad |
| email | sequence, broadcast, nurture, welcome |
| landing | sales-page, vsl, opt-in |
| social | carrossel, thread, post, script |

### Step 4: Return Result

- SE válido → retornar briefing YAML completo (com defaults preenchidos)
- SE inválido → retornar erro:

```
BRIEFING INVÁLIDO

Campos faltantes:
- [campo]: [descrição do que é necessário]

Campos inválidos:
- [campo]: valor "[valor]" não aceito. Valores aceitos: [lista]

Corrija e reenvie.
```
