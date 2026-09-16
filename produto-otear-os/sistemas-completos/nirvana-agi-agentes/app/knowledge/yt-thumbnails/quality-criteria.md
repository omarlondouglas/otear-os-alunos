# Quality Criteria — YouTube Thumbnail Prompts

## Critérios de Avaliação (1-10)

### 1. Clareza Visual (peso: alto)
A thumbnail gerada a partir do prompt comunicará sua mensagem em 1.8 segundos?
- 9-10: Mensagem instantaneamente clara, mesmo em 168×94px
- 7-8: Clara após 2-3 segundos de atenção
- 5-6: Precisa de esforço para entender
- 1-4: Confusa ou ambígua

### 2. Gatilho Emocional (peso: alto)
O prompt descreve elementos que provocam resposta emocional?
- 9-10: Expressão facial intensa + composição que gera curiosidade/choque
- 7-8: Tem elementos emocionais mas poderia ser mais intenso
- 5-6: Emoção genérica, sem especificidade
- 1-4: Sem gatilho emocional perceptível

### 3. Curiosity Gap (peso: alto)
A thumbnail cria uma pergunta que só se responde assistindo o vídeo?
- 9-10: Impossível não querer saber mais
- 7-8: Gera interesse moderado
- 5-6: Dá para imaginar o conteúdo sem clicar
- 1-4: Não gera nenhuma curiosidade

### 4. Contraste e Legibilidade (peso: médio)
O prompt especifica cores com contraste alto e elementos legíveis?
- 9-10: Cores vibrantes, alto contraste, vai funcionar em qualquer tamanho
- 7-8: Bom contraste, pode melhorar em detalhes
- 5-6: Contraste mediano, pode se perder em mobile
- 1-4: Cores apagadas ou sem especificação de contraste

### 5. Especificidade Técnica do Prompt (peso: médio)
O prompt inclui detalhes técnicos necessários para boa geração?
- 9-10: Aspect ratio, estilo, iluminação, câmera, resolução — tudo presente
- 7-8: Maioria dos detalhes técnicos presente
- 5-6: Faltam especificações importantes
- 1-4: Prompt vago sem detalhes técnicos

### 6. Composição e Layout (peso: médio)
O prompt descreve uma composição visualmente equilibrada?
- 9-10: Regra dos terços, hierarquia visual clara, espaço para texto overlay
- 7-8: Boa composição com pequenos ajustes possíveis
- 5-6: Composição genérica sem direção clara
- 1-4: Sem instruções de composição

### 7. Alinhamento com Canal (peso: médio)
O prompt reflete a identidade visual do canal @marlonlima_ia?
- 9-10: Tom, estilo e cores consistentes com o canal
- 7-8: Maioria alinhado, detalhes a ajustar
- 5-6: Genérico, poderia ser de qualquer canal
- 1-4: Conflita com a identidade do canal

### 8. Viabilidade de Geração (peso: baixo)
O prompt é realista para o modelo de IA especificado?
- 9-10: Dentro das capacidades do modelo, vai gerar bem
- 7-8: Provável boa geração com 1-2 tentativas
- 5-6: Pode precisar de múltiplas tentativas ou ajustes
- 1-4: Pede algo que o modelo não consegue fazer (ex: texto perfeito em Midjourney)

## Regras de Decisão

| Condição | Veredito |
|----------|----------|
| Média >= 7/10, nenhum critério abaixo de 4 | APROVAR |
| Média >= 7/10, critério não-crítico entre 4-6 | APROVAR COM REVISÕES |
| Média < 7/10 | REJEITAR |
| Qualquer critério abaixo de 4/10 | REJEITAR (trigger hard) |
| 3+ ciclos de revisão com mesmos problemas | ESCALAR para o usuário |

## Thresholds Específicos

- **Palavras no texto overlay**: máximo 4. Se o conceito tem mais de 4 palavras de texto, REJEITAR
- **Cores**: mínimo 2 cores vibrantes especificadas no prompt. Se não tem cores, REJEITAR
- **Aspect ratio**: deve ser 16:9. Se não especifica, REJEITAR
- **Expressão facial** (quando aplicável): deve ser específica (não "happy face", mas "wide-eyed surprise with open mouth"). Se genérica, pontuar baixo em Gatilho Emocional
