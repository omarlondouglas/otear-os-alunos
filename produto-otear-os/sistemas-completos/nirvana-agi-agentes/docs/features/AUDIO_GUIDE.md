# 🎵 Guia de Trilha Sonora (Add Audio)

Guia completo sobre como adicionar música de fundo ou substituir o áudio do vídeo.

## 📋 Visão Geral

A operação `add_audio` permite:
- ✅ Adicionar música de fundo (mix com áudio original)
- ✅ Substituir áudio original completamente
- ✅ Controle preciso de volumes
- ✅ Fade in/out para transições suaves
- ✅ Loop automático para músicas curtas
- ✅ Timing customizado

## 🎯 Casos de Uso

### 1. Vlog com Música de Fundo
Adicione música sutil mantendo sua voz.

### 2. Montagem/Slideshow
Substitua áudio por música.

### 3. Tutorial com Intro Musical
Música nos primeiros segundos, depois só voz.

### 4. Podcast com Trilha
Música de fundo durante todo o episódio.

### 5. Vídeo Corporativo
Música profissional de fundo.

## 📝 Parâmetros Completos

### Obrigatórios
- `audio_url`: URL do arquivo de áudio (MP3, WAV, AAC, etc)

### Modo de Operação
- `mode`: Como o áudio será adicionado
  - `"mix"` - Mixa com áudio original (padrão)
  - `"replace"` - Substitui áudio original
  - `"background"` - Igual a mix (nome descritivo)

### Controle de Volume
- `audio_volume`: Volume da música 0.0-1.0 (padrão: 0.3)
- `original_volume`: Volume do áudio original 0.0-1.0 (padrão: 1.0)

### Efeitos
- `fade_in`: Fade in em segundos (padrão: 0)
- `fade_out`: Fade out em segundos (padrão: 0)
- `loop`: Repetir música (true/false, padrão: false)
- `start_time`: Quando a música começa em segundos (padrão: 0)

## 🎨 Exemplos Práticos

### Exemplo 1: Vlog Básico
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@vlog.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_audio",
      "params": {
        "audio_url": "https://example.com/musica.mp3",
        "mode": "mix",
        "audio_volume": 0.2
      }
    }]
  }'
```

### Exemplo 2: Montagem sem Áudio Original
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@montagem.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_audio",
      "params": {
        "audio_url": "https://example.com/trilha.mp3",
        "mode": "replace"
      }
    }]
  }'
```

### Exemplo 3: Intro Musical (10 segundos)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_audio",
        "params": {
          "audio_url": "https://example.com/intro.mp3",
          "mode": "replace",
          "start_time": 0,
          "fade_out": 2
        }
      }
    ]
  }'
```

**Nota:** Para intro + conteúdo, você precisaria de duas operações ou editar o vídeo em partes.

### Exemplo 4: Música em Loop
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_longo.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_audio",
      "params": {
        "audio_url": "https://example.com/musica_curta.mp3",
        "mode": "mix",
        "audio_volume": 0.25,
        "loop": true,
        "fade_in": 1,
        "fade_out": 2
      }
    }]
  }'
```

### Exemplo 5: Reduzir Voz + Música Alta
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_audio",
      "params": {
        "audio_url": "https://example.com/musica.mp3",
        "mode": "mix",
        "audio_volume": 0.6,
        "original_volume": 0.4
      }
    }]
  }'
```

## 🎚️ Guia de Volumes

### Música de Fundo Sutil
```json
{
  "audio_volume": 0.15,
  "original_volume": 1.0
}
```
**Uso:** Tutoriais, palestras, entrevistas

### Música de Fundo Balanceada
```json
{
  "audio_volume": 0.3,
  "original_volume": 1.0
}
```
**Uso:** Vlogs, vídeos casuais (recomendado)

### Música em Destaque
```json
{
  "audio_volume": 0.5,
  "original_volume": 0.6
}
```
**Uso:** Montagens, vídeos artísticos

### Música Dominante
```json
{
  "audio_volume": 0.8,
  "original_volume": 0.3
}
```
**Uso:** Clipes musicais, vídeos emocionais

## 💡 Dicas Profissionais

### 1. Escolha da Música
- **Instrumental**: Melhor para não competir com voz
- **Ritmo**: Combine com o ritmo do vídeo
- **Duração**: Idealmente próxima à duração do vídeo
- **Qualidade**: Mínimo 128kbps, ideal 192kbps+

### 2. Volumes Recomendados por Tipo

| Tipo de Vídeo | audio_volume | original_volume |
|---------------|--------------|-----------------|
| Tutorial | 0.15-0.20 | 1.0 |
| Vlog | 0.20-0.30 | 1.0 |
| Entrevista | 0.10-0.15 | 1.0 |
| Montagem | N/A (use replace) | N/A |
| Corporativo | 0.20-0.25 | 1.0 |
| Podcast | 0.15-0.20 | 1.0 |

### 3. Fade In/Out
- **Fade In**: 1-3 segundos (suave)
- **Fade Out**: 2-4 segundos (mais longo)
- **Sempre use fade** para evitar cortes abruptos

### 4. Loop
- Use quando música < vídeo
- Escolha músicas que fazem loop naturalmente
- Evite músicas com final marcante

### 5. Timing
- `start_time: 0` - Música desde o início
- `start_time: 5` - Música após 5 segundos
- Combine com fade_in para entrada suave

## 🔄 Combinando com Outras Operações

### Normalizar + Música
```json
{
  "operations": [
    {
      "type": "adjust_volume",
      "params": {"normalize": true}
    },
    {
      "type": "add_audio",
      "params": {
        "audio_url": "...",
        "mode": "mix",
        "audio_volume": 0.25
      }
    }
  ]
}
```

### Música + Legendas
```json
{
  "operations": [
    {
      "type": "add_audio",
      "params": {
        "audio_url": "...",
        "mode": "mix",
        "audio_volume": 0.2
      }
    },
    {
      "type": "auto_subtitle",
      "params": {"language": "pt", "model": "small"}
    }
  ]
}
```

### Pipeline Completo
```json
{
  "operations": [
    {"type": "trim", "params": {"start": 0, "end": 60}},
    {"type": "adjust_volume", "params": {"normalize": true}},
    {"type": "add_audio", "params": {"audio_url": "...", "audio_volume": 0.25}},
    {"type": "auto_subtitle", "params": {"language": "pt"}},
    {"type": "add_text_overlay", "params": {"text": "Meu Vídeo", "position": "top"}}
  ]
}
```

## ⚠️ Limitações e Cuidados

### 1. Direitos Autorais
- ⚠️ Use apenas música livre de direitos
- ⚠️ Ou música licenciada para uso comercial
- ✅ Fontes: YouTube Audio Library, Epidemic Sound, Artlist

### 2. Formatos Suportados
- ✅ MP3 (recomendado)
- ✅ WAV
- ✅ AAC
- ✅ M4A
- ✅ OGG

### 3. Duração
- Se música > vídeo: Música será cortada
- Se música < vídeo: Use `loop: true`

### 4. Qualidade
- Mínimo: 128kbps
- Recomendado: 192kbps
- Profissional: 320kbps

### 5. Performance
- Arquivos grandes demoram mais para baixar
- Use URLs rápidas e confiáveis
- Considere hospedar em CDN

## 🧪 Testando

```bash
chmod +x test_add_audio.sh
# Edite o script e substitua a URL do áudio
./test_add_audio.sh
```

## 📚 Recursos de Música Livre

### Gratuitas
- YouTube Audio Library
- Free Music Archive
- Incompetech
- Bensound

### Pagas (Licença)
- Epidemic Sound
- Artlist
- AudioJungle
- PremiumBeat

---

**Adicione trilhas sonoras profissionais aos seus vídeos!** 🎵
