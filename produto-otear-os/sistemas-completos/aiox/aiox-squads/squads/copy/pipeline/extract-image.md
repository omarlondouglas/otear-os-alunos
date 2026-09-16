# Pipeline: Extract Image

## Engine: Claude Vision (Read tool nativo)

### Processo

1. **Ler imagem** via Read tool do Claude Code
2. **Analisar** com prompt estruturado
3. **Gerar markdown** descritivo

### Prompt de Análise

```
Analise esta peça publicitária/de copywriting e extraia:

1. TEXTO VISÍVEL: Todo texto legível na imagem, preservando hierarquia
   (headline, subheadline, body, CTA, fine print)

2. LAYOUT: Estrutura visual da peça
   - Disposição dos elementos
   - Hierarquia visual
   - Uso de espaço em branco

3. TÉCNICAS VISUAIS: Técnicas de design usadas para persuasão
   - Contraste e ênfase
   - Direcionamento do olhar
   - Uso de cores para emoção

4. TÉCNICAS DE COPY: Padrões de copywriting identificáveis
   - Tipo de hook usado
   - Framework de estrutura
   - Técnicas de persuasão

5. COMPOSIÇÃO: Como texto e visual trabalham juntos

Retorne em formato markdown estruturado.
```

### Formato de Output

```markdown
# Análise: {descrição da peça}

Source: {nome do arquivo}
Type: {direct-mail|ad|sales-letter|packaging|etc}

## Texto Extraído

### Headline
{headline}

### Subheadline
{subheadline}

### Body
{body text}

### CTA
{call to action}

## Análise Técnica

### Layout
{descrição do layout}

### Técnicas de Copy
- {técnica 1}
- {técnica 2}

### Técnicas Visuais
- {técnica 1}
- {técnica 2}
```

### Formatos Aceitos
- `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`

### Limitações
- Imagens de baixa resolução reduzem qualidade da extração
- Texto muito pequeno pode não ser legível
- Layouts muito complexos podem perder hierarquia

## Output Esperado

Arquivo `.md` com:
- Todo texto visível extraído
- Análise de layout e técnicas
- Pronto para enriquecimento
