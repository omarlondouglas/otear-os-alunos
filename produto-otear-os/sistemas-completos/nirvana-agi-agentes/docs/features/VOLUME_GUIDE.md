# 🔊 Guia de Ajuste de Volume

Guia completo sobre como ajustar o volume do áudio em seus vídeos.

## 📋 Visão Geral

A operação `adjust_volume` permite:
- ✅ Aumentar ou diminuir o volume manualmente
- ✅ Normalizar áudio automaticamente
- ✅ Ajustar para padrões de streaming (YouTube, Spotify, etc)
- ✅ Corrigir áudio muito baixo ou muito alto

## 🎚️ Dois Modos de Operação

### 1. Ajuste Manual (`volume`)
Controle preciso do volume usando um multiplicador.

```json
{
  "type": "adjust_volume",
  "params": {
    "volume": 2.0
  }
}
```

### 2. Normalização Automática (`normalize`)
Ajusta automaticamente para um nível ideal.

```json
{
  "type": "adjust_volume",
  "params": {
    "normalize": true,
    "target_level": -16
  }
}
```

## 📊 Guia de Valores (Volume Manual)

| Valor | Efeito | Exemplo de Uso |
|-------|--------|----------------|
| 0.1 | 10% do original | Música de fundo muito sutil |
| 0.3 | 30% do original | Música de fundo |
| 0.5 | Metade do volume | Reduzir áudio alto |
| 0.7 | 70% do original | Redução leve |
| 1.0 | Sem mudança | Original |
| 1.5 | +50% | Aumentar levemente |
| 2.0 | Dobro | Áudio baixo |
| 3.0 | Triplo | Áudio muito baixo |
| 5.0 | 5x mais alto | Áudio extremamente baixo |

## ⚠️ Cuidados com Volume Alto

- **volume > 2.0**: Pode causar distorção
- **volume > 5.0**: Quase sempre causa distorção
- **Recomendação**: Use normalização para áudio muito baixo

## 🎯 Normalização (LUFS)

LUFS = Loudness Units relative to Full Scale (padrão da indústria)

### Níveis Recomendados

| Plataforma | Target Level | Uso |
|------------|--------------|-----|
| YouTube | -14 LUFS | Vídeos em geral |
| Spotify | -14 LUFS | Música |
| Apple Music | -16 LUFS | Música |
| Podcast | -16 a -19 LUFS | Falado |
| Broadcast TV | -23 LUFS | TV (EBU R128) |
| Streaming Geral | -16 LUFS | Padrão (recomendado) |

### Como Funciona

A normalização:
1. Analisa o áudio completo
2. Calcula o volume médio (loudness)
3. Ajusta para o nível alvo
4. Previne distorção (limiting)

## 📝 Exemplos Práticos

### Exemplo 1: Vídeo com Áudio Baixo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_baixo.mp4" \
  -F 'request={
    "operations": [{
      "type": "adjust_volume",
      "params": {
        "volume": 2.0
      }
    }]
  }'
```

### Exemplo 2: Vídeo com Áudio Alto
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video_alto.mp4" \
  -F 'request={
    "operations": [{
      "type": "adjust_volume",
      "params": {
        "volume": 0.5
      }
    }]
  }'
```

### Exemplo 3: Normalizar para YouTube
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "adjust_volume",
      "params": {
        "normalize": true,
        "target_level": -14
      }
    }]
  }'
```

### Exemplo 4: Normalizar para Podcast
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@podcast.mp4" \
  -F 'request={
    "operations": [{
      "type": "adjust_volume",
      "params": {
        "normalize": true,
        "target_level": -18
      }
    }]
  }'
```

### Exemplo 5: Pipeline Completo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@raw.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "trim",
        "params": {"start": 0, "end": 60}
      },
      {
        "type": "adjust_volume",
        "params": {"normalize": true}
      },
      {
        "type": "remove_silence",
        "params": {"noise": "-30dB", "duration": 0.5}
      },
      {
        "type": "auto_subtitle",
        "params": {"language": "pt", "model": "small"}
      }
    ]
  }'
```

## 🤔 Quando Usar Cada Modo

### Use Volume Manual quando:
- ✅ Você sabe exatamente quanto quer ajustar
- ✅ Precisa de controle preciso
- ✅ Quer processar mais rápido
- ✅ Está ajustando música de fundo

### Use Normalização quando:
- ✅ Não sabe o nível atual do áudio
- ✅ Quer consistência entre vídeos
- ✅ Está preparando para plataforma específica
- ✅ Quer evitar distorção
- ✅ Áudio tem variações grandes

## 💡 Dicas Profissionais

### 1. Teste Primeiro
Sempre teste com um trecho curto antes de processar vídeo completo.

### 2. Normalização é Mais Segura
Se em dúvida, use normalização ao invés de volume manual alto.

### 3. Combine com Remove Silence
Para podcasts/entrevistas, normalize ANTES de remover silêncios:
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true}},
    {"type": "remove_silence", "params": {...}}
  ]
}
```

### 4. Áudio Muito Baixo
Se `volume: 2.0` não for suficiente, use normalização:
```json
{"normalize": true, "target_level": -14}
```

### 5. Música de Fundo
Para adicionar música de fundo sutil:
```json
{"volume": 0.2}
```

## 🔍 Troubleshooting

### Problema: Áudio distorcido após aumentar volume
**Solução:** Use normalização ao invés de volume manual alto.

### Problema: Normalização deixou áudio muito baixo
**Solução:** Use target_level mais alto (ex: -14 ao invés de -23).

### Problema: Áudio ainda muito baixo após normalização
**Solução:** O áudio original pode ter ruído. Tente:
1. Limpar ruído primeiro
2. Usar volume manual após normalização

### Problema: Processamento muito lento
**Solução:** Normalização é mais lenta. Use volume manual se velocidade for crítica.

## 📊 Comparação: Manual vs Normalização

| Aspecto | Volume Manual | Normalização |
|---------|---------------|--------------|
| **Velocidade** | ⚡ Rápido | 🐢 Mais lento |
| **Controle** | 🎯 Preciso | 🤖 Automático |
| **Segurança** | ⚠️ Pode distorcer | ✅ Previne distorção |
| **Consistência** | ❌ Varia | ✅ Consistente |
| **Uso** | Ajustes simples | Produção profissional |

## 🎬 Casos de Uso Reais

### Vlog do YouTube
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true, "target_level": -14}},
    {"type": "remove_silence", "params": {"noise": "-30dB", "duration": 0.4}},
    {"type": "auto_subtitle", "params": {"language": "pt", "model": "small"}}
  ]
}
```

### Podcast
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true, "target_level": -18}},
    {"type": "remove_silence", "params": {"noise": "-35dB", "duration": 1.5}}
  ]
}
```

### Tutorial/Screencast
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"normalize": true, "target_level": -16}},
    {"type": "auto_subtitle", "params": {"language": "pt", "model": "base"}}
  ]
}
```

### Vídeo com Música de Fundo (a adicionar depois)
```json
{
  "operations": [
    {"type": "adjust_volume", "params": {"volume": 0.3}},
    // Futuramente: add_audio para música
  ]
}
```

---

**Dica Final:** Quando em dúvida, use `{"normalize": true}` com valores padrão. É a opção mais segura e profissional!
