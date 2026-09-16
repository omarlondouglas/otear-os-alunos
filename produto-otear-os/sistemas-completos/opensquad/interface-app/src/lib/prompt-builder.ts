/** Builds the Claude CLI prompt for a carousel squad run */
export function buildSquadPrompt(opts: {
  squadCode: string;
  topic: string;
  period: string;
  mode: "copy" | "images" | "full";
  imageStrategy: "ia" | "capa" | "banco" | "nenhuma";
}): string {
  const { squadCode, topic, period, mode, imageStrategy } = opts;

  const periodLabel =
    period === "B" ? "Últimos 3 dias" :
    period === "C" ? "Última semana" :
    "Últimas 24 horas";

  if (mode === "full") {
    const imageCheckpointAnswer =
      imageStrategy === "ia" || imageStrategy === "capa"
        ? "opção 2 (Sim — gerar com IA)"
        : imageStrategy === "banco"
        ? "opção 1 (Sim — usar banco de imagens)"
        : "opção 3 (Não — manter só texto)";

    const periodHours = period === "C" ? 168 : period === "B" ? 72 : 24;
    const newsApiUrl = `http://localhost:3000/api/news?tema=${encodeURIComponent(topic)}&horas=${periodHours}&limite=10`;
    const capaOnly = imageStrategy === "capa";

    return `Execute /opensquad run ${squadCode}

CHECKPOINT FAST-PATH: Os checkpoints já têm respostas abaixo. NÃO apresente opções ao usuario. Apenas escreva state.json, salve o outputFile se necessário, e avance para o próximo step.

PERFORMANCE:
- Para state.json: reutilize o conteúdo anterior, só mude status/step/agent.
- Pesquisador: chame a API diretamente em vez de WebSearch: ${newsApiUrl}
- Steps de imagem com estratégia "banco": se Curador encontrou imagens (sem FALLBACK), Conceituador e Gerador devem fazer fast-exit em poucas palavras.

RESPOSTAS PRE-DEFINIDAS:

Checkpoint 1 - "Foco do Dia":
- Tema: opção 4 (Notícia específica) — o tema é: "${topic}"
- Período: ${periodLabel}

Checkpoint 2 - "Imagens para o Carrossel":
- ${imageCheckpointAnswer}
- Slides com imagem: ${capaOnly ? "APENAS o slide 1 (capa). Os demais slides ficam SEM imagem." : "todos os que o curador recomendar"}${imageStrategy === "ia" ? `
- IMPORTANTE: O usuario escolheu GERAR COM IA. O Conceituador DEVE criar prompts para todos os slides. NAO pular.` : ""}${capaOnly ? `
- IMPORTANTE: Gerar imagem APENAS para o slide 1 (capa). Conceituador cria prompt SO para a capa. Gerador gera SO 1 imagem. Image-patcher injeta SO no slide 1. Os outros slides mantém imageFile: null.
- OBRIGATORIO PARA A CAPA: Identificar o ELEMENTO VISUAL CHAVE da noticia — sempre existe pelo menos um:
  * PESSOA: CEO, fundador, artista, politico, celebridade mencionada → buscar foto real via POST http://localhost:3000/api/banco-pessoas com body {"nome": "Nome Completo"}
  * MARCA/EMPRESA: logo ou identidade visual da empresa principal → buscar via Google CSE (web_search)
  O Conceituador DEVE buscar essa referencia real ANTES de criar o prompt do Gemini.
  O Gerador DEVE enviar a foto/logo como referencia (Template B multimodal) para o Gemini manter semelhanca fisica ou identidade da marca.
  NUNCA gerar a capa 100% do zero sem referencia visual real.` : ""}

Execute o pipeline completo. Nao pause para pedir confirmação.
Para o Curador: consulte http://localhost:3000/api/image-bank?categoria=geral&limit=30
Para o Gerador: carregue o .env com "set -a && source .env && set +a" antes da API Gemini.`;
  }

  if (mode === "images") {
    const imageCheckpointAnswer =
      imageStrategy === "ia"
        ? "opção 2 (Sim — gerar com IA)"
        : imageStrategy === "banco"
        ? "opção 1 (Sim — usar banco de imagens)"
        : "opção 3 (Não — manter só texto)";

    return `Execute /opensquad run ${squadCode}

IMPORTANTE: O carrossel já tem texto pronto de um run anterior. Os agentes de texto (Pesquisador, Estrategista, Redator, Designer) já rodaram.

RESPOSTAS PRE-DEFINIDAS PARA OS CHECKPOINTS (responda automaticamente sem pedir confirmacao ao usuario):

Checkpoint 1 - "Foco do Dia":
- Tema: opção 4 (Notícia específica) — o tema é: "${topic}"
- Período: ${periodLabel}

Checkpoint 2 - "Imagens para o Carrossel":
- ${imageCheckpointAnswer}
- Slides com imagem: todos os que o curador recomendar

Execute o pipeline completo. Nao pause para pedir confirmação.
Para o Curador: consulte http://localhost:3000/api/image-bank?categoria=geral&limit=30
Para o Gerador: carregue o .env com "set -a && source .env && set +a" antes da API Gemini.`;
  }

  // mode === "copy"
  return `Execute /opensquad run ${squadCode}

RESPOSTAS PRE-DEFINIDAS PARA OS CHECKPOINTS (responda automaticamente sem pedir confirmacao ao usuario):

Checkpoint 1 - "Foco do Dia":
- Tema: opção 4 (Notícia específica) — o tema é: "${topic}"
- Período: ${periodLabel}

Checkpoint 2 - "Estrategia de Imagens":
- sem imagens, apenas texto por enquanto

Execute o pipeline completo do início ao fim usando essas respostas. Nao pause para pedir confirmação.`;
}
