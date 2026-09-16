# Pipeline: Extract Video

## Engine: Whisper / Groq API

### Transcrição

```bash
# Via Groq API (rápido + barato)
curl -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@{input.mp4}" \
  -F "model=whisper-large-v3" \
  -F "response_format=verbose_json" \
  -F "language=pt"
```

### Segmentação por Blocos Temáticos

Após transcrição bruta, segmentar por blocos:

1. **Detectar mudanças de tópico** via timestamps e conteúdo
2. **Criar headings** para cada bloco temático
3. **Preservar timestamps** como referência

### Formato de Output

```markdown
# Transcrição: {título do vídeo}

Source: {nome do arquivo}
Duration: {duração}
Language: {idioma}

## Bloco 1: {tópico} [00:00 - 05:30]

{texto transcrito}

## Bloco 2: {tópico} [05:30 - 12:15]

{texto transcrito}

...
```

### Formatos de Vídeo Aceitos
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
- Extrair áudio primeiro se necessário: `ffmpeg -i {input} -vn -acodec mp3 {output.mp3}`

### Limitações
- Groq: máximo 25MB por arquivo
- Para arquivos maiores: dividir com ffmpeg antes de transcrever
- Qualidade depende do áudio original (background noise reduz precisão)

## Output Esperado

Arquivo `.md` com:
- Transcrição completa
- Segmentação por blocos temáticos
- Timestamps de referência
- Pronto para enriquecimento
