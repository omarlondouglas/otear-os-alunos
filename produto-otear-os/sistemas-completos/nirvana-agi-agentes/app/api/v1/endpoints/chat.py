from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
import json
import os
import re
import logging
import time
from pathlib import Path

# Limite duro pro orchestrator. Acima disso, cancela e devolve erro pro user
# em vez de deixar o request pendurado.
ORCHESTRATOR_TIMEOUT_S = float(os.getenv("CHAT_ORCHESTRATOR_TIMEOUT_S", "120"))

from app.api.v1.endpoints.logs import add_log_entry
from app.core.security import verify_api_key_or_token_with_context
from app.services.profile_cache import get_user_context, get_brand_context
from app.orchestrator.project_orchestrator import project_orchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    brand_id: Optional[str] = None

    @staticmethod
    def _validate_msg(v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message must not be empty")
        if len(v) > 10_000:
            raise ValueError("message too long (max 10000 chars)")
        return v


class ChatResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None


# ─── Guard fast-path: mensagens triviais nao precisam passar pelo LLM ─────────
# Saudacoes, agradecimentos, confirmacoes curtas e perguntas comuns sobre a
# plataforma. Tudo isso o guard sempre liberaria de qualquer forma.
_TRIVIAL_PATTERNS = re.compile(
    r"^\s*(oi+|ola|ola+!|hello|hey|opa|eai|e ai|bom dia|boa tarde|boa noite|"
    r"obrigad[oa]+|valeu|thanks|thx|tmj|blz|beleza|ok|okay|certo|sim|nao|"
    r"tudo bem\??|como vai\??|td bem\??|legal|massa|show|perfeito|otimo|"
    r"continua|prossiga|pode seguir|manda v[eê]r|vai|isso|exato)\s*[!?.]*\s*$",
    re.IGNORECASE,
)


def _is_trivial(msg: str) -> bool:
    """True quando a mensagem e claramente conversacional/curta."""
    if len(msg.strip()) < 4:
        return True
    if _TRIVIAL_PATTERNS.match(msg):
        return True
    return False


def _trivial_response(msg: str) -> str:
    text = (msg or "").strip().lower()
    if any(word in text for word in ("obrigad", "valeu", "thanks", "thx")):
        return "Disponha. Quando quiser, posso criar um roteiro, carrossel, imagem ou job de video."
    return "Oi. Posso te ajudar com roteiro, carrossel, imagem, estrategia ou edicao de video."


async def _add_chat_log(
    agent: str,
    message: str,
    log_type: str = "agent",
    metadata: Optional[dict] = None,
) -> bool:
    try:
        return await add_log_entry(
            agent=agent,
            message=message,
            log_type=log_type,
            metadata=metadata,
        )
    except TypeError:
        return await add_log_entry(agent=agent, message=message, log_type=log_type)


async def _run_guard_async(user_msg: str) -> Optional[str]:
    """
    Roda o GuardAgent em thread (e sincrono internamente).
    Retorna None se permitido, string com motivo se bloqueado.
    """
    if _is_trivial(user_msg):
        return None  # bypass

    def _do_guard():
        try:
            from app.agents.agno_agents import guard_agent
            resp = guard_agent.run(user_msg)
            text = resp.content if hasattr(resp, "content") else str(resp)
            text = text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            data = json.loads(text)
            if not data.get("allowed", True):
                return data.get("reason", "Pedido fora do escopo da plataforma")
            return None
        except Exception as e:
            logger.warning(f"Guard parse error, allowing through: {e}")
            return None

    return await asyncio.to_thread(_do_guard)


async def _build_enriched_msg(user_msg: str, user_id: Optional[str], brand_id: Optional[str]) -> str:
    """Carrega context (cacheado) em paralelo e prefixa na mensagem."""
    if brand_id:
        ctx = await asyncio.to_thread(get_brand_context, brand_id)
    elif user_id:
        ctx = await asyncio.to_thread(get_user_context, user_id)
    else:
        ctx = None
    return f"{ctx}\n\n{user_msg}" if ctx else user_msg


_WORKSPACE_CONTEXT_RE = re.compile(
    r"\b("
    r"refer[eê]ncia|referencia|referencias|banco|criador|creator|perfil|"
    r"roteiro|roteiros|script|scripts|texto|copy|legenda|"
    r"estilo|comunica[cç][aã]o|transcri[cç][aã]o|transcricao"
    r")\b",
    re.IGNORECASE,
)


def _build_request_context(
    user_msg: str,
    request_context: Optional[Dict[str, Any]],
    user_id: Optional[str],
    org_id: Optional[str],
    brand_id: Optional[str],
) -> str:
    parts: list[str] = []
    uploaded = _format_uploaded_file_context(request_context)
    if uploaded:
        parts.append(uploaded)
    if _WORKSPACE_CONTEXT_RE.search(user_msg or ""):
        workspace = _load_workspace_context(user_id, org_id, brand_id, user_msg)
        if workspace:
            parts.append(workspace)
    if not parts:
        return ""
    return "\n\n".join(parts)


def _format_uploaded_file_context(request_context: Optional[Dict[str, Any]]) -> str:
    if not request_context:
        return ""
    uploaded = request_context.get("uploaded_file")
    if not isinstance(uploaded, dict):
        return ""

    filename = str(uploaded.get("filename") or "arquivo enviado")
    url = str(uploaded.get("url") or "")
    content_type = str(uploaded.get("content_type") or "")
    content_text = str(uploaded.get("content_text") or "").strip()
    truncated = bool(uploaded.get("text_truncated"))

    lines = [
        "## Arquivo enviado no chat",
        f"- Nome: {filename}",
    ]
    if content_type:
        lines.append(f"- Tipo: {content_type}")
    if url:
        lines.append(f"- URL: {url}")
    if content_text:
        suffix = "\n\n[texto truncado]" if truncated else ""
        lines.append(f"\n### Conteudo extraido\n{content_text[:40_000]}{suffix}")
    else:
        lines.append("\nConteudo textual nao extraido. Use a URL acima como referencia do arquivo.")
    return "\n".join(lines)


def _load_workspace_context(
    user_id: Optional[str],
    org_id: Optional[str],
    brand_id: Optional[str],
    user_msg: str,
) -> str:
    parts: list[str] = []
    scripts = _load_script_context(user_id, org_id, brand_id)
    if scripts:
        parts.append(scripts)
    refs = _load_reference_context(user_msg)
    if refs:
        parts.append(refs)
    if not parts:
        return ""
    return "## Contexto disponivel da biblioteca e referencias\n\n" + "\n\n".join(parts)


def _load_script_context(user_id: Optional[str], org_id: Optional[str], brand_id: Optional[str]) -> str:
    if not user_id and not org_id:
        return ""
    try:
        from app.core.supabase import get_supabase

        client = get_supabase()
        query = (
            client.table("content_assets")
            .select("title,description,metadata,created_at")
            .eq("type", "script")
            .order("created_at", desc=True)
            .limit(8)
        )
        if org_id:
            query = query.eq("org_id", org_id)
            if brand_id:
                query = query.eq("brand_id", brand_id)
        elif user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()
        assets = result.data or []
    except Exception as exc:
        logger.warning("failed to load script context: %s", exc)
        return ""

    if not assets:
        return ""
    blocks = ["### Roteiros salvos"]
    for item in assets:
        title = str(item.get("title") or "Sem titulo")
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        content = str(metadata.get("content") or item.get("description") or "").strip()
        content = _compact_text(content, 1200)
        blocks.append(f"#### {title}\n{content}")
    return "\n\n".join(blocks)


def _load_reference_context(user_msg: str) -> str:
    try:
        from app.services.social.markdown_writer import REFERENCES_DIR
    except Exception:
        return ""

    if not REFERENCES_DIR.exists():
        return ""

    include_transcripts = bool(re.search(r"transcri|video|videos|vídeo|vídeos", user_msg or "", re.IGNORECASE))
    blocks = ["### Banco de referencias"]
    count = 0
    for creator_dir in sorted(
        [p for p in REFERENCES_DIR.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        if count >= 8:
            break
        profile_path = creator_dir / "_profile.md"
        if not profile_path.exists():
            continue
        try:
            profile_text = profile_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        block = [f"#### {creator_dir.name}", _compact_text(profile_text, 2200)]

        if include_transcripts:
            post_text = _load_one_reference_transcript(creator_dir)
            if post_text:
                block.append("##### Transcricao de video analisado\n" + _compact_text(post_text, 1800))

        blocks.append("\n\n".join(block))
        count += 1

    return "\n\n".join(blocks) if count else ""


def _load_one_reference_transcript(creator_dir: Path) -> str:
    for path in sorted(
        [p for p in creator_dir.glob("*.md") if not p.name.startswith("_")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:2]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        match = re.search(r"##\s+Transcript\s*(.+)$", text, re.IGNORECASE | re.DOTALL)
        if match:
            transcript = match.group(1).strip()
            if transcript and not transcript.startswith("_("):
                return transcript
    return ""


def _compact_text(text: str, max_chars: int) -> str:
    text = re.sub(r"\n{3,}", "\n\n", (text or "").strip())
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "..."


def _merge_context_into_message(enriched_msg: str, extra_context: str) -> str:
    if not extra_context:
        return enriched_msg
    return f"{extra_context}\n\n## Pedido do usuario\n{enriched_msg}"


def _blocked_response(reason: str) -> str:
    return (
        f"⚠️ **Não posso ajudar com isso.**\n\n"
        f"{reason}\n\n"
        f"Sou especializada em **criação de conteúdo digital**: "
        f"carrosséis, edição de vídeo, roteiros, imagens e materiais de marca. "
        f"Como posso te ajudar dentro dessas áreas?"
    )


def _resolve_session(user_data: dict | None, request: ChatRequest):
    """Devolve (user_id, org_id, brand_id, session_id)."""
    if user_data and user_data.get("user_id"):
        user_id = user_data["user_id"]
        session_id = f"user_{user_id}"
    else:
        user_id = None
        session_id = None
        if request.context:
            session_id = request.context.get("session_id") or request.context.get("user_id")
        if not session_id:
            import uuid as _uuid
            session_id = f"anon_{_uuid.uuid4().hex[:12]}"

    brand_id = (user_data or {}).get("brand_id") or request.brand_id
    org_id = (user_data or {}).get("org_id")
    if brand_id and user_id:
        session_id = f"brand_{brand_id}_{user_id}"
    return user_id, org_id, brand_id, session_id


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user_data: dict | None = Depends(verify_api_key_or_token_with_context),
):
    """
    Processa mensagem via Jobs Team (Agno coordinate).
    Suporta JWT Bearer (frontend multi-usuário) e API Key (WhatsApp/integrations).
    Headers opcionais: X-Org-Id, X-Brand-Id pra contexto multi-tenant.
    """
    try:
        user_msg = request.message
        user_id, org_id, brand_id, session_id = _resolve_session(user_data, request)

        logger.info(f"Chat - session_id: {session_id}, msg: {user_msg[:50]}...")
        await _add_chat_log(agent="User", message=user_msg, log_type="user")

        # Roda Guard + carregamento de contexto em PARALELO (era serial)
        guard_task = asyncio.create_task(_run_guard_async(user_msg))
        enrich_task = asyncio.create_task(_build_enriched_msg(user_msg, user_id, brand_id))
        request_context_task = asyncio.create_task(asyncio.to_thread(
            _build_request_context,
            user_msg,
            request.context,
            user_id,
            org_id,
            brand_id,
        ))
        block_reason, enriched_msg, request_context = await asyncio.gather(
            guard_task,
            enrich_task,
            request_context_task,
        )

        if block_reason:
            await _add_chat_log(agent="Guard", message=f"Blocked: {block_reason}", log_type="system")
            return ChatResponse(
                response=_blocked_response(block_reason),
                data={"session_id": session_id, "blocked": True},
            )

        # Set thread-local pras tools terem contexto
        from app.agents.agno_tools import set_current_user_id, set_current_context
        set_current_user_id(user_id)
        set_current_context(org_id=org_id, brand_id=brand_id)

        run_context = {"user_id": user_id} if user_id else {}
        if org_id:
            run_context["org_id"] = org_id
        if brand_id:
            run_context["brand_id"] = brand_id

        # ProjectOrchestrator e o caminho principal: ele roteia de forma
        # deterministica, injeta memoria do cliente e so usa LLM/tools quando
        # necessario. O Agno Team legado fica fora do caminho critico.
        orchestrator_msg = _merge_context_into_message(enriched_msg, request_context)

        logger.info(f"[chat] project_orchestrator iniciando session={session_id}")
        t0 = time.monotonic()
        try:
            result = await asyncio.wait_for(
                project_orchestrator.run(
                    orchestrator_msg,
                    user_id=user_id,
                    org_id=org_id,
                    brand_id=brand_id,
                    session_id=session_id,
                ),
                timeout=ORCHESTRATOR_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            elapsed = time.monotonic() - t0
            logger.error(f"[chat] project_orchestrator TIMEOUT apos {elapsed:.1f}s session={session_id}")
            raise HTTPException(
                status_code=504,
                detail=f"Orchestrator timeout apos {elapsed:.0f}s - tente reformular ou simplificar o pedido",
            )
        elapsed = time.monotonic() - t0
        logger.info(f"[chat] project_orchestrator concluido em {elapsed:.1f}s session={session_id}")
        response_text = result.response

        orchestration = result.data.get("orchestration") if isinstance(result.data, dict) else None
        if orchestration:
            capability = orchestration.get("capability", {}) if isinstance(orchestration, dict) else {}
            await _add_chat_log(
                agent="Orchestrator",
                message=(
                    f"Habilidade: {capability.get('name', 'desconhecida')} | "
                    f"Intent: {orchestration.get('intent', 'desconhecido')}"
                ),
                log_type="decision",
                metadata={"orchestration": orchestration},
            )

        await _add_chat_log(
            agent="Jobs",
            message=response_text,
            log_type="agent",
            metadata={"orchestration": orchestration} if orchestration else None,
        )

        if user_id:
            background_tasks.add_task(_track_analytics, user_id, "chat_message", {"session_id": session_id})
            background_tasks.add_task(_auto_save_response_to_library, user_id, response_text)

        from app.core.model_factory import get_llm_status
        llm_info = get_llm_status()

        return ChatResponse(
            response=response_text,
            data={
                "session_id": session_id,
                "llm_provider": llm_info["active_provider"],
                "llm_label": llm_info["active_provider_label"],
                **result.data,
            },
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await _add_chat_log(agent="System", message=f"Error: {str(e)}", log_type="system")
        raise HTTPException(status_code=500, detail="Internal error processing request")


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user_data: dict | None = Depends(verify_api_key_or_token_with_context),
):
    """
    Versao streaming do /chat via SSE. Frontend recebe eventos:
      event: status     data: {"phase":"guard"|"context"|"thinking"|"writing"}
      event: blocked    data: {"reason":"..."}
      event: chunk      data: {"text":"..."} (resposta em pedacos)
      event: done       data: {"session_id":"...", "llm_provider":"...", "full":"..."}
      event: error      data: {"detail":"..."}

    UX: usuario ve "pensando..." enquanto o LLM processa, e a resposta sai em
    chunks de ~80 chars assim que o response chega.
    """
    user_msg = request.message
    user_id, org_id, brand_id, session_id = _resolve_session(user_data, request)
    await _add_chat_log(agent="User", message=user_msg, log_type="user")

    async def _gen() -> AsyncGenerator[str, None]:
        def _sse(event: str, payload: dict) -> str:
            return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Pre-roll de 4KB de comentarios SSE — forca Traefik / nginx a abrir
        # o stream IMEDIATAMENTE em vez de bufferizar ate ter conteudo. Sem
        # isso, o front pode ficar mudo durante todo o "thinking" se o proxy
        # bufferizar ate atingir threshold (geralmente 4-8KB).
        yield ":" + (" " * 4096) + "\n\n"
        yield _sse("status", {"phase": "starting"})

        try:
            yield _sse("status", {"phase": "guard"})
            guard_task = asyncio.create_task(_run_guard_async(user_msg))
            enrich_task = asyncio.create_task(_build_enriched_msg(user_msg, user_id, brand_id))
            request_context_task = asyncio.create_task(asyncio.to_thread(
                _build_request_context,
                user_msg,
                request.context,
                user_id,
                org_id,
                brand_id,
            ))
            block_reason, enriched_msg, request_context = await asyncio.gather(
                guard_task,
                enrich_task,
                request_context_task,
            )

            if block_reason:
                await _add_chat_log(agent="Guard", message=f"Blocked: {block_reason}", log_type="system")
                yield _sse("blocked", {"reason": block_reason, "response": _blocked_response(block_reason)})
                return

            from app.agents.agno_tools import set_current_user_id, set_current_context
            set_current_user_id(user_id)
            set_current_context(org_id=org_id, brand_id=brand_id)

            run_context: dict = {}
            if user_id: run_context["user_id"] = user_id
            if org_id: run_context["org_id"] = org_id
            if brand_id: run_context["brand_id"] = brand_id

            yield _sse("status", {"phase": "thinking", "elapsed_s": 0})
            logger.info(f"[chat-stream] project_orchestrator iniciando session={session_id}")
            t0 = time.monotonic()

            orchestrator_msg = _merge_context_into_message(enriched_msg, request_context)

            orch_task = asyncio.create_task(project_orchestrator.run(
                orchestrator_msg,
                user_id=user_id,
                org_id=org_id,
                brand_id=brand_id,
                session_id=session_id,
            ))

            # Heartbeat a cada 3s + timeout duro
            timed_out = False
            while not orch_task.done():
                try:
                    await asyncio.wait_for(asyncio.shield(orch_task), timeout=3.0)
                except asyncio.TimeoutError:
                    elapsed = time.monotonic() - t0
                    if elapsed >= ORCHESTRATOR_TIMEOUT_S:
                        timed_out = True
                        orch_task.cancel()
                        break
                    yield _sse("status", {"phase": "thinking", "elapsed_s": round(elapsed, 1)})

            if timed_out:
                logger.error(f"[chat-stream] TIMEOUT apos {ORCHESTRATOR_TIMEOUT_S}s session={session_id}")
                yield _sse("error", {
                    "detail": f"Tempo esgotado apos {int(ORCHESTRATOR_TIMEOUT_S)}s. Tenta reformular ou pedir algo mais simples.",
                })
                return

            elapsed = time.monotonic() - t0
            logger.info(f"[chat-stream] project_orchestrator concluido em {elapsed:.1f}s session={session_id}")
            result = orch_task.result()
            response_text = result.response

            yield _sse("status", {"phase": "writing"})

            # Chunks de ~80 chars com sleep curto pra dar UX de typing
            CHUNK = 80
            for i in range(0, len(response_text), CHUNK):
                yield _sse("chunk", {"text": response_text[i : i + CHUNK]})
                await asyncio.sleep(0.02)

            orchestration = result.data.get("orchestration") if isinstance(result.data, dict) else None
            if orchestration:
                capability = orchestration.get("capability", {}) if isinstance(orchestration, dict) else {}
                await _add_chat_log(
                    agent="Orchestrator",
                    message=(
                        f"Habilidade: {capability.get('name', 'desconhecida')} | "
                        f"Intent: {orchestration.get('intent', 'desconhecido')}"
                    ),
                    log_type="decision",
                    metadata={"orchestration": orchestration},
                )

            await _add_chat_log(
                agent="Jobs",
                message=response_text,
                log_type="agent",
                metadata={"orchestration": orchestration} if orchestration else None,
            )

            if user_id:
                asyncio.create_task(asyncio.to_thread(
                    _track_analytics_sync, user_id, "chat_message", {"session_id": session_id}
                ))
                asyncio.create_task(asyncio.to_thread(
                    _auto_save_response_to_library, user_id, response_text
                ))

            from app.core.model_factory import get_llm_status
            llm_info = get_llm_status()
            yield _sse("done", {
                "session_id": session_id,
                "llm_provider": llm_info["active_provider"],
                "llm_label": llm_info["active_provider_label"],
                "full": response_text,
                "elapsed_s": round(elapsed, 1),
                **result.data,
            })

        except Exception as e:
            logger.error(f"Chat stream error: {e}", exc_info=True)
            await _add_chat_log(agent="System", message=f"Error: {str(e)}", log_type="system")
            yield _sse("error", {"detail": str(e)})

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Traefik/nginx nao bufferiza SSE
            "Connection": "keep-alive",
        },
    )


def _track_analytics_sync(user_id: str, action_type: str, metadata: dict):
    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        client.table("usage_analytics").insert({
            "user_id": user_id,
            "action_type": action_type,
            "metadata": metadata,
        }).execute()
    except Exception as e:
        logger.warning(f"Analytics tracking failed: {e}")


async def _track_analytics(user_id: str, action_type: str, metadata: dict):
    await asyncio.to_thread(_track_analytics_sync, user_id, action_type, metadata)


def _auto_save_response_to_library(user_id: str, response_text: str):
    """Detecta URLs de imagens na resposta e salva na biblioteca se nao existirem."""
    if not user_id or not response_text:
        return

    try:
        from app.api.v1.endpoints.library import save_asset
        from app.core.supabase import get_supabase

        client = get_supabase()
        image_urls = re.findall(
            r'(https?://[^\s\)\"\']+\.(?:png|jpg|jpeg|webp))',
            response_text, re.IGNORECASE
        )
        for url in image_urls:
            existing = client.table("content_assets").select("id").eq(
                "user_id", user_id
            ).eq("url", url).execute()
            if not existing.data:
                save_asset(
                    user_id=user_id,
                    asset_type="image",
                    title="Imagem gerada",
                    url=url,
                    thumbnail_url=url,
                )
                logger.info(f"[AutoSave] Image saved to library: {url[:80]}")
    except Exception as e:
        logger.warning(f"[AutoSave] Failed: {e}")
