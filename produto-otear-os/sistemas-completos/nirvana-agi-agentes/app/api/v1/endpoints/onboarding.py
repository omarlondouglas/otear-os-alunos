import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from app.agents.onboarding_agent import create_onboarding_agent
from app.core.security import verify_supabase_token
from app.models.user_profile import get_user_profile, upsert_user_profile

router = APIRouter()
logger = logging.getLogger(__name__)

_onboarding_sessions: dict = {}


class OnboardingChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class OnboardingChatResponse(BaseModel):
    response: str
    onboarding_completed: bool
    session_id: str


class OnboardingQuestion(BaseModel):
    id: str
    label: str
    type: str
    required: bool = False
    placeholder: Optional[str] = None
    options: List[str] = Field(default_factory=list)


class OnboardingQuestionsResponse(BaseModel):
    version: str
    questions: List[OnboardingQuestion]


class StructuredOnboardingRequest(BaseModel):
    empresa: Optional[str] = None
    nicho: Optional[str] = None
    publico_texto: Optional[str] = None
    oferta: Optional[str] = None
    promessa_conteudo: Optional[str] = None
    objetivo_conteudo: Optional[str] = None
    tom_de_voz: Optional[str] = None
    social_handle: Optional[str] = None
    social_platform: Optional[str] = None
    nicho_conteudo: Optional[str] = None
    inspiracoes: Optional[Union[List[str], str]] = None
    formatos_prioritarios: Optional[Union[List[str], str]] = None
    radar_keywords: Optional[str] = None
    valores_texto: Optional[str] = None
    historia_texto: Optional[str] = None
    main_cta: Optional[str] = None


@router.get("/status")
async def onboarding_status(user_data: dict = Depends(verify_supabase_token)):
    """Verifica se o onboarding do usuario esta completo."""
    profile = get_user_profile(user_data["user_id"])
    return {
        "onboarding_completed": profile.onboarding_completed if profile else False,
        "has_profile": profile is not None,
        "should_show_onboarding": not profile or not profile.onboarding_completed,
    }


@router.get("/questions", response_model=OnboardingQuestionsResponse)
async def onboarding_questions(_: dict = Depends(verify_supabase_token)):
    """Perguntas estruturadas para a primeira abertura do Otear OS."""
    return build_onboarding_questions()


def build_onboarding_questions() -> OnboardingQuestionsResponse:
    return OnboardingQuestionsResponse(
        version="otear-os-day-zero-v1",
        questions=[
            OnboardingQuestion(
                id="empresa",
                label="Qual e o nome da sua marca, empresa ou projeto?",
                type="text",
                required=True,
                placeholder="Ex: O Tear",
            ),
            OnboardingQuestion(
                id="nicho",
                label="Em qual nicho voce atua?",
                type="text",
                required=True,
                placeholder="Ex: IA para pequenos negocios",
            ),
            OnboardingQuestion(
                id="publico_texto",
                label="Quem voce quer atrair?",
                type="textarea",
                required=True,
                placeholder="Ex: donos de clinicas que querem vender mais pelo Instagram",
            ),
            OnboardingQuestion(
                id="oferta",
                label="O que voce vende ou quer promover?",
                type="textarea",
                placeholder="Produto, servico, comunidade, consultoria ou ideia principal",
            ),
            OnboardingQuestion(
                id="objetivo_conteudo",
                label="Qual e o objetivo principal agora?",
                type="select",
                required=True,
                options=[
                    "Atrair leads",
                    "Vender uma oferta",
                    "Criar autoridade",
                    "Educar o mercado",
                    "Aquecer audiencia",
                    "Lancar produto",
                ],
            ),
            OnboardingQuestion(
                id="tom_de_voz",
                label="Como a marca deve soar?",
                type="select",
                options=["Direto", "Consultivo", "Provocativo", "Didatico", "Premium", "Casual"],
            ),
            OnboardingQuestion(
                id="formatos_prioritarios",
                label="Quais formatos voce quer priorizar?",
                type="multiselect",
                options=["Carrossel", "Reels", "Stories", "LinkedIn", "Email", "Landing page", "Anuncio"],
            ),
            OnboardingQuestion(
                id="social_handle",
                label="Qual e o perfil principal da marca?",
                type="text",
                placeholder="@seuperfil",
            ),
            OnboardingQuestion(
                id="inspiracoes",
                label="Quais perfis inspiram voce?",
                type="textarea",
                placeholder="@perfil1, @perfil2, @perfil3",
            ),
            OnboardingQuestion(
                id="radar_keywords",
                label="Quais temas o radar deve monitorar?",
                type="textarea",
                placeholder="Palavras-chave, fontes, noticias e tendencias relevantes",
            ),
        ],
    )


@router.post("/complete")
async def complete_structured_onboarding(
    request: StructuredOnboardingRequest,
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(verify_supabase_token),
):
    """Salva o onboarding inicial estruturado do Otear OS."""
    user_id = user_data["user_id"]
    raw = request.model_dump()
    profile_data = _normalize_structured_profile(raw)

    if not any(value for key, value in profile_data.items() if key != "onboarding_completed"):
        raise HTTPException(status_code=400, detail="Informe pelo menos um campo de perfil")

    profile_data["onboarding_completed"] = True
    profile = upsert_user_profile(user_id, profile_data)
    _sync_profile_to_vault(profile_data, _structured_strategy_data(raw))
    _enqueue_creator_extraction(profile_data)
    background_tasks.add_task(_dispatch_onboarding_webhook, user_id, user_data.get("email"), raw, profile_data)

    return {
        "message": "Onboarding concluido com sucesso",
        "onboarding_completed": profile.onboarding_completed,
        "profile": {
            "empresa": profile.empresa,
            "nicho": profile.nicho,
            "publico_texto": profile.publico_texto,
            "tom_de_voz": profile.tom_de_voz,
            "social_handle": profile.social_handle,
            "social_platform": profile.social_platform,
            "nicho_conteudo": profile.nicho_conteudo,
            "inspiracoes": profile.inspiracoes,
        },
    }


@router.post("/chat", response_model=OnboardingChatResponse)
async def onboarding_chat(
    request: OnboardingChatRequest,
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(verify_supabase_token),
):
    """Chat com o agente entrevistador para construcao do perfil."""
    user_id = user_data["user_id"]
    session_id = request.session_id or f"onboarding_{user_id}"

    if session_id not in _onboarding_sessions:
        _onboarding_sessions[session_id] = create_onboarding_agent(session_id=session_id)

    agent = _onboarding_sessions[session_id]

    try:
        logger.info("Onboarding chat: session=%s, msg_len=%s", session_id, len(request.message))
        response = agent.run(request.message, session_id=session_id)
        response_text = response.content if hasattr(response, "content") else str(response)

        onboarding_completed = "PERFIL_COMPLETO" in response_text
        response_text = response_text.replace("PERFIL_COMPLETO", "").strip()

        if onboarding_completed:
            background_tasks.add_task(_save_profile_from_history, user_id, session_id, agent, response_text)
            _onboarding_sessions.pop(session_id, None)

        return OnboardingChatResponse(
            response=response_text,
            onboarding_completed=onboarding_completed,
            session_id=session_id,
        )

    except Exception as exc:
        logger.error("Onboarding chat error: %s: %s", type(exc).__name__, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


async def _save_profile_from_history(user_id: str, session_id: str, agent, final_summary: str = ""):
    """Extrai perfil da conversa, salva no Supabase e sincroniza USER.md."""
    try:
        history_text = ""
        if hasattr(agent, "memory") and agent.memory:
            messages = getattr(agent.memory, "messages", [])
            for msg in messages:
                role = getattr(msg, "role", "unknown")
                content = getattr(msg, "content", "")
                if content:
                    history_text += f"{role}: {content}\n"

        source_text = final_summary or history_text
        if not source_text:
            logger.warning("Sem texto para extracao de perfil user_id=%s", user_id)
            upsert_user_profile(user_id, {"onboarding_completed": True})
            return

        from agno.agent import Agent as AgnoAgent
        from app.core.model_factory import get_model

        extraction_agent = AgnoAgent(
            name="Extrator",
            model=get_model("fast"),
            markdown=False,
        )

        extraction_prompt = (
            "Voce e um extrator de dados. Analise o texto abaixo e retorne SOMENTE um JSON valido "
            "com as chaves indicadas. Sem explicacoes, sem markdown, apenas o JSON.\n\n"
            f"TEXTO:\n{source_text}\n\n"
            "Regras:\n"
            "- Use o que foi informado; deixe string vazia se nao mencionado.\n"
            "- social_handle_raw = texto bruto da rede social do usuario.\n"
            "- inspiracoes_raw = texto bruto dos criadores que inspiram, separados por virgula.\n"
            "- nicho_conteudo = nicho especifico do conteudo digital.\n"
            "- promessa_conteudo = transformacao, tese ou promessa editorial do perfil.\n"
            "- objetivo_conteudo = objetivo principal: crescer audiencia, vender, autoridade, comunidade, nutricao etc.\n"
            "- radar_keywords = temas, palavras-chave, noticias e fontes que o radar deve monitorar.\n"
            "- formatos_prioritarios = formatos citados pelo usuario, separados por virgula.\n\n"
            "JSON esperado:\n"
            '{"empresa": "", "nicho": "", "valores_texto": "", "publico_texto": "", "historia_texto": "", '
            '"tom_de_voz": "", "social_handle_raw": "", "nicho_conteudo": "", "inspiracoes_raw": "", '
            '"promessa_conteudo": "", "objetivo_conteudo": "", "radar_keywords": "", "formatos_prioritarios": ""}'
        )

        result = extraction_agent.run(extraction_prompt)
        result_text = result.content if hasattr(result, "content") else str(result)

        json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
        if json_match:
            try:
                raw = json.loads(json_match.group())
                profile_data = _normalize_profile(raw)
                profile_data["onboarding_completed"] = True
                upsert_user_profile(user_id, profile_data)
                logger.info("Perfil salvo para user_id=%s: campos=%s", user_id, list(profile_data.keys()))
                _sync_profile_to_vault(profile_data, raw)
                _enqueue_creator_extraction(profile_data)
                return
            except json.JSONDecodeError as exc:
                logger.warning("JSON invalido na extracao de perfil: %s | texto=%s", exc, result_text[:200])

        upsert_user_profile(user_id, {"onboarding_completed": True})
        logger.warning("Perfil salvo sem dados de campo para user_id=%s", user_id)

    except Exception as exc:
        logger.error("Erro ao salvar perfil do onboarding: %s", exc, exc_info=True)
        try:
            upsert_user_profile(user_id, {"onboarding_completed": True})
        except Exception:
            pass


_PRODUCT_DEFAULTS_TECNICAS = (
    "Plataforma O Tear: presets de video disponiveis no painel "
    "(VIRAL, HORMOZI, AULA_PRO, PODCAST, FAST_HORMOZI, VIRAL_FUTURO_PRO, CLEAN_PRO). "
    "Formatos suportados: vertical 9:16 (Reels/TikTok/Shorts), horizontal 16:9 (YouTube) "
    "e carrosseis Instagram 1080x1350. Cliente escolhe preset via interface."
)

_PRODUCT_DEFAULTS_WORKFLOW = (
    "Fluxo padrao: briefing/tema -> radar de noticias e referencias -> roteiro -> calendario/editor "
    "ou upload de video -> preset/corte inteligente -> aprovacao de candidatos virais -> render -> entrega. "
    "O agente sempre deve transcrever antes de cortar."
)


def _normalize_profile(raw: dict) -> dict:
    """Normaliza apenas campos persistidos no Supabase."""
    from app.services.social.parser import parse_inspirations, parse_social_handle, serialize_handles

    out: dict = {}
    for key in (
        "empresa",
        "nicho",
        "valores_texto",
        "publico_texto",
        "historia_texto",
        "tom_de_voz",
        "nicho_conteudo",
    ):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            out[key] = value.strip()

    raw_social = raw.get("social_handle_raw", "")
    if isinstance(raw_social, str) and raw_social.strip():
        parsed = parse_social_handle(raw_social.strip())
        if parsed:
            out["social_handle"] = parsed.handle
            out["social_platform"] = parsed.platform

    raw_inspirations = raw.get("inspiracoes_raw", "")
    if isinstance(raw_inspirations, str) and raw_inspirations.strip():
        handles = parse_inspirations(raw_inspirations.strip(), max_items=3)
        if handles:
            out["inspiracoes"] = serialize_handles(handles)

    return out


def _join_values(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, str):
        return value.strip()
    return ""


def _normalize_structured_profile(raw: dict) -> dict:
    from app.services.social.parser import parse_inspirations, parse_social_handle, serialize_handles

    out: dict = {}
    for key in (
        "empresa",
        "nicho",
        "publico_texto",
        "historia_texto",
        "tom_de_voz",
        "nicho_conteudo",
    ):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            out[key] = value.strip()

    valores_parts = []
    for label, key in (
        ("valores", "valores_texto"),
        ("oferta", "oferta"),
        ("cta", "main_cta"),
        ("objetivo", "objetivo_conteudo"),
        ("promessa", "promessa_conteudo"),
    ):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            valores_parts.append(f"{label}: {value.strip()}")
    if valores_parts:
        out["valores_texto"] = "\n".join(valores_parts)

    raw_social = raw.get("social_handle") or ""
    if isinstance(raw_social, str) and raw_social.strip():
        parsed = parse_social_handle(raw_social.strip())
        if parsed:
            out["social_handle"] = parsed.handle
            out["social_platform"] = parsed.platform
        elif isinstance(raw.get("social_platform"), str) and raw.get("social_platform").strip():
            out["social_handle"] = raw_social.strip().lstrip("@")
            out["social_platform"] = raw.get("social_platform").strip()

    raw_inspirations = _join_values(raw.get("inspiracoes"))
    if raw_inspirations:
        handles = parse_inspirations(raw_inspirations, max_items=3)
        if handles:
            out["inspiracoes"] = serialize_handles(handles)

    if not out.get("nicho_conteudo") and out.get("nicho"):
        out["nicho_conteudo"] = out["nicho"]

    return out


def _structured_strategy_data(raw: dict) -> Dict[str, Any]:
    return {
        "promessa_conteudo": _join_values(raw.get("promessa_conteudo") or raw.get("oferta")),
        "objetivo_conteudo": _join_values(raw.get("objetivo_conteudo")),
        "radar_keywords": _join_values(raw.get("radar_keywords")),
        "formatos_prioritarios": _join_values(raw.get("formatos_prioritarios")),
    }


def _get_onboarding_webhook_url() -> str:
    url = os.getenv("ONBOARDING_WEBHOOK_URL", "").strip()
    if url:
        return url

    try:
        from app.api.v1.endpoints.settings import load_settings

        return (load_settings().webhook_url or "").strip()
    except Exception as exc:
        logger.warning("Falha ao carregar webhook_url das configuracoes: %s", exc)
        return ""


async def _dispatch_onboarding_webhook(
    user_id: str,
    email: Optional[str],
    raw_answers: Dict[str, Any],
    profile_data: Dict[str, Any],
) -> None:
    url = _get_onboarding_webhook_url()
    if not url:
        return

    payload = {
        "event": "otear_os_onboarding_completed",
        "user_id": user_id,
        "email": email,
        "answers": raw_answers,
        "profile": profile_data,
    }

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        logger.info("Webhook de onboarding enviado para user_id=%s", user_id)
    except Exception as exc:
        logger.warning("Falha ao enviar webhook de onboarding user_id=%s: %s", user_id, exc)


def _strategy_value(strategy_data: Dict[str, Any], key: str) -> str:
    value = strategy_data.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _sync_profile_to_vault(profile_data: dict, strategy_data: Optional[Dict[str, Any]] = None) -> None:
    """Espelha perfil e estrategia no USER.md do vault Obsidian."""
    try:
        from app.services.social.parser import deserialize_handles
        from app.services.user_memory import complete_onboarding, update_section

        strategy_data = strategy_data or {}
        empresa = (profile_data.get("empresa") or "").strip()
        nicho = (profile_data.get("nicho") or "").strip()
        social_handle = (profile_data.get("social_handle") or "").strip()
        social_platform = (profile_data.get("social_platform") or "").strip()

        identidade_parts = [part for part in (empresa, nicho) if part]
        if social_handle:
            identidade_parts.append(f"{social_platform}:{social_handle}" if social_platform else social_handle)
        identidade = ", ".join(identidade_parts) or "(nao informado)"

        promessa = _strategy_value(strategy_data, "promessa_conteudo")
        objetivo_conteudo = _strategy_value(strategy_data, "objetivo_conteudo")
        radar_keywords = _strategy_value(strategy_data, "radar_keywords")
        formatos = _strategy_value(strategy_data, "formatos_prioritarios")
        nicho_conteudo = (profile_data.get("nicho_conteudo") or "").strip()

        valores = (profile_data.get("valores_texto") or "").strip()
        historia = (profile_data.get("historia_texto") or "").strip()
        objetivos_parts = [part for part in (valores, historia) if part]
        objetivos = "\n".join(objetivos_parts) if objetivos_parts else "(nao informado)"

        complete_onboarding({
            "identidade": identidade,
            "estilo de comunicacao": (profile_data.get("tom_de_voz") or "(nao informado)").strip(),
            "preferencias tecnicas": _PRODUCT_DEFAULTS_TECNICAS,
            "workflow": _PRODUCT_DEFAULTS_WORKFLOW,
            "objetivos": objetivos,
        })

        if nicho_conteudo:
            update_section("user", "nicho de conteudo", nicho_conteudo)

        strategy_lines = [
            f"promessa: {promessa or '(nao informado)'}",
            f"objetivo: {objetivo_conteudo or '(nao informado)'}",
            f"publico: {(profile_data.get('publico_texto') or '(nao informado)').strip()}",
            f"nicho_de_conteudo: {nicho_conteudo or '(nao informado)'}",
            "pilares:",
            "- noticias: tendencias e sinais oportunos conectados ao nicho",
            "- tutorial: educacao pratica, processos, templates e demonstracoes",
            "- vlog: bastidores, rotina, experimentos e prova de trabalho",
            "- review_sincero: avaliacao honesta de ferramentas, trends e metodos",
            f"formatos_prioritarios: {formatos or '(nao informado)'}",
        ]
        update_section("user", "estrategia de conteudo", "\n".join(strategy_lines))

        if radar_keywords or nicho_conteudo:
            update_section(
                "user",
                "news_radar",
                "\n".join([
                    f"niche: {radar_keywords or nicho_conteudo}",
                    f"youtube_query: {radar_keywords or nicho_conteudo}",
                    f"twitter_query: {radar_keywords or nicho_conteudo}",
                    "subreddits: n8n,AI_Agents,LocalLLaMA,marketing",
                ]),
            )

        inspiracoes_json = profile_data.get("inspiracoes") or ""
        handles = deserialize_handles(inspiracoes_json) if inspiracoes_json else []
        if handles:
            lines = []
            for handle in handles:
                url = handle.to_url() or ""
                suffix = f" ({url})" if url else ""
                lines.append(f"- {handle.platform}: {handle.handle}{suffix}")
            update_section("user", "inspiracoes", "\n".join(lines))

        logger.info("USER.md sincronizado com estrategia de conteudo")
    except Exception as exc:
        logger.warning("Falha ao sincronizar USER.md no vault: %s", exc)


def _enqueue_creator_extraction(profile_data: dict) -> None:
    """Dispara extracao paralela de perfil proprio e inspiracoes."""
    from app.services.social.parser import deserialize_handles
    from app.workers.social_tasks import enqueue_extractions

    targets = []
    if profile_data.get("social_handle"):
        targets.append({
            "platform": profile_data.get("social_platform", "unknown"),
            "handle": profile_data["social_handle"],
            "kind": "self",
        })

    handles = deserialize_handles(profile_data.get("inspiracoes") or "")
    for handle in handles:
        targets.append({"platform": handle.platform, "handle": handle.handle, "kind": "inspiration"})

    if not targets:
        return

    try:
        job_ids = enqueue_extractions(targets, posts_count=10)
        logger.info("[creator_extraction] enfileirados %s jobs em paralelo: %s", len(job_ids), job_ids)
        try:
            from app.services.user_memory import update_section

            lines = [
                f"- {job['kind']}: {job['platform']} {job['handle']} -> job_id={job['job_id']}"
                for job in job_ids
            ]
            update_section("memory", "extracoes de referencias", "\n".join(lines))
        except Exception:
            pass
    except Exception as exc:
        logger.warning("[creator_extraction] falha ao enfileirar (Celery offline?): %s", exc)
