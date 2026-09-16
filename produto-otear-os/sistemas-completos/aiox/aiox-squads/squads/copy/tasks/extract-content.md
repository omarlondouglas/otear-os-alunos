# Task: extract-content

```yaml
id: extract-content
version: "1.0.0"
title: "Extract Content from Source Files"
description: >
  Converte arquivos de origem (PDF, vídeo, imagem) para markdown.
  Detecta formato, seleciona engine, executa conversão. Fallback
  automático quando engine primária falha.
elicit: false
owner: copy-chief
executor: copy-chief
outputs:
  - Arquivos markdown convertidos
  - Log de conversão (sucesso/falha por arquivo)
```

## When This Task Runs

- Novos arquivos detectados na pasta de entrada
- Usuário dispara *extract manualmente
- Pipeline de extração batch

## Extraction Steps

### Step 1: Detect New Files

Escanear pasta de entrada por novos arquivos:
```
Glob knowledge-base/_inbox/**/*
```

Classificar por formato:
- `.pdf` → PDF pipeline
- `.mp4`, `.mov`, `.avi`, `.mkv` → Video pipeline
- `.png`, `.jpg`, `.jpeg`, `.webp` → Image pipeline

### Step 2: Extract by Format

#### PDF → Markdown (Docling)
```bash
# Engine primária
docling convert {input.pdf} --output {output.md}

# Fallback: Gemini 2.5 Pro (para scans, OCR ruim)
# Acionar se Docling retornar markdown com < 50% de texto legível
```

#### Video → Markdown (Whisper/Groq)
```bash
# Transcrição via Whisper/Groq API
# Input: arquivo de vídeo
# Output: transcrição segmentada por blocos temáticos
```

#### Image → Markdown (Claude Vision)
```
# Usar Read tool nativo para análise de imagem
# Extrair: texto visível, layout, técnicas visuais, composição
# Output: descrição estruturada em markdown
```

### Step 3: Quality Check (Pre-Enrichment)

Para cada arquivo convertido:
- Markdown legível? (não é lixo de OCR)
- Estrutura preservada? (headings, listas, parágrafos)
- Texto completo? (não cortou no meio)

SE qualidade insuficiente:
- Tentar fallback engine
- SE fallback também falha → marcar para curadoria manual

### Step 4: Output

```yaml
extraction_log:
  total_files: N
  success: N
  failed: N
  manual_review: N
  files:
    - name: "{filename}"
      format: "pdf|video|image"
      engine: "docling|whisper|vision|gemini-fallback"
      status: "success|failed|manual_review"
      output_path: "{path to .md}"
```
