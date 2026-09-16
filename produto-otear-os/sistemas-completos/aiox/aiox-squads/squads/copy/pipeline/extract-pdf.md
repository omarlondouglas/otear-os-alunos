# Pipeline: Extract PDF

## Engine Primária: Docling

```bash
# Instalação (one-time)
pip install docling

# Conversão
docling convert {input.pdf} --output {output_dir} --format md
```

### Quando Funciona Bem
- PDFs com texto digital (não escaneado)
- Documentos com estrutura clara (headings, listas)
- Livros e cursos em formato digital

### Quando Falha
- PDFs escaneados (imagens de texto)
- Direct mail antigo digitalizado
- PDFs com layout complexo (colunas, tabelas)

## Engine Fallback: Gemini 2.5 Pro

Acionar quando Docling retorna markdown com < 50% de texto legível.

```
Prompt para Gemini:
"Converta este PDF para markdown estruturado. Preserve:
- Toda a estrutura (headings, listas, parágrafos)
- Todo o texto visível
- Descrição de elementos visuais relevantes
- Formato markdown limpo e legível

Retorne APENAS o markdown, sem comentários."
```

### Critério de Fallback
- Markdown do Docling tem < 50% de texto legível
- Mais de 30% de caracteres são artefatos de OCR
- Estrutura não preservada (tudo em um bloco)

## Engine de Último Recurso: Curadoria Manual

Se ambos falharem:
- Mover para `_review/` com log
- Notificar usuário: "Arquivo {name} requer curadoria manual"

## Output Esperado

Arquivo `.md` com:
- Texto completo e legível
- Estrutura preservada
- Pronto para enriquecimento de metadados
