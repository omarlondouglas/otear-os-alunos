from __future__ import annotations

import re
from typing import Optional

from app.orchestrator.schemas import Intent

_URL_RE = re.compile(r"https?://[^\s)>\"]+", re.IGNORECASE)
_JOB_RE = re.compile(r"\b(?:job[_\s-]?id|task[_\s-]?id|id)\s*[:#-]?\s*([a-zA-Z0-9_.:-]{6,})", re.IGNORECASE)


def classify_intent(message: str) -> Intent:
    text = (message or "").lower()

    if any(word in text for word in ("status", "andamento", "progresso", "job id", "job_id")):
        if "video" in text or _JOB_RE.search(text):
            return Intent.VIDEO_STATUS

    if any(word in text for word in ("carrossel", "carousel", "post em slides", "slides para instagram")):
        return Intent.CAROUSEL

    has_linkedin = "linkedin" in text or "linked in" in text
    has_linkedin_text_format = any(
        word in text
        for word in ("post", "texto", "artigo", "copy", "publicacao", "publicação")
    )
    has_authority_post_signal = any(
        signal in text
        for signal in ("post longo", "post de autoridade", "artigo de autoridade", "texto de autoridade")
    )
    if (has_linkedin and has_linkedin_text_format) or has_authority_post_signal:
        return Intent.LINKEDIN_POST

    if any(word in text for word in ("edite", "editar", "legenda", "legendas", "corte", "shorts", "reels")):
        if "video" in text or extract_url(message):
            return Intent.VIDEO_EDIT

    if any(word in text for word in ("imagem", "capa", "thumbnail", "visual", "arte")):
        return Intent.IMAGE

    if any(word in text for word in ("roteiro", "script", "copy", "texto", "anuncio", "anuncio")):
        return Intent.SCRIPT

    if any(word in text for word in ("aprenda", "lembre", "memorize", "prefiro", "nao gosto", "não gosto", "minha marca")):
        return Intent.MEMORY

    if any(word in text for word in ("estrategia", "estratégia", "campanha", "planeje", "plano", "funil")):
        return Intent.STRATEGY

    return Intent.GENERAL


def extract_url(message: str) -> Optional[str]:
    match = _URL_RE.search(message or "")
    return match.group(0).rstrip(".,") if match else None


def extract_job_id(message: str) -> Optional[str]:
    match = _JOB_RE.search(message or "")
    return match.group(1) if match else None
