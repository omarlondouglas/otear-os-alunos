# Smoke Tests — Copy Squad

> Testes rápidos para validar que o squad está operacional.

## Agent Activation Tests

- [ ] @copy-chief ativa e exibe greeting
- [ ] @ads-specialist ativa e exibe greeting
- [ ] @email-specialist ativa e exibe greeting
- [ ] @landing-specialist ativa e exibe greeting
- [ ] @social-specialist ativa e exibe greeting
- [ ] @copy-reviewer ativa e exibe greeting

## Command Tests

- [ ] *help exibe lista de comandos
- [ ] *style exibe copywriters disponíveis
- [ ] *exit sai do modo agente

## Briefing Validation Tests

- [ ] Briefing YAML válido aceito
- [ ] Briefing sem campo obrigatório retorna erro com campos faltantes
- [ ] Briefing em linguagem natural convertido para YAML
- [ ] Canal inválido retorna erro com canais aceitos

## Routing Tests

- [ ] canal=ads roteia para @ads-specialist
- [ ] canal=email roteia para @email-specialist
- [ ] canal=landing roteia para @landing-specialist
- [ ] canal=social roteia para @social-specialist
- [ ] copywriter especificado é respeitado (override)
- [ ] copywriter não especificado é selecionado via matrix

## Generation Tests

- [ ] Especialista gera draft com consulta à knowledge-base
- [ ] Draft inclui _draft_meta com sources e frameworks
- [ ] Draft segue estrutura do formato selecionado

## Review Tests

- [ ] Reviewer pontua 4 critérios com score numérico
- [ ] Copy boa aprovada com scores
- [ ] Copy fraca rejeitada com feedback acionável
- [ ] Feedback específico (não genérico)
