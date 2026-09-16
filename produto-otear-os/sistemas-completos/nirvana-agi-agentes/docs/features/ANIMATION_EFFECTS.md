# 🎨 Guia de Efeitos de Animação para Legendas

Este documento detalha todos os efeitos de animação disponíveis para legendas automáticas na API.

## 📋 Efeitos Disponíveis

### 1. Estático (Padrão)
**Descrição:** Legendas tradicionais sem animação. O texto aparece completo e permanece na tela.

**Quando usar:**
- Vídeos profissionais/corporativos
- Documentários
- Conteúdo formal
- Quando a legibilidade é prioridade máxima

**Exemplo:**
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "pt",
    "model": "small",
    "style": {
      "color": "#FFFFFF",
      "font": "Arial",
      "font_size": 24,
      "position": "bottom"
    }
  }
}
```

---

### 2. Highlight Word (Destaque por Palavra) ⭐
**Descrição:** Destaca cada palavra conforme é falada, estilo karaoke. A palavra atual fica em uma cor diferente.

**Quando usar:**
- Vídeos educativos (ajuda na leitura)
- Conteúdo infantil
- Karaoke
- Aprendizado de idiomas
- Acessibilidade (facilita acompanhamento)

**Vantagens:**
- ✅ Ajuda o espectador a acompanhar a fala
- ✅ Melhora compreensão para não-nativos
- ✅ Engajamento visual
- ✅ Ótimo para crianças

**Exemplo:**
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "pt",
    "model": "small",
    "style": {
      "color": "#FFFFFF",
      "highlight_color": "#FFFF00",
      "font": "Arial",
      "font_size": 28,
      "position": "bottom",
      "animation": "highlight-word"
    }
  }
}
```

**Combinações de cores populares:**
- Branco + Amarelo: `#FFFFFF` + `#FFFF00` (clássico)
- Branco + Laranja: `#FFFFFF` + `#FF8C00` (energético)
- Preto + Vermelho: `#000000` + `#FF0000` (dramático)
- Azul + Ciano: `#0080FF` + `#00FFFF` (moderno)

---

### 3. Typewriter (Digitação) ⌨️ NOVO!
**Descrição:** Mostra o texto sendo "digitado" caractere por caractere, como se alguém estivesse escrevendo em tempo real.

**Quando usar:**
- Tutoriais de programação/tecnologia
- Efeito dramático/suspense
- Estilo hacker/terminal
- Narrativas criativas
- Documentários de tecnologia
- Vídeos de mistério/thriller

**Vantagens:**
- ✅ Efeito visual único e chamativo
- ✅ Cria sensação de "ao vivo"
- ✅ Perfeito para conteúdo tech
- ✅ Adiciona dinamismo

**Desvantagens:**
- ⚠️ Pode ser cansativo em vídeos longos
- ⚠️ Velocidade muito rápida dificulta leitura
- ⚠️ Não recomendado para conteúdo formal

**Exemplo básico:**
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "pt",
    "model": "small",
    "style": {
      "color": "#FFFFFF",
      "font": "Arial",
      "font_size": 26,
      "position": "bottom",
      "animation": "typewriter",
      "typewriter_speed": 20
    }
  }
}
```

**Exemplo estilo hacker/terminal:**
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "en",
    "model": "base",
    "style": {
      "color": "#00FF00",
      "font": "Courier New",
      "font_size": 24,
      "position": "bottom",
      "animation": "typewriter",
      "typewriter_speed": 25
    }
  }
}
```

**Exemplo dramático (lento):**
```json
{
  "type": "auto_subtitle",
  "params": {
    "language": "pt",
    "model": "small",
    "style": {
      "color": "#FFD700",
      "font": "Impact",
      "font_size": 32,
      "position": "center",
      "animation": "typewriter",
      "typewriter_speed": 12
    }
  }
}
```

---

## ⚙️ Parâmetro: typewriter_speed

Controla a velocidade de digitação em **caracteres por segundo**.

### Tabela de Velocidades

| Speed | Caracteres/seg | Sensação | Uso Recomendado |
|-------|----------------|----------|-----------------|
| 5-10 | Muito lento | Dramático, tenso | Suspense, horror, ênfase extrema |
| 10-15 | Lento | Deliberado, pensativo | Narrativas dramáticas, citações |
| 20-25 | Normal | Natural, legível | Uso geral, tutoriais |
| 30-40 | Rápido | Dinâmico, energético | Ação, tech, conteúdo jovem |
| 50+ | Muito rápido | Frenético | Apenas efeito visual, não para leitura |

### Recomendações por Tipo de Conteúdo

**Tutorial de Programação:** 20-25 (legível, mas dinâmico)
```json
"typewriter_speed": 22
```

**Vídeo de Hacker/Cybersecurity:** 25-30 (rápido, tech)
```json
"typewriter_speed": 28
```

**Documentário Dramático:** 12-15 (lento, impactante)
```json
"typewriter_speed": 13
```

**Vlog Tech:** 25-30 (energético)
```json
"typewriter_speed": 27
```

**Narrativa de Suspense:** 8-12 (muito lento)
```json
"typewriter_speed": 10
```

---

## 🎨 Estilos Visuais Recomendados

### Estilo 1: Terminal Hacker 💻
```json
{
  "color": "#00FF00",
  "font": "Courier New",
  "font_size": 24,
  "position": "bottom",
  "animation": "typewriter",
  "typewriter_speed": 25
}
```
**Fontes alternativas:** Consolas, Monaco, Lucida Console

### Estilo 2: Máquina de Escrever Vintage 📝
```json
{
  "color": "#D4AF37",
  "font": "Courier New",
  "font_size": 26,
  "position": "center",
  "animation": "typewriter",
  "typewriter_speed": 15
}
```

### Estilo 3: Sci-Fi Futurista 🚀
```json
{
  "color": "#00FFFF",
  "font": "Arial",
  "font_size": 28,
  "position": "bottom",
  "animation": "typewriter",
  "typewriter_speed": 30
}
```

### Estilo 4: Dramático Cinema 🎬
```json
{
  "color": "#FFD700",
  "font": "Impact",
  "font_size": 36,
  "position": "center",
  "animation": "typewriter",
  "typewriter_speed": 10
}
```

### Estilo 5: Educativo Moderno 📚
```json
{
  "color": "#FFFFFF",
  "font": "Arial",
  "font_size": 26,
  "position": "bottom",
  "animation": "typewriter",
  "typewriter_speed": 20
}
```

---

## 🔄 Comparação de Efeitos

| Característica | Estático | Highlight Word | Typewriter |
|----------------|----------|----------------|------------|
| **Legibilidade** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Engajamento** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Profissional** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Criativo** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Acessibilidade** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Vídeos Longos** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

---

## 💡 Dicas de Uso

### ✅ Boas Práticas

1. **Typewriter em vídeos curtos:** Funciona melhor em vídeos de até 5 minutos
2. **Ajuste a velocidade ao ritmo da fala:** Fala rápida = speed maior
3. **Teste diferentes velocidades:** O que parece bom no papel pode não funcionar no vídeo
4. **Considere o público:** Crianças e idosos preferem velocidades menores
5. **Combine com o tema:** Terminal = verde, Drama = dourado, Tech = ciano

### ❌ Evite

1. **Typewriter muito rápido:** Impossível de ler (> 40 chars/seg)
2. **Typewriter em vídeos longos:** Cansa o espectador
3. **Fontes muito decorativas:** Dificulta leitura
4. **Cores de baixo contraste:** Texto deve ser visível
5. **Misturar efeitos:** Escolha um e mantenha consistência

---

## 🧪 Testando os Efeitos

Use o script de teste incluído:

```bash
chmod +x test_typewriter.sh
./test_typewriter.sh
```

Ou teste manualmente:

```bash
# Teste rápido com typewriter
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@seu_video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "auto_subtitle",
        "params": {
          "language": "pt",
          "model": "base",
          "style": {
            "animation": "typewriter",
            "typewriter_speed": 20
          }
        }
      }
    ]
  }'
```

---

## 🎯 Casos de Uso Reais

### Caso 1: Tutorial de Python
```json
{
  "language": "pt",
  "model": "small",
  "style": {
    "color": "#00FF00",
    "font": "Consolas",
    "font_size": 24,
    "position": "bottom",
    "animation": "typewriter",
    "typewriter_speed": 22
  }
}
```

### Caso 2: Vlog de Tecnologia
```json
{
  "language": "pt",
  "model": "small",
  "style": {
    "color": "#FFFFFF",
    "font": "Arial",
    "font_size": 28,
    "position": "bottom",
    "animation": "highlight-word",
    "highlight_color": "#FF6600"
  }
}
```

### Caso 3: Documentário Dramático
```json
{
  "language": "pt",
  "model": "medium",
  "style": {
    "color": "#FFD700",
    "font": "Impact",
    "font_size": 32,
    "position": "center",
    "animation": "typewriter",
    "typewriter_speed": 12
  }
}
```

### Caso 4: Aula para Crianças
```json
{
  "language": "pt",
  "model": "small",
  "style": {
    "color": "#FFFFFF",
    "highlight_color": "#FF1493",
    "font": "Comic Sans MS",
    "font_size": 30,
    "position": "bottom",
    "animation": "highlight-word"
  }
}
```

---

**Desenvolvido para a API de Edição de Vídeos** 🎬
