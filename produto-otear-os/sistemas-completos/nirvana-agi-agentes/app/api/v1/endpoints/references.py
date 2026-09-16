"""
References API — leitura do vault de creators.

Endpoints (consumidos pelo frontend de Referencias):
  GET    /api/v1/references/creators                       lista creators + status
  GET    /api/v1/references/creators/{handle}              perfil agregado (estilo + comunicacao)
  GET    /api/v1/references/creators/{handle}/videos       lista posts (sem transcript)
  GET    /api/v1/references/creators/{handle}/videos/{id}  post completo + transcript
  POST   /api/v1/references/creators                       enfileira nova extracao manual
  DELETE /api/v1/references/creators/{handle}              remove do vault
  GET    /api/v1/references/jobs/{job_id}                  status do job Celery

Observacao sobre handle: aceita com ou sem @ — normaliza internamente.
"""
from __future__ import annotations

import json
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.social.markdown_writer import (
    REFERENCES_DIR, get_creator_dir, list_creators, read_meta,
)
from app.services.social.parser import parse_social_handle

router = APIRouter()


# ─── Models ───────────────────────────────────────────────────────────────────

class CreatorListItem(BaseModel):
    handle: str
    kind: str
    platform: str
    status: str
    posts_total: int
    posts_done: int
    last_extraction: Optional[str] = None


class CreatorStyle(BaseModel):
    hook_patterns: List[str] = []
    narrative_arc: str = ""
    vocabulary: List[str] = []
    emotional_triggers: List[str] = []


class CreatorCommunication(BaseModel):
    tone: str = ""
    pacing: str = ""
    visual_format: str = ""
    cta_style: str = ""


class CreatorProfile(BaseModel):
    handle: str
    platform: str
    kind: str
    posts_analyzed: int
    last_extraction: Optional[str] = None
    estilo: CreatorStyle
    comunicacao: CreatorCommunication
    summary: str = ""


class VideoListItem(BaseModel):
    post_id: str
    platform: str
    handle: str
    url: str
    duration: float
    posted_at: Optional[str] = None
    play_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    caption_preview: str = ""  # primeiros 200 chars


class VideoDetail(VideoListItem):
    caption: str = ""
    transcript: str = ""
    hook_literal: str = ""
    hook_type: str = ""
    script_analysis: str = ""
    reusable_patterns: List[str] = []


class CreateExtractionRequest(BaseModel):
    handle: str
    platform: str = "unknown"
    kind: str = "inspiration"
    posts_count: int = 10


class CreateVideoReferenceRequest(BaseModel):
    url: str
    label: str = ""
    platform: str = "unknown"
    kind: str = "inspiration"


class CreateExtractionResponse(BaseModel):
    handle: str
    job_id: str
    status: str = "queued"


class JobStatusResponse(BaseModel):
    job_id: str
    state: str
    handle: Optional[str] = None
    posts_done: Optional[int] = None
    posts_total: Optional[int] = None
    error: Optional[str] = None


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _normalize_handle(handle: str) -> str:
    parsed = parse_social_handle(handle)
    if parsed:
        h = parsed.handle.strip().lstrip("@").lower()
    else:
        h = handle.strip().strip("/").lstrip("@").lower()
    if not h:
        raise HTTPException(status_code=400, detail="handle vazio")
    return f"@{h}"


def _normalize_creator_target(handle: str, platform: str) -> tuple[str, str]:
    parsed = parse_social_handle(handle)
    normalized = _normalize_handle(handle)
    resolved_platform = platform
    if platform == "unknown" and parsed and parsed.platform != "unknown":
        resolved_platform = parsed.platform
    return normalized, resolved_platform


def _ensure_creator_exists(handle: str) -> Path:
    d = get_creator_dir(handle)
    if not d.exists():
        raise HTTPException(status_code=404, detail=f"Creator '{handle}' nao encontrado no vault")
    return d


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    """Parser YAML simples (chave: valor) sem dependencia de PyYAML."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    fm: Dict[str, Any] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip().strip('"').strip("'")
        if v.lower() == "null" or v == "":
            fm[k.strip()] = None
        elif v.isdigit():
            fm[k.strip()] = int(v)
        else:
            try:
                fm[k.strip()] = float(v) if "." in v and v.replace(".", "").isdigit() else v
            except ValueError:
                fm[k.strip()] = v
    return fm, body


def _parse_profile_md(path: Path) -> Dict[str, Any]:
    """Le _profile.md e estrutura para a UI."""
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    # Quebra body em secoes por heading
    sections: Dict[str, str] = {}
    matches = list(_HEADING_RE.finditer(body))
    for i, m in enumerate(matches):
        title = _normalize_heading(m.group(2))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()

    def _bullets(text: str) -> List[str]:
        return [
            ln.lstrip("- ").strip()
            for ln in text.splitlines()
            if ln.strip().startswith("-")
        ]

    def _csv(text: str) -> List[str]:
        clean = text.strip().strip("_")
        if not clean or clean.startswith("(nao"):
            return []
        return [s.strip() for s in clean.split(",") if s.strip()]

    raw_summary = sections.get("resumo", "").strip()
    hook_patterns = _bullets(sections.get("hook patterns", ""))
    if not hook_patterns:
        hook_patterns = _extract_string_list(raw_summary, "hook_patterns")

    style = CreatorStyle(
        hook_patterns=hook_patterns,
        narrative_arc=sections.get("estrutura narrativa", "").strip(),
        vocabulary=_csv(sections.get("vocabulario-chave", "")),
        emotional_triggers=_csv(sections.get("gatilhos emocionais", "")),
    )
    comm = CreatorCommunication(
        tone=sections.get("tom", "").strip(),
        pacing=sections.get("ritmo", "").strip(),
        visual_format=sections.get("formato visual", "").strip(),
        cta_style=sections.get("cta padrao", "").strip(),
    )

    return {
        "handle": fm.get("handle", ""),
        "platform": fm.get("platform", "unknown"),
        "kind": fm.get("kind", "unknown"),
        "posts_analyzed": int(fm.get("posts_analyzed", 0) or 0),
        "last_extraction": fm.get("last_extraction"),
        "estilo": style,
        "comunicacao": comm,
        "summary": raw_summary,
    }


def _extract_string_list(text: str, key: str) -> List[str]:
    """Extrai uma lista simples de strings de JSON bruto salvo como texto.

    Alguns perfis antigos guardaram a resposta do LLM em `Resumo` quando o JSON
    veio sem fence de fechamento. Esta rotina recupera campos como
    `hook_patterns` sem depender do JSON completo estar valido.
    """
    if not text:
        return []
    pattern = rf'"{re.escape(key)}"\s*:\s*\[(.*?)\]'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    return [
        item.strip()
        for item in re.findall(r'"([^"]+)"', match.group(1))
        if item.strip()
    ]


def _parse_post_md(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    # Caption e transcript estao em headings ## Caption / ## Transcript
    sections: Dict[str, str] = {}
    matches = list(_HEADING_RE.finditer(body))
    for i, m in enumerate(matches):
        title = _normalize_heading(m.group(2))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()

    caption = sections.get("caption", "").strip()
    if caption.startswith("_"):
        caption = ""
    transcript = sections.get("transcript", "").strip()
    if transcript.startswith("_"):
        transcript = ""
    script_analysis = _extract_heading_block(body, "Analise do roteiro").strip()
    if not script_analysis:
        script_analysis = sections.get("analise do roteiro", "").strip()

    hook_literal = sections.get("hook usado", "").strip()
    hook_type = sections.get("tipo de hook", "").strip()
    reusable_patterns: List[str] = []
    if script_analysis:
        hook_literal = hook_literal or _extract_subsection(script_analysis, "Hook usado")
        hook_type = hook_type or _extract_subsection(script_analysis, "Tipo de hook")
        reusable_raw = sections.get("padroes reutilizaveis", "").strip() or _extract_subsection(script_analysis, "Padroes reutilizaveis")
        reusable_patterns = [
            line.lstrip("- ").strip()
            for line in reusable_raw.splitlines()
            if line.strip().startswith("-")
        ]

    return {
        "post_id": str(fm.get("post_id", path.stem)),
        "platform": fm.get("platform", "unknown"),
        "handle": fm.get("handle", ""),
        "url": fm.get("url", ""),
        "duration": float(fm.get("duration", 0) or 0),
        "posted_at": fm.get("posted_at") or None,
        "play_count": fm.get("play_count"),
        "like_count": fm.get("like_count"),
        "comment_count": fm.get("comment_count"),
        "caption": caption,
        "transcript": transcript,
        "hook_literal": hook_literal,
        "hook_type": hook_type,
        "script_analysis": script_analysis,
        "reusable_patterns": reusable_patterns,
    }


def _extract_subsection(text: str, title: str) -> str:
    return _extract_heading_level(text, title, 3)


def _extract_heading_block(text: str, title: str) -> str:
    """Extrai uma secao ## preservando subsecoes ### internas."""
    return _extract_heading_level(text, title, 2)


def _normalize_heading(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).strip().lower()


def _extract_heading_level(text: str, title: str, level: int) -> str:
    target = _normalize_heading(title)
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for index, match in enumerate(matches):
        if _normalize_heading(match.group(1)) != target:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return ""


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/creators", response_model=List[CreatorListItem])
async def list_all_creators():
    """Lista todos os creators no vault com status. Frontend faz polling enquanto houver 'extracting'."""
    return list_creators()


@router.get("/creators/{handle}", response_model=CreatorProfile)
async def get_creator(handle: str):
    handle = _normalize_handle(handle)
    d = _ensure_creator_exists(handle)
    profile_path = d / "_profile.md"
    if not profile_path.exists():
        # Ainda nao analisado — devolve placeholder
        meta = read_meta(handle)
        return CreatorProfile(
            handle=handle,
            platform=meta.platform if meta else "unknown",
            kind=meta.kind if meta else "unknown",
            posts_analyzed=0,
            last_extraction=meta.finished_at if meta else None,
            estilo=CreatorStyle(),
            comunicacao=CreatorCommunication(),
            summary="Analise ainda nao concluida.",
        )
    return _parse_profile_md(profile_path)


@router.get("/creators/{handle}/videos", response_model=List[VideoListItem])
async def list_creator_videos(handle: str):
    handle = _normalize_handle(handle)
    d = _ensure_creator_exists(handle)
    out: List[VideoListItem] = []
    for p in sorted(d.glob("*.md")):
        if p.name.startswith("_"):
            continue
        try:
            data = _parse_post_md(p)
            out.append(VideoListItem(
                post_id=data["post_id"],
                platform=data["platform"],
                handle=data["handle"],
                url=data["url"],
                duration=data["duration"],
                posted_at=data["posted_at"],
                play_count=data["play_count"],
                like_count=data["like_count"],
                comment_count=data["comment_count"],
                caption_preview=(data["caption"] or "")[:200],
            ))
        except Exception:
            continue
    return out


@router.get("/creators/{handle}/videos/{video_id}", response_model=VideoDetail)
async def get_creator_video(handle: str, video_id: str):
    handle = _normalize_handle(handle)
    d = _ensure_creator_exists(handle)
    candidates = [p for p in d.glob(f"*{video_id}*.md") if not p.name.startswith("_")]
    if not candidates:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' nao encontrado")
    data = _parse_post_md(candidates[0])
    return VideoDetail(**data, caption_preview=(data["caption"] or "")[:200])


@router.post("/creators", response_model=CreateExtractionResponse, status_code=202)
async def create_extraction(request: CreateExtractionRequest):
    """Adiciona manualmente um creator e enfileira extracao em background.

    Usado pelo botao '+ Adicionar' da UI ou via chat com o agente.
    """
    handle, platform = _normalize_creator_target(request.handle, request.platform)
    try:
        from app.workers.social_tasks import extract_creator_profile_task
        result = extract_creator_profile_task.apply_async(
            kwargs={
                "handle": handle,
                "platform": platform,
                "kind": request.kind,
                "posts_count": request.posts_count,
            },
            priority=5,
        )
        return CreateExtractionResponse(handle=handle, job_id=result.id, status="queued")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Celery offline ou erro: {e}")


@router.post("/videos", response_model=CreateExtractionResponse, status_code=202)
async def create_video_reference(request: CreateVideoReferenceRequest):
    """Adiciona uma URL de video avulsa como referencia de estilo.

    O video e baixado via yt-dlp/play_url, transcrito e salvo no mesmo vault de
    referencias, como uma entrada de 1 post.
    """
    if not request.url.strip().startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL de video invalida")

    try:
        from app.workers.social_tasks import extract_video_reference_task
        result = extract_video_reference_task.apply_async(
            kwargs={
                "url": request.url.strip(),
                "label": request.label.strip(),
                "platform": request.platform,
                "kind": request.kind,
            },
            priority=5,
        )
        # O handle final e gerado dentro da task apos hash da URL. Retornamos job_id.
        return CreateExtractionResponse(handle=request.label or request.url, job_id=result.id, status="queued")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Celery offline ou erro: {e}")


@router.delete("/creators/{handle}", status_code=204)
async def delete_creator(handle: str):
    handle = _normalize_handle(handle)
    d = _ensure_creator_exists(handle)
    shutil.rmtree(d)
    return None


class ScreenshotRequest(BaseModel):
    handle: str
    count: int = 9


class ScreenshotResponse(BaseModel):
    profile: str
    captured_at: str
    grid_url: str
    post_urls: List[str]
    post_count: int


@router.post("/screenshots", response_model=ScreenshotResponse, status_code=201)
async def capture_screenshots(request: ScreenshotRequest):
    """Tira prints visuais de um perfil Instagram via Playwright (sessao persistente).

    Diferente do /creators/{handle}/videos (que mostra metadata extraida pelo
    instaloader), este endpoint produz screenshots PNG do perfil real para
    referencia visual ('quero copiar a pegada do @x').
    """
    try:
        from app.services.instagram_playwright import capture_profile_screenshots
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Playwright nao disponivel: {e}")

    try:
        result = await capture_profile_screenshots(
            handle=request.handle,
            count=request.count,
            headless=True,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

    # Converte paths absolutos pra URLs servidas via /static/
    import os as _os
    storage = _os.getenv("STORAGE_PATH", "/app/storage").rstrip("/")
    public_base = _os.getenv("PUBLIC_API_URL", "").rstrip("/")

    def _to_url(path: str) -> str:
        rel = path.replace(storage, "").replace("\\", "/").lstrip("/")
        return f"{public_base}/static/{rel}" if public_base else f"/static/{rel}"

    return ScreenshotResponse(
        profile=result["profile"],
        captured_at=result["captured_at"],
        grid_url=_to_url(result["grid_path"]),
        post_urls=[_to_url(p) for p in result["post_paths"]],
        post_count=result["post_count"],
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Status do job Celery. Frontend pode usar como alternativa ao polling de /creators."""
    try:
        from celery.result import AsyncResult
        from app.core.celery_app import celery_app

        result = AsyncResult(job_id, app=celery_app)
        state = result.state
        info: Dict[str, Any] = {}
        if isinstance(result.info, dict):
            info = result.info
        elif isinstance(result.info, Exception):
            info = {"error": str(result.info)}

        return JobStatusResponse(
            job_id=job_id,
            state=state,
            handle=info.get("handle"),
            posts_done=info.get("posts_done"),
            posts_total=info.get("posts_total"),
            error=info.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro consultando Celery: {e}")
