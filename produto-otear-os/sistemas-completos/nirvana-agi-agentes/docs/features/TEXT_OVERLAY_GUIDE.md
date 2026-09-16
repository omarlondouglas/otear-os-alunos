# 📝 Guia de Text Overlay (Texto com Tarja)

Guia completo sobre como adicionar texto sobre vídeos com tarja de fundo.

## 📋 Visão Geral

A operação `add_text_overlay` permite adicionar texto sobre o vídeo com:
- ✅ Tarja de fundo colorida (opcional)
- ✅ Controle total de posição
- ✅ Timing preciso (quando aparece e por quanto tempo)
- ✅ Múltiplos textos no mesmo vídeo
- ✅ Estilos customizáveis

## 🎯 Casos de Uso

### 1. Títulos de Vídeo
Adicione um título chamativo no início.

### 2. Lower Thirds
Nome e cargo de entrevistados (canto inferior).

### 3. Call to Action
"INSCREVA-SE!", "CURTA!", "COMPARTILHE!"

### 4. Créditos
Informações de produção no final.

### 5. Marca D'água de Texto
Seu canal/marca sempre visível.

### 6. Capítulos/Seções
Marcar diferentes partes do vídeo.

### 7. Anotações
Destacar informações importantes.

## 📝 Parâmetros Completos

### Obrigatórios
- `text`: O texto a ser exibido

### Posicionamento
- `position`: Posição predefinida
  - `"top"` - Topo centralizado
  - `"bottom"` - Base centralizada (padrão)
  - `"center"` - Centro da tela
  - `"top-left"` - Canto superior esquerdo
  - `"top-right"` - Canto superior direito
  - `"bottom-left"` - Canto inferior esquerdo
  - `"bottom-right"` - Canto inferior direito
- `x`, `y`: Posição customizada em pixels (sobrescreve position)

### Estilo do Texto
- `font`: Nome da fonte (padrão: "Arial")
- `font_size`: Tamanho em pixels (padrão: 48)
- `font_color`: Cor do texto (padrão: "white")
- `alignment`: Alinhamento do texto (padrão: "center")
  - `"left"` - Alinhado à esquerda
  - `"center"` - Centralizado (recomendado)
  - `"right"` - Alinhado à direita
  - **Nota:** Especialmente útil para textos com múltiplas linhas
- `line_spacing`: Espaçamento entre linhas em pixels (padrão: 0)

### Tarja de Fundo
- `box`: Mostrar tarja (true/false, padrão: true)
- `box_color`: Cor da tarja (padrão: "black")
- `box_opacity`: Opacidade 0.0-1.0 (padrão: 0.7)
- `box_padding`: Espaçamento interno da tarja em pixels (padrão: 20)
  - Valores maiores = tarja mais espaçosa
  - Recomendado: 15-50 pixels

### Timing
- `start_time`: Quando aparece em segundos (padrão: 0)
- `duration`: Duração em segundos (padrão: até o fim)

## 🎨 Exemplos Práticos

### Exemplo 1: Título Simples
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "Meu Vídeo",
        "position": "top",
        "font_size": 60
      }
    }]
  }'
```

### Exemplo 2: Lower Third Profissional
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@entrevista.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "Dr. João Silva\nCardiologista",
        "position": "bottom-left",
        "font_size": 32,
        "font_color": "white",
        "box_color": "#0066CC",
        "box_opacity": 0.9,
        "start_time": 10,
        "duration": 15
      }
    }]
  }'
```

### Exemplo 3: Call to Action Animado
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "👍 CURTA!",
          "position": "center",
          "font_size": 100,
          "font_color": "yellow",
          "box": false,
          "start_time": 5,
          "duration": 2
        }
      },
      {
        "type": "add_text_overlay",
        "params": {
          "text": "🔔 INSCREVA-SE!",
          "position": "center",
          "font_size": 100,
          "font_color": "red",
          "box": false,
          "start_time": 8,
          "duration": 2
        }
      }
    ]
  }'
```

### Exemplo 4: Marca D'água de Texto
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "@meucanal",
        "position": "top-right",
        "font_size": 24,
        "font_color": "white",
        "box_color": "black",
        "box_opacity": 0.5,
        "box_padding": 10
      }
    }]
  }'
```

### Exemplo 5: Capítulos do Vídeo
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@tutorial.mp4" \
  -F 'request={
    "operations": [
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Capítulo 1: Introdução",
          "position": "top",
          "font_size": 50,
          "start_time": 0,
          "duration": 3
        }
      },
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Capítulo 2: Desenvolvimento",
          "position": "top",
          "font_size": 50,
          "start_time": 60,
          "duration": 3
        }
      },
      {
        "type": "add_text_overlay",
        "params": {
          "text": "Capítulo 3: Conclusão",
          "position": "top",
          "font_size": 50,
          "start_time": 120,
          "duration": 3
        }
      }
    ]
  }'
```

### Exemplo 6: Créditos Finais
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "Produção: Minha Empresa\nDireção: João Silva\nEdição: Maria Santos",
        "position": "center",
        "font_size": 36,
        "font_color": "white",
        "box_color": "black",
        "box_opacity": 0.8,
        "line_spacing": 10,
        "box_padding": 40,
        "start_time": 115,
        "duration": 5
      }
    }]
  }'
```

### Exemplo 7: Título com Tarja Grande (Muito Espaçamento)
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "TÍTULO GRANDE",
        "position": "top",
        "font_size": 80,
        "font_color": "white",
        "box_color": "black",
        "box_opacity": 0.9,
        "box_padding": 50
      }
    }]
  }'
```

### Exemplo 8: Múltiplas Linhas com Espaçamento
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "Primeira Linha\nSegunda Linha\nTerceira Linha",
        "position": "center",
        "font_size": 50,
        "font_color": "yellow",
        "line_spacing": 15,
        "box_padding": 35
      }
    }]
  }'
```

### Exemplo 9: Texto Centralizado com Alinhamento 🎯
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "POV: IA é uma bolha\nEu criando minha agencia\ncom agentes",
        "position": "center",
        "alignment": "center",
        "font_size": 60,
        "font_color": "white",
        "box_color": "black",
        "box_opacity": 0.8,
        "line_spacing": 10,
        "box_padding": 40
      }
    }]
  }'
```

### Exemplo 10: Texto Alinhado à Esquerda
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "• Primeiro item\n• Segundo item\n• Terceiro item",
        "position": "center",
        "alignment": "left",
        "font_size": 40,
        "font_color": "white",
        "line_spacing": 8,
        "box_padding": 30
      }
    }]
  }'
```

### Exemplo 11: Texto Alinhado à Direita
```bash
curl -X POST "http://localhost:8000/api/v1/videos/edit" \
  -H "X-API-Key: dev-secret-key" \
  -F "video=@video.mp4" \
  -F 'request={
    "operations": [{
      "type": "add_text_overlay",
      "params": {
        "text": "Linha 1\nLinha 2 mais longa\nLinha 3",
        "position": "top-right",
        "alignment": "right",
        "font_size": 36,
        "font_color": "yellow",
        "line_spacing": 5,
        "box_padding": 25
      }
    }]
  }'
```

## 🎨 Guia de Cores

### Cores por Nome
```
white, black, red, green, blue, yellow
cyan, magenta, orange, purple, pink
brown, gray, lime, navy, teal
```

### Cores Hex
```
#FF0000 - Vermelho
#00FF00 - Verde
#0000FF - Azul
#FFFF00 - Amarelo
#FF6600 - Laranja
#9900FF - Roxo
#00FFFF - Ciano
```

### Cores com Transparência
```
#FF000080 - Vermelho 50% transparente
#0000FF40 - Azul 25% transparente
```

## 📊 Tamanhos de Fonte Recomendados

| Uso | Tamanho | Exemplo |
|-----|---------|---------|
| Marca d'água | 20-28 | @meucanal |
| Lower third | 28-36 | Nome - Cargo |
| Texto normal | 36-48 | Informações |
| Título | 50-70 | Título do Vídeo |
| Call to Action | 70-100 | INSCREVA-SE! |
| Destaque | 100+ | NOVO! |

## 📏 Guia de Espaçamento

### box_padding (Espaçamento Interno da Tarja)

Controla o espaço entre o texto e a borda da tarja.

| Valor | Efeito | Uso |
|-------|--------|-----|
| 10-15 | Compacto | Marca d'água, textos pequenos |
| 20-30 | Normal | Uso geral (padrão: 20) |
| 35-50 | Espaçoso | Títulos, destaques |
| 60+ | Muito espaçoso | Efeito dramático |

**Exemplo:**
```json
{
  "text": "Título",
  "box_padding": 40
}
```

## 📐 Guia de Alinhamento de Texto

### alignment (Alinhamento Horizontal do Texto)

Controla como o texto é alinhado, especialmente útil para múltiplas linhas.

| Valor | Efeito | Quando Usar |
|-------|--------|-------------|
| `"left"` | Alinhado à esquerda | Listas, bullet points, texto corrido |
| `"center"` | Centralizado | Títulos, destaques, frases curtas (padrão) |
| `"right"` | Alinhado à direita | Timestamps, informações secundárias |

### Comparação Visual

```
alignment: "left"
┌──────────────────┐
│ Linha 1          │
│ Linha 2 longa    │
│ Linha 3          │
└──────────────────┘

alignment: "center"
┌──────────────────┐
│     Linha 1      │
│  Linha 2 longa   │
│     Linha 3      │
└──────────────────┘

alignment: "right"
┌──────────────────┐
│          Linha 1 │
│    Linha 2 longa │
│          Linha 3 │
└──────────────────┘
```

**Exemplo Prático:**
```json
{
  "text": "POV: IA é uma bolha\nEu criando minha agencia\ncom agentes",
  "position": "center",
  "alignment": "center",
  "line_spacing": 10
}
```

### line_spacing (Espaçamento Entre Linhas)

Controla o espaço entre linhas quando há múltiplas linhas de texto.

| Valor | Efeito | Uso |
|-------|--------|-----|
| 0 | Sem espaço extra | Padrão |
| 5-10 | Espaçamento leve | Textos normais |
| 15-25 | Espaçamento médio | Melhor legibilidade |
| 30+ | Espaçamento grande | Efeito visual |

**Exemplo:**
```json
{
  "text": "Linha 1\nLinha 2\nLinha 3",
  "line_spacing": 15
}
```

### Combinando Espaçamentos

Para textos com múltiplas linhas e tarja espaçosa:
```json
{
  "text": "Título Principal\nSubtítulo Secundário",
  "font_size": 60,
  "box_padding": 40,
  "line_spacing": 10
}
```

## 💡 Dicas Profissionais

### 1. Contraste é Fundamental
Sempre use cores que contrastem com o vídeo:
- Texto branco + tarja preta (clássico)
- Texto preto + tarja branca (limpo)
- Texto branco + tarja colorida (moderno)

### 2. Opacidade da Tarja
- `0.5-0.6`: Sutil, deixa ver o vídeo
- `0.7-0.8`: Balanceado (recomendado)
- `0.9-1.0`: Sólido, máxima legibilidade

### 3. Timing
- Títulos: 3-5 segundos
- Lower thirds: 8-15 segundos
- Call to action: 2-3 segundos
- Créditos: 5-10 segundos

### 4. Posicionamento
- **Topo**: Títulos, capítulos
- **Base**: Lower thirds, créditos
- **Centro**: Call to action, destaques
- **Cantos**: Marca d'água, informações secundárias

### 5. Múltiplos Textos
Evite sobrepor textos. Use timing diferente:
```json
[
  {"start_time": 0, "duration": 3},
  {"start_time": 4, "duration": 3},
  {"start_time": 8, "duration": 3}
]
```

## 🎬 Estilos Populares

### Estilo YouTube
```json
{
  "text": "NOVO VÍDEO!",
  "position": "top",
  "font_size": 70,
  "font_color": "white",
  "box_color": "red",
  "box_opacity": 0.95,
  "box_padding": 30
}
```

### Estilo Documentário
```json
{
  "text": "Nome do Entrevistado\nCargo/Função",
  "position": "bottom-left",
  "font_size": 32,
  "font_color": "white",
  "box_color": "#1a1a1a",
  "box_opacity": 0.85
}
```

### Estilo Minimalista
```json
{
  "text": "Título Simples",
  "position": "center",
  "font_size": 60,
  "font_color": "white",
  "box": false
}
```

### Estilo Corporativo
```json
{
  "text": "Empresa XYZ",
  "position": "bottom-right",
  "font_size": 28,
  "font_color": "white",
  "box_color": "#003366",
  "box_opacity": 0.9
}
```

## 🔄 Combinando com Outras Operações

### Título + Legendas
```json
{
  "operations": [
    {
      "type": "add_text_overlay",
      "params": {
        "text": "Tutorial Completo",
        "position": "top",
        "start_time": 0,
        "duration": 3
      }
    },
    {
      "type": "auto_subtitle",
      "params": {"language": "pt", "model": "small"}
    }
  ]
}
```

### Lower Third + Volume
```json
{
  "operations": [
    {
      "type": "adjust_volume",
      "params": {"normalize": true}
    },
    {
      "type": "add_text_overlay",
      "params": {
        "text": "João Silva - CEO",
        "position": "bottom-left",
        "start_time": 5,
        "duration": 10
      }
    }
  ]
}
```

## ⚠️ Limitações

1. **Fontes**: Usa fontes do sistema. Nem todas as fontes podem estar disponíveis.
2. **Emojis**: Suporte limitado dependendo da fonte.
3. **Quebras de linha**: Use `\n` para múltiplas linhas.
4. **Caracteres especiais**: Alguns podem precisar de escape.

## 🧪 Testando

```bash
chmod +x test_text_overlay.sh
./test_text_overlay.sh
```

---

**Crie textos profissionais em seus vídeos!** 📝
