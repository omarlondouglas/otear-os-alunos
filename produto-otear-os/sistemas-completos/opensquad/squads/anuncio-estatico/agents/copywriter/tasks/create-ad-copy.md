---
task: "Create Ad Copy"
order: 1
input: |
  - ad-brief.md: Brief com produto, objetivo, ângulo emocional e info adicional
  - tone-of-voice.md: Opções de tom de voz disponíveis
  - company.md: Contexto da empresa e público-alvo
output: |
  - ad-copy.md: Copy completa com headline, corpo, CTA e direção visual
---

# Create Ad Copy

Cria a copy completa para um anúncio estático de Meta Ads, incluindo diagnóstico de público, headline, corpo persuasivo, CTA e direção visual para o designer.

## Process

1. **Diagnosticar**: Ler o brief e identificar nível de consciência do público (Schwartz), framework de copy mais adequado (AIDA, PAS, BAB, Hook-Story-Offer), e driver psicológico dominante.
2. **Selecionar tom**: Ler tone-of-voice.md, recomendar o tom mais adequado ao brief e ângulo emocional escolhido.
3. **Criar 3 headlines**: Escrever 3 opções de headline usando abordagens emocionais diferentes. Cada headline com max 8 palavras, específica ao produto.
4. **Apresentar headlines**: Mostrar as 3 opções ao contexto para seleção.
5. **Escrever corpo**: Com a headline definida, escrever max 4 linhas de corpo. Cada linha = uma proposição de valor independente.
6. **Criar CTA**: Verbo imperativo + benefício específico. Ex: "Garanta sua vaga na mentoria"
7. **Direção visual**: Definir destaques (palavras em cor), layout sugerido, elementos extras (selos, ícones).

## Output Format

```yaml
headline: "..."
corpo:
  - "Linha 1..."
  - "Linha 2..."
  - "Linha 3..."
  - "Linha 4..."
cta: "..."
diagnostico:
  consciencia: "..."
  framework: "..."
  tom: "..."
  gatilho: "..."
direcao_visual:
  destaques: ["palavra1", "palavra2"]
  layout: "..."
  cores_sugeridas: ["#hex1", "#hex2"]
  elementos_extras: ["..."]
```

## Output Example

> Use as quality reference, not as rigid template.

```
# Ad Copy — Mentoria Sua Agência de IA

## Diagnóstico
- Nível de consciência: Solution-aware
- Framework: PAS (Problem, Agitate, Solution)
- Tom de voz: Direto e Prático
- Gatilho principal: Oportunidade

## Copy Final

HEADLINE: 12 agentes de IA prontos em 8 semanas

CORPO:
Enquanto agências gastam meses tentando entender IA,
você sai com 12 agentes funcionando.
SDR, atendimento, follow-up, conteúdo e mais.
Sem programação. Suporte ao vivo toda semana.

CTA: Garanta sua vaga na mentoria →

## Direção Visual
- Destaque: "12" e "8 semanas" em verde neon (#A3F12E)
- Layout: headline topo, corpo centro, CTA base
- Cores sugeridas: verde neon para números, branco para texto
- Elementos extras: ícones minimalistas dos agentes
```

## Quality Criteria

- [ ] Diagnóstico completo (consciência + framework + tom + gatilho)
- [ ] Headline max 8 palavras, específica
- [ ] Corpo max 4 linhas, uma proposição de valor por linha
- [ ] CTA com verbo imperativo + benefício
- [ ] Direção visual com destaques e layout
- [ ] Zero travessões na copy

## Veto Conditions

Reject and redo if ANY are true:
1. Headline genérica que poderia ser de qualquer empresa do nicho
2. Copy contém travessões (—) em qualquer parte do texto
3. CTA sem verbo imperativo
