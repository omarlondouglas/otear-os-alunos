from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

from app.orchestrator.memory import load_client_context, maybe_store_user_learning
from app.orchestrator.router import classify_intent, extract_job_id, extract_url
from app.orchestrator.schemas import ClientContext, Intent, OrchestratorResult
from app.capabilities import get_capability

logger = logging.getLogger(__name__)

_AUDIENCE_QUESTION_RE = re.compile(
    r"\b("
    r"quem\s+(?:e|eh|é)\s+(?:meu|o)\s+p[uúÃº]blico|"
    r"qual\s+(?:e|eh|é)\s+(?:meu|o)\s+p[uúÃº]blico|"
    r"p[uúÃº]blico\s+alvo|"
    r"cliente\s+ideal|"
    r"persona|avatar"
    r")\b",
    re.IGNORECASE,
)

_AUDIENCE_HEADING_RE = re.compile(
    r"^##\s*(?:P[uúÃº]blico(?:-Alvo)?|Cliente Ideal|Persona|Avatar)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

_LLM_STATUS_QUESTION_RE = re.compile(
    r"\b("
    r"qual\s+llm|"
    r"que\s+llm|"
    r"qual\s+modelo|"
    r"que\s+modelo|"
    r"modelo\s+(?:voce|voc[eêÃª])\s+(?:esta|ta|t[aá])\s+usando|"
    r"llm\s+(?:voce|voc[eêÃª])\s+(?:esta|ta|t[aá])\s+usando|"
    r"provider\s+llm"
    r")\b",
    re.IGNORECASE,
)


_INTENT_CAPABILITY = {
    Intent.CAROUSEL: "creation",
    Intent.VIDEO_EDIT: "video",
    Intent.VIDEO_STATUS: "video",
    Intent.IMAGE: "creation",
    Intent.LINKEDIN_POST: "writing",
    Intent.SCRIPT: "writing",
    Intent.STRATEGY: "writing",
    Intent.MEMORY: "memory",
    Intent.GENERAL: "writing",
}


class TextModelUnavailable(Exception):
    def __init__(self, detail: str, status: Optional[Dict[str, Any]] = None):
        super().__init__(detail)
        self.detail = detail
        self.status = status or {}


class ProjectOrchestrator:
    """
    Deterministic orchestration layer.

    Hermes/memory supplies client context; this class owns routing, execution,
    persistence hooks, and response formatting. Specialist agents can still be
    called behind this layer, but they are no longer the product's critical path.
    """

    async def run(
        self,
        message: str,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> OrchestratorResult:
        ctx = await asyncio.to_thread(load_client_context, user_id, org_id, brand_id)
        intent = classify_intent(message)

        from app.agents.agno_tools import set_current_context, set_current_user_id
        set_current_user_id(user_id)
        set_current_context(org_id=org_id, brand_id=brand_id)

        if self._is_llm_status_question(message):
            result = await asyncio.to_thread(self._run_llm_status_question)
        elif self._is_audience_question(message):
            intent = Intent.STRATEGY
            result = await asyncio.to_thread(self._run_audience_question, ctx)
        elif intent == Intent.CAROUSEL:
            result = await asyncio.to_thread(self._run_carousel, message, ctx)
        elif intent == Intent.VIDEO_EDIT:
            result = await asyncio.to_thread(self._run_video_edit, message)
        elif intent == Intent.VIDEO_STATUS:
            result = await asyncio.to_thread(self._run_video_status, message)
        elif intent == Intent.IMAGE:
            result = await asyncio.to_thread(self._run_image, message, ctx)
        elif intent == Intent.LINKEDIN_POST:
            result = await asyncio.to_thread(self._run_linkedin_post, message, ctx)
        elif intent == Intent.MEMORY:
            stored = await asyncio.to_thread(maybe_store_user_learning, message, "preferencia registrada")
            result = OrchestratorResult(
                response="Registrei isso na memoria do cliente." if stored else "Entendi. Vou considerar isso nos proximos trabalhos.",
                data={"intent": intent.value, "memory_updated": stored, "session_id": session_id},
            )
        elif intent in (Intent.SCRIPT, Intent.STRATEGY):
            result = await asyncio.to_thread(self._run_text_work, message, ctx, intent)
        else:
            result = await asyncio.to_thread(self._run_general, message, ctx)

        result.data.setdefault("intent", intent.value)
        result.data.setdefault("session_id", session_id)
        self._attach_orchestration_trace(result, intent, session_id)
        if intent != Intent.MEMORY:
            await asyncio.to_thread(maybe_store_user_learning, message, result.response[:220])
        return result

    def _attach_orchestration_trace(
        self,
        result: OrchestratorResult,
        intent: Intent,
        session_id: Optional[str],
    ) -> None:
        capability_id = _INTENT_CAPABILITY.get(intent, "writing")
        capability = get_capability(capability_id)
        capability_payload = {
            "id": capability_id,
            "name": capability.name if capability else capability_id,
        }

        steps: list[dict[str, Any]] = [
            {
                "label": "Entender pedido",
                "status": "done",
                "detail": f"Intent: {intent.value}",
            },
            {
                "label": "Selecionar habilidade",
                "status": "done",
                "detail": capability_payload["name"],
            },
        ]

        tool = result.data.get("tool")
        if tool:
            steps.append({
                "label": "Executar tool",
                "status": "done",
                "detail": str(tool),
            })
        elif result.data.get("llm"):
            steps.append({
                "label": "Gerar entrega textual",
                "status": "done",
                "detail": str(result.data["llm"]),
            })

        if result.data.get("needs"):
            steps.append({
                "label": "Aguardar informacao",
                "status": "waiting",
                "detail": str(result.data["needs"]),
            })
        else:
            steps.append({
                "label": "Preparar resposta",
                "status": "done",
                "detail": "Resposta enviada para a interface",
            })

        result.data["capability"] = capability_payload
        result.data["orchestration"] = {
            "session_id": session_id,
            "intent": intent.value,
            "capability": capability_payload,
            "steps": steps,
        }

    def _run_carousel(self, message: str, ctx: ClientContext) -> OrchestratorResult:
        from app.agents.agno_tools import generate_carousel_tool

        slides = self._build_carousel_slides(message, ctx)
        tool_result = generate_carousel_tool(slides)
        if not tool_result.get("success"):
            error = tool_result.get("error") or json.dumps(tool_result, ensure_ascii=False)[:500]
            return OrchestratorResult(
                response=f"Nao consegui gerar o carrossel. Erro: {error}",
                data={"tool": "generate_carousel_tool", "tool_result": tool_result},
            )

        slide_urls = [
            s.get("url") for s in tool_result.get("slides", [])
            if isinstance(s, dict) and s.get("url")
        ]
        lines = ["Carrossel criado.", ""]
        lines.extend(f"{i}. {url}" for i, url in enumerate(slide_urls, start=1))
        return OrchestratorResult(
            response="\n".join(lines).strip(),
            data={
                "tool": "generate_carousel_tool",
                "carousel_id": tool_result.get("carouselId"),
                "slides": slide_urls,
                "tool_result": tool_result,
            },
        )

    def _run_video_edit(self, message: str) -> OrchestratorResult:
        from app.agents.agno_tools import edit_video_tool

        video_url = extract_url(message)
        if not video_url:
            return OrchestratorResult(
                response="Envie a URL do video para eu criar o job de edicao.",
                data={"needs": "video_url"},
            )

        preset = "AULA" if any(w in message.lower() for w in ("aula", "curso", "palestra")) else "VIRAL"
        tool_result = edit_video_tool(
            video_url=video_url,
            preset=preset,
            wait_for_completion=False,
        )
        if tool_result.get("error"):
            return OrchestratorResult(
                response=f"Nao consegui criar o job de video. Erro: {tool_result['error']}",
                data={"tool": "edit_video_tool", "tool_result": tool_result},
            )

        job_id = tool_result.get("job_id") or tool_result.get("task_id") or tool_result.get("id")
        response = "Job de video criado."
        if job_id:
            response += f"\nJob ID: {job_id}\nUse esse ID para consultar o status."
        return OrchestratorResult(
            response=response,
            data={"tool": "edit_video_tool", "job_id": job_id, "tool_result": tool_result},
        )

    def _run_video_status(self, message: str) -> OrchestratorResult:
        from app.agents.agno_tools import check_video_status_tool

        job_id = extract_job_id(message)
        if not job_id:
            return OrchestratorResult(
                response="Me envie o Job ID do video para consultar o status.",
                data={"needs": "job_id"},
            )

        tool_result = check_video_status_tool(job_id)
        if tool_result.get("error"):
            return OrchestratorResult(
                response=f"Nao consegui consultar o status. Erro: {tool_result['error']}",
                data={"tool": "check_video_status_tool", "tool_result": tool_result},
            )

        status = tool_result.get("status", "desconhecido")
        download_url = tool_result.get("download_url")
        response = f"Status do video: {status}"
        if download_url:
            response += f"\nDownload: {download_url}"
        return OrchestratorResult(
            response=response,
            data={"tool": "check_video_status_tool", "status": status, "download_url": download_url, "tool_result": tool_result},
        )

    def _run_image(self, message: str, ctx: ClientContext) -> OrchestratorResult:
        from app.agents.agno_tools import generate_image_tool

        prompt = self._with_context(message, ctx)
        tool_result = generate_image_tool(prompt=prompt)
        if tool_result.get("error"):
            return OrchestratorResult(
                response=f"Nao consegui gerar a imagem. Erro: {tool_result['error']}",
                data={"tool": "generate_image_tool", "tool_result": tool_result},
            )
        url = tool_result.get("url") or tool_result.get("image_url")
        response = "Imagem criada."
        if url:
            response += f"\n{url}"
        return OrchestratorResult(
            response=response,
            data={"tool": "generate_image_tool", "url": url, "tool_result": tool_result},
        )

    def _run_text_work(self, message: str, ctx: ClientContext, intent: Intent) -> OrchestratorResult:
        script_direction = ""
        if intent == Intent.SCRIPT:
            script_direction = (
                "\n\nDIRECAO OBRIGATORIA DE CENA PARA ROTEIROS DE VIDEO:\n"
                "Quando o roteiro confrontar uma crenca ou objecao comum, inclua um beat visual curto de virada: "
                "a pessoa se assusta com a afirmacao, abre o campo de comentario e comeca a digitar uma critica; "
                "apos a explicacao/prova, ela para, reconhece internamente que o argumento faz sentido e apaga a critica. "
                "Descreva isso como acao de cena (sem narrar pensamentos literais) e use no maximo uma vez por roteiro, "
                "no ponto de maior contraste. A reacao deve parecer humana e contida, nunca uma caricatura."
            )
        prompt = (
            "Voce e um estrategista de conteudo para marcas. Responda em portugues, "
            "com entrega objetiva e pronta para uso.\n\n"
            f"{ctx.as_prompt()}\n\n"
            f"Pedido: {message}{script_direction}"
        )
        text = ""
        llm_error = ""
        llm_status: Dict[str, Any] = {}
        try:
            text = self._call_text_model(prompt, timeout=55)
        except TextModelUnavailable as exc:
            llm_error = exc.detail
            llm_status = exc.status
        if text:
            return OrchestratorResult(response=text, data={"llm": "text_model", "llm_fallback": False})
        text = (
            f"{self._format_text_model_unavailable(llm_error, llm_status)}\n\n"
            f"{self._fallback_text_plan(message, intent)}"
        )
        return OrchestratorResult(
            response=text,
            data={"llm": "fallback", "llm_fallback": True, "llm_error": llm_error, "llm_status": llm_status},
        )

    def _run_linkedin_post(self, message: str, ctx: ClientContext) -> OrchestratorResult:
        prompt = (
            "Voce e um ghostwriter senior de LinkedIn para fundadores, consultores e marcas B2B. "
            "Escreva em portugues do Brasil um post longo de autoridade, pronto para publicar, "
            "no estilo reflexivo, diagnostico e direto.\n\n"
            "Estrutura obrigatoria:\n"
            "1. Gancho problematico: abra com uma tensao real, sem frase generica.\n"
            "2. Desenvolvimento em blocos curtos: paragrafos de 1 a 3 linhas, com ritmo de LinkedIn.\n"
            "3. Diagnostico/processo: explique por que o problema acontece e qual processo resolve.\n"
            "4. Papel da IA quando aplicavel: conecte IA ao processo sem exagero ou promessa magica.\n"
            "5. Fechamento/CTA: termine com uma pergunta ou convite sobrio.\n\n"
            "Regras:\n"
            "- Nao entregue plano, roteiro, topicos soltos ou explicacao sobre a estrutura.\n"
            "- Nao use headings como 'Gancho' ou 'CTA'.\n"
            "- Evite emojis e hashtags, a menos que o usuario peça.\n"
            "- Use a especificidade do brief. Se houver produto, como TEAR CRM, trate como eixo do post.\n\n"
            f"{ctx.as_prompt()}\n\n"
            f"Brief do usuario: {message}"
        )
        text = ""
        llm_error = ""
        llm_status: Dict[str, Any] = {}
        try:
            text = self._call_text_model(prompt, timeout=55)
        except TextModelUnavailable as exc:
            llm_error = exc.detail
            llm_status = exc.status
        if text:
            return OrchestratorResult(
                response=text,
                data={"llm": "text_model", "llm_fallback": False, "format": "linkedin_post"},
            )

        return OrchestratorResult(
            response=self._fallback_linkedin_post(message, ctx),
            data={
                "llm": "fallback",
                "llm_fallback": True,
                "llm_error": llm_error,
                "llm_status": llm_status,
                "format": "linkedin_post",
            },
        )

    def _run_general(self, message: str, ctx: ClientContext) -> OrchestratorResult:
        prompt = (
            "Voce e o orquestrador de projeto de uma plataforma de conteudo. "
            "Seja direto. Quando faltar informacao, faca uma pergunta curta.\n\n"
            f"{ctx.as_prompt()}\n\n"
            f"Mensagem do usuario: {message}"
        )
        text = ""
        llm_error = ""
        llm_status: Dict[str, Any] = {}
        try:
            text = self._call_text_model(prompt, timeout=35)
        except TextModelUnavailable as exc:
            llm_error = exc.detail
            llm_status = exc.status
        if text:
            return OrchestratorResult(response=text, data={"llm": "text_model", "llm_fallback": False})
        text = self._format_text_model_unavailable(llm_error, llm_status)
        return OrchestratorResult(
            response=text,
            data={"llm": "fallback", "llm_fallback": True, "llm_error": llm_error, "llm_status": llm_status},
        )

    def _is_audience_question(self, message: str) -> bool:
        return bool(_AUDIENCE_QUESTION_RE.search(message or ""))

    def _is_llm_status_question(self, message: str) -> bool:
        return bool(_LLM_STATUS_QUESTION_RE.search(message or ""))

    def _run_llm_status_question(self) -> OrchestratorResult:
        try:
            from app.core.model_factory import get_llm_status
            status = get_llm_status()
        except Exception as exc:
            logger.warning("llm status unavailable: %s", exc)
            status = {}

        response = self._format_llm_status(status)
        return OrchestratorResult(
            response=response,
            data={"llm": "deterministic_llm_status", "llm_status": status},
        )

    def _format_llm_status(self, status: Dict[str, Any]) -> str:
        provider = status.get("active_provider")
        label = status.get("active_provider_label")
        models = status.get("models") if isinstance(status.get("models"), dict) else {}

        if not provider and not label:
            return (
                "Nao consegui consultar o status do LLM neste ambiente agora. "
                "Pela configuracao do projeto, o chat usa `MODEL_PROVIDER` via `model_factory.get_model()`, "
                "com providers por API: `openrouter`, `claude` ou `gemini`."
            )

        lines = [f"Estou usando: {label or provider}."]
        if provider:
            lines.append(f"Provider tecnico: `{provider}`.")
        if models:
            writer = models.get("writer")
            planner = models.get("planner")
            fast = models.get("fast")
            model_parts = []
            if writer:
                model_parts.append(f"writer `{writer}`")
            if planner:
                model_parts.append(f"planner `{planner}`")
            if fast:
                model_parts.append(f"fast `{fast}`")
            if model_parts:
                lines.append("Modelos configurados: " + ", ".join(model_parts) + ".")
        return "\n".join(lines)

    def _run_audience_question(self, ctx: ClientContext) -> OrchestratorResult:
        audience_text, source = self._find_audience_context(ctx)
        if audience_text:
            response = self._format_audience_answer(audience_text, source)
            return OrchestratorResult(
                response=response,
                data={"llm": "deterministic_audience_context", "source": source},
            )

        return OrchestratorResult(
            response=(
                "Ainda nao tenho publico-alvo registrado para esta marca. "
                "Me diga em uma frase quem voce vende, o que essa pessoa quer e qual dor ela sente. "
                "Com isso eu ajusto o roteiro para o publico certo."
            ),
            data={"needs": "audience_profile"},
        )

    def _find_audience_context(self, ctx: ClientContext) -> tuple[str, str]:
        context_sources = [
            ("perfil da marca", ctx.brand_context),
            ("perfil do usuario", ctx.user_context),
            ("memoria operacional", ctx.vault_context),
        ]
        for source, text in context_sources:
            section = self._extract_audience_section(text)
            if section:
                return section, source

        return "", ""

    def _extract_audience_section(self, text: str) -> str:
        if not text:
            return ""
        match = _AUDIENCE_HEADING_RE.search(text)
        if not match:
            return ""
        start = match.end()
        next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
        end = start + next_heading.start() if next_heading else len(text)
        return text[start:end].strip()

    def _format_audience_answer(self, audience_text: str, source: str) -> str:
        market = self._extract_markdown_field(audience_text, "Mercado-Alvo")
        avatar = self._extract_markdown_field(audience_text, "Avatar (Perfil Representativo do Cliente)")
        problem = self._extract_markdown_field(audience_text, "O Problema Principal Que Enfrentam")

        if market or avatar or problem:
            lines = ["Pelo contexto disponivel, seu publico principal e:"]
            if market:
                lines.append(f"\n**Quem:** {market}")
            if avatar:
                lines.append(f"\n**Perfil:** {avatar}")
            if problem:
                lines.append(f"\n**Dor central:** {problem}")
            lines.append(
                "\nVou usar esse perfil para ajustar gancho, dor, promessa e CTA do roteiro."
            )
            return "\n".join(lines)

        summary = re.sub(r"\s+", " ", audience_text).strip()
        if len(summary) > 900:
            summary = summary[:900].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
        return (
            "Pelo contexto disponivel, seu publico e:\n\n"
            f"{summary}\n\n"
            "Vou usar esse perfil para ajustar gancho, dor, promessa e CTA do roteiro."
        )

    def _extract_markdown_field(self, text: str, label: str) -> str:
        pattern = re.compile(
            rf"-\s*\*\*{re.escape(label)}\*\*:\s*(.+?)(?=\n\s*-\s*\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(text)
        if not match:
            return ""
        value = re.sub(r"\s+", " ", match.group(1)).strip()
        return value[:500].rstrip()

    def _build_carousel_slides(self, message: str, ctx: ClientContext) -> List[Dict[str, Any]]:
        title = self._short_title(message)
        brand_context = re.sub(r"^#+\s+.*$", "", ctx.as_prompt(), flags=re.MULTILINE)
        brand_context = re.sub(r"\s+", " ", brand_context).strip(" -:.")
        if len(brand_context) > 120:
            brand_context = brand_context[:120].rsplit(" ", 1)[0]
        bg = "#0a0a0a"
        accent = "#A3F12E"
        if any(word in message.lower() for word in ("branco", "clean", "claro")):
            bg = "#f7f7f2"
            accent = "#111111"

        ideas = self._extract_content_points(title)
        return [
            {
                "type": "cover",
                "title": title.upper(),
                "subtitle": brand_context or "Conteudo adaptado ao contexto da marca",
                "bgColor": bg,
                "titleColor": accent,
                "fontFamily": "urbanist",
            },
            *[
                {
                    "type": "text-only",
                    "title": point,
                    "bgColor": bg,
                    "titleColor": "#ffffff" if bg == "#0a0a0a" else "#111111",
                    "highlightColor": accent,
                    "fontFamily": "urbanist",
                }
                for point in ideas
            ],
            {
                "type": "text-only",
                "title": "Salve este post para aplicar depois.",
                "bgColor": accent,
                "titleColor": "#0a0a0a",
                "fontFamily": "urbanist",
            },
        ]

    def _short_title(self, message: str) -> str:
        text = re.sub(r"\b(crie|faca|faça|um|uma|carrossel|sobre|para|instagram)\b", " ", message, flags=re.IGNORECASE)
        text = re.sub(r"https?://\S+", "", text).strip(" .,:;-")
        if not text:
            return "Ideia principal"
        return text[:90].rsplit(" ", 1)[0] or text[:90]

    def _extract_content_points(self, message: str) -> List[str]:
        cleaned = re.sub(r"https?://\S+", "", message)
        chunks = [c.strip(" .,:;-") for c in re.split(r"[,;\n]+", cleaned) if c.strip()]
        points = [c for c in chunks if len(c) > 18][:4]
        defaults = [
            "Comece pelo problema que o publico sente hoje.",
            "Mostre a mudanca desejada com uma promessa especifica.",
            "Explique um passo pratico que a pessoa consegue aplicar.",
            "Feche com uma acao simples e mensuravel.",
        ]
        return (points + defaults)[:4]

    def _fallback_linkedin_post(self, message: str, ctx: ClientContext) -> str:
        subject = self._extract_linkedin_subject(message)
        ai_applies = self._linkedin_ai_applies(message, ctx)

        lines = [
            f"O problema de {subject} raramente e falta de ferramenta.",
            "",
            "E falta de processo.",
            "",
            "Muita empresa compra tecnologia esperando que ela resolva uma operacao que ainda nao foi desenhada.",
            "",
            "O resultado e previsivel:",
            "",
            "- dados espalhados",
            "- follow-up inconsistente",
            "- time comercial trabalhando no improviso",
            "- gestor sem visibilidade real do funil",
            "- cliente recebendo uma experiencia fragmentada",
            "",
            f"Quando {subject} entra nesse cenario, a pergunta certa nao e:",
            "",
            "\"qual recurso essa plataforma tem?\"",
            "",
            "A pergunta certa e:",
            "",
            "\"qual comportamento comercial precisamos tornar inevitavel?\"",
            "",
            "Esse e o diagnostico.",
            "",
            "Um CRM forte nao deve ser apenas um lugar onde o time registra contatos.",
            "",
            "Ele precisa funcionar como um sistema operacional da relacao com o cliente.",
            "",
            "Isso muda o processo em cinco camadas:",
            "",
            "1. Entrada clara: todo lead chega com origem, contexto e prioridade.",
            "2. Proximo passo definido: nenhuma oportunidade fica sem dono ou sem acao.",
            "3. Historico confiavel: cada conversa vira inteligencia para a proxima.",
            "4. Gestao visual: o lider enxerga gargalos antes que eles virem perda.",
            "5. Rotina comercial: o time sabe o que fazer hoje, nao apenas o que aconteceu ontem.",
            "",
        ]

        if ai_applies:
            lines.extend([
                "A IA entra como camada de aceleracao, nao como substituta do criterio.",
                "",
                "Ela pode resumir interacoes, sugerir proximas acoes, identificar padroes de perda, priorizar oportunidades e transformar dados soltos em leitura operacional.",
                "",
                "Mas IA sem processo apenas automatiza confusao.",
                "",
                "Primeiro vem o desenho da operacao.",
                "Depois vem a automacao.",
                "So entao a inteligencia artificial realmente aumenta a capacidade do time.",
                "",
            ])

        lines.extend([
            f"Por isso, falar de {subject} nao e falar apenas de software.",
            "",
            "E falar de disciplina comercial.",
            "De memoria institucional.",
            "De previsibilidade.",
            "De uma empresa que para de depender de heroismo individual e passa a operar com metodo.",
            "",
            "No fim, a pergunta que separa um CRM decorativo de um CRM estrategico e simples:",
            "",
            "sua operacao esta registrando informacoes ou esta tomando decisoes melhores a partir delas?",
        ])

        return "\n".join(lines)

    def _extract_linkedin_subject(self, message: str) -> str:
        text = re.sub(r"https?://\S+", "", message or "")
        text = re.sub(
            r"\b("
            r"crie|criar|faca|fa[cç]a|escreva|gere|produza|monte|"
            r"um|uma|post|texto|artigo|longo|linkedin|linked in|"
            r"de|do|da|para|sobre|autoridade|no estilo|estilo"
            r")\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"[\s,:;.-]+", " ", text).strip()
        if not text:
            return "esse tema"
        subject = text[:80].strip()
        return subject.rsplit(" ", 1)[0] if len(text) > 80 and " " in subject else subject

    def _linkedin_ai_applies(self, message: str, ctx: ClientContext) -> bool:
        combined = " ".join([message or "", ctx.brand_context, ctx.user_context, ctx.vault_context]).lower()
        return any(
            word in combined
            for word in ("ia", "ai", "inteligencia artificial", "automacao", "automação", "agente", "crm")
        )

    def _with_context(self, message: str, ctx: ClientContext) -> str:
        context = ctx.as_prompt()
        if not context:
            return message
        return f"{message}\n\nContexto do cliente:\n{context[:1800]}"

    def _call_text_model(self, prompt: str, timeout: int) -> str:
        system_prompt = (
            "Voce e o motor textual do O Tear Agentes. Responda em portugues, "
            "de forma objetiva, pronta para uso e sem mencionar detalhes internos."
        )
        messages = [
            SimpleNamespace(
                role="system",
                content=system_prompt,
            ),
            SimpleNamespace(role="user", content=prompt),
        ]
        status: Dict[str, Any] = {}
        try:
            from app.core.model_factory import get_llm_status, get_model

            status = get_llm_status()
            model = get_model("writer")
            if hasattr(model, "timeout"):
                model.timeout = timeout
            response = model.invoke(messages, assistant_message=None)
            text = str(getattr(response, "content", "") or "").strip()
            if text and not self._is_provider_error_text(text):
                return text
            if text:
                logger.warning("primary text model returned provider error: %s", text[:240])
                raise TextModelUnavailable(text[:500], status)
        except Exception as exc:
            if isinstance(exc, TextModelUnavailable):
                raise
            logger.warning("text model unavailable: %s", exc)
            fallback_text = self._call_direct_provider(prompt, system_prompt, status, timeout)
            if fallback_text:
                return fallback_text
            raise TextModelUnavailable(str(exc), status)

        return ""

    def _call_direct_provider(
        self,
        prompt: str,
        system_prompt: str,
        status: Dict[str, Any],
        timeout: int,
    ) -> str:
        provider = (status.get("active_provider") or "").lower()
        models = status.get("models") if isinstance(status.get("models"), dict) else {}
        if provider != "openrouter":
            return ""

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return ""

        try:
            from openai import OpenAI

            headers = {}
            referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
            app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
            if referer:
                headers["HTTP-Referer"] = referer
            if app_name:
                headers["X-Title"] = app_name

            model_id = (
                models.get("writer")
                or os.getenv("OPENROUTER_MODEL_WRITER")
                or os.getenv("OPENROUTER_MODEL")
                or "openai/gpt-4o-mini"
            )
            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                default_headers=headers or None,
                timeout=timeout,
            )
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1800,
            )
            text = str(response.choices[0].message.content or "").strip()
            if text and not self._is_provider_error_text(text):
                logger.info("text model fallback succeeded via OpenRouter direct API")
                return text
            return ""
        except Exception as exc:
            logger.warning("direct OpenRouter fallback failed: %s", exc)
            return ""

    def _is_provider_error_text(self, text: str) -> bool:
        lowered = (text or "").lower()
        markers = (
            "serviço de ia está temporariamente indisponível",
            "servico de ia esta temporariamente indisponivel",
            "invalid authentication credentials",
            "failed to authenticate",
            "claude cli falhou",
        )
        return any(marker in lowered for marker in markers)

    def _format_text_model_unavailable(self, detail: str, status: Dict[str, Any]) -> str:
        provider = status.get("active_provider") or "desconhecido"
        label = status.get("active_provider_label") or provider
        models = status.get("models") if isinstance(status.get("models"), dict) else {}
        writer = models.get("writer")

        if provider in ("none", "desconhecido"):
            return (
                "O chat esta online, mas nenhum provider LLM por API esta configurado.\n\n"
                "Configure uma destas opcoes no ambiente do backend e reinicie o servico:\n"
                "1. `MODEL_PROVIDER=openrouter` + `OPENROUTER_API_KEY`\n"
                "2. `MODEL_PROVIDER=claude` + `ANTHROPIC_API_KEY`\n"
                "3. `MODEL_PROVIDER=gemini` + `GOOGLE_API_KEY`"
            )

        lines = [
            f"O chat esta online, mas o provider de texto falhou.",
            f"Provider ativo: `{label}` (`{provider}`).",
        ]
        if writer:
            lines.append(f"Modelo writer: `{writer}`.")
        if detail:
            lines.append(f"Erro reportado: {detail[:500]}")
        lines.append("Verifique a API key/modelo do provider no ambiente do backend e reinicie o servico.")
        return "\n".join(lines)

    def _fallback_text_plan(self, message: str, intent: Intent) -> str:
        if intent == Intent.STRATEGY:
            return (
                "Plano inicial:\n"
                "1. Definir objetivo do projeto e publico principal.\n"
                "2. Separar uma promessa central para a campanha.\n"
                "3. Criar um carrossel de autoridade, um roteiro curto e uma imagem de apoio.\n"
                "4. Medir resposta do publico e registrar feedback na memoria do cliente."
            )
        return (
            "Rascunho inicial:\n"
            "1. Gancho: apresente o problema de forma direta.\n"
            "2. Desenvolvimento: mostre uma mudanca concreta.\n"
            "3. Prova: conecte com uma situacao real do cliente.\n"
            "4. CTA: convide para uma acao simples."
        )


project_orchestrator = ProjectOrchestrator()
