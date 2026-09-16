from __future__ import annotations

import datetime as _dt
import logging
import re
from typing import Optional

from app.orchestrator.schemas import ClientContext

logger = logging.getLogger(__name__)

_MEMORY_HINT_RE = re.compile(
    r"\b(prefiro|nao gosto|não gosto|gosto de|minha marca|meu publico|meu público|"
    r"cliente ideal|tom de voz|nunca use|sempre use|aprenda|lembre|memorize)\b",
    re.IGNORECASE,
)


def load_client_context(
    user_id: Optional[str],
    org_id: Optional[str],
    brand_id: Optional[str],
) -> ClientContext:
    user_context = ""
    brand_context = ""
    vault_context = ""

    if brand_id:
        try:
            from app.services.profile_cache import get_brand_context
            brand_context = get_brand_context(brand_id) or ""
        except Exception as exc:
            logger.warning("brand context unavailable: %s", exc)

    if user_id:
        try:
            from app.services.profile_cache import get_user_context
            user_context = get_user_context(user_id) or ""
        except Exception as exc:
            logger.warning("user context unavailable: %s", exc)

    try:
        from app.services.user_memory import get_memory_prompt
        vault_context = get_memory_prompt() or ""
    except Exception as exc:
        logger.warning("vault context unavailable: %s", exc)

    return ClientContext(
        user_id=user_id,
        org_id=org_id,
        brand_id=brand_id,
        user_context=user_context,
        brand_context=brand_context,
        vault_context=vault_context,
    )


def maybe_store_user_learning(message: str, response_summary: str = "") -> bool:
    """Persist explicit preference/identity statements into MEMORY.md."""
    if not message or not _MEMORY_HINT_RE.search(message):
        return False
    try:
        from app.services.user_memory import add_memory_entry
        now = _dt.datetime.utcnow().strftime("%Y-%m-%d")
        entry = f"- {now}: Usuario informou: {message.strip()[:500]}"
        if response_summary:
            entry += f" | Sistema: {response_summary.strip()[:220]}"
        add_memory_entry("aprendizados do cliente", entry)
        return True
    except Exception as exc:
        logger.warning("failed to persist learning: %s", exc)
        return False

