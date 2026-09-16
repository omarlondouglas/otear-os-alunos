---
name: otear-content-templates
description: "Templates de carrossel, roteiro, thread e WhatsApp O Tear."
version: 1.0.0
category: content
tags: [otear, templates, carousel, scripts, whatsapp, clickup]
---

# O Tear Content Templates

Templates de conteúdo prontos para uso no pipeline O Tear (ClickUp → Evolution API → WhatsApp/Redes Sociais).

## Carrossel (Instagram/LinkedIn/WhatsApp PDF)

Arquivo: `templates/carrossel-template.md`

**Estrutura 7 slides:**
1. Capa — gancho visual + promessa
2. Contexto — fatos (1-2 frases)
3. Por que importa — implicação pro ICP
4. Insight/Contrarian — "o que ninguém te conta"
5. Prova/Exemplo — case real ou analogia
6. Ação Prática — checklist 3 passos acionáveis
7. CTA O Tear — direct/WhatsApp + assinatura

**Regras:**
- 7 slides máx (atenção cai após slide 5)
- Um conceito por slide, fonte ≥ 32pt, lê-se em 2s
- Slide 6 = checklist acionável (não teoria)
- Slide 7 = funil pro WhatsApp/direct (Patrícia controla disparo 3min delay)
- Visual: fundo `#0D0D0D`, texto `#FFFFFF` + `#FFD700`, fonte Inter/Montserrat bold
- Legenda complementa, não repete

**Adaptações por plataforma:** ver template.

## Roteiro Curto (TikTok/Reels/Shorts)

Formato padrão (já coberto por `news-script-adapter`):
- Hook (1-2 frases)
- Development
- Closing
- On-Screen Editing
- Delivery Notes

## Thread Twitter/X

Estrutura 7-10 tweets:
1. Hook + promessa
2-6. Desenvolvimento (1 ponto por tweet)
7. Checklist prático
8. CTA + link/profile
9-10. Contexto extra/hashtags

## Disparo WhatsApp (Evolution API)

Configuração O Tear:
- URL: `https://evo2.otear.com.br`
- Instância: `agi`
- Key: `SUA_EVOLUTION_API_KEY`
- Endpoint: `POST /message/sendText/agi`
- Delay: **180s (3 min)** — preferência da Patrícia, NÃO reduzir

Formato telefone: `55DDDNumero` (ex: `5521999999999`), sem formatação.
⚠️ 0800 não aceita WhatsApp — pular antes de enviar.

## ClickUp Integration

Lista: Tiktok (ID: 901415273387)
Pasta: Marketing
Espaço: O Tear CRM (90142498572)
Team: 36977155

Status inicial: `concept`
Tags base: `roteiro`, `tiktok` + plataforma + tema
Nome: `Roteiro: {tema} - {plataforma}` ou `Hook: {titulo}` ou `Carrossel: {tema}`

## Estratégia Editorial (pilares de tema)

Regras sempre-on (Marlon corrigiu 2x: "ainda tá técnico"; quer conversa, não tutorial):

- **Topo de funil NUNCA começa técnico** — nada de n8n, prompt, workflow como gancho. Começa filosófico/humano: identidade ("quem sou sem o negócio"), tempo, família, propósito, empreender no Brasil.
- **4 pilares de tema**: Notícia / Filosófico (citar alguém, citar dor, citar experiência) / Família / Trabalho-Propósito. Um pilar por dia; 2 posts/dia máx (1 feed + 1 story).
- **Cada peça termina com pergunta aberta** — a métrica é comentário com história real ("cara, ano passado eu..."), não like/salvo. Sem pergunta = não publica.
- **Ponte invisível**: nunca "por isso você precisa de automação". Usar "foi essa dor que me fez construir meu primeiro agente" — tecnologia como consequência, nunca causa.
- **Volume (até 9 vídeos/dia)**: framework da fábrica = 12 caixas (4 pilares × 3 sub-temas) + 3 formatos fixos (câmera 15-45s / tela+voz 20-60s / áudio 30-90s). 1 ideia → 3-5 peças por reciclagem. Detalhes: `references/estrategia-editorial.md`.
- **Golden Circle**: WHY (problema, não vende) → HOW (solução com automação, entrega o como) → WHAT (oferta). Calendário semanal integra os 3.
- **Camadas fora-da-bolha**: Universal → Comportamental → Ponte → Técnico leve. Cada camada tem CTA próprio (comentário → salvo → link bio → direct).

## Design System Visual (Tokens)

Tokens visuais aplicados em carrosséis HTML e PDFs gerados:

| Token | Valor |
|-------|-------|
| Fundo principal | `#0a0a0f` (body) / `#0D0D0D` (slides print) |
| Fundo card/elevado | `#16161f` |
| Texto principal | `#fafafa` |
| Texto secundário | `#a0a0b0` |
| Accent (amarelo O Tear) | `#FFD700` / `#ffd600` |
| Danger/alerta | `#ff3b3b` |
| Borda | `#2a2a3a` |
| Fonte heading/corpo | Space Grotesk (400/600/700) |
| Fonte mono/badges | JetBrains Mono (400/700) |
| Fonte alternativa (redes) | Inter / Montserrat bold |
| Slide ratio (Instagram) | 1080×1350px (4:5) |

## Geração de Carrossel HTML → PDF/PNG

Quando o usuário pede carrossel visual (não só texto):

1. Gerar HTML único com todos os slides usando Tailwind CDN + Google Fonts (Space Grotesk + JetBrains Mono) + tokens acima.
2. Cada slide = `<section class="slide">` com 1080×1350px. Navegação por teclado (setas) e swipe touch.
3. Converter para PDF: `npm install puppeteer` em `/tmp/pdfgen`, script Node com `page.pdf({format:'A4', printBackground:true})`.
4. Converter para PNGs individuais: loop `page.evaluate` mostrando 1 slide por vez + `page.screenshot()`.
5. Enviar via WhatsApp: `MEDIA:/caminho/arquivo.pdf` (chega como documento) ou `.png`/`.jpg` (abre como foto nativa).

Pitfall: puppeteer precisa `--no-sandbox --disable-setuid-sandbox` quando roda como root na VPS.

## Referências Relacionadas

- `news-script-adapter` → roteiros notícia + storytelling
- `content-pipeline-automation` → pipeline completo
- `marlon-brand-guide.md` (em news-script-adapter/references) → tom, ICP, frases-poder
- `references/estrategia-editorial.md` → framework completo de pilares, camadas e fábrica de volume