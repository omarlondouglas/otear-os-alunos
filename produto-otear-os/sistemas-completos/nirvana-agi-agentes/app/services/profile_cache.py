"""
Cache TTL em memoria pra user_profile e brand context.

O chat.py carrega esses dois em CADA mensagem do usuario, fazendo 1-2 queries
Supabase a cada turn (200-500ms). Como mudanca em profile/brand e rara, cachear
60s elimina esse overhead sem custo de freshness perceptivel.

Cache invalida automaticamente em 60s. Pra invalidacao manual (ex: usuario
acabou de salvar perfil), chame `invalidate_user(user_id)` ou `invalidate_brand(brand_id)`.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Optional, Tuple

TTL_SECONDS = 60.0

_lock = threading.Lock()
_user_cache: dict[str, Tuple[float, str]] = {}
_brand_cache: dict[str, Tuple[float, str]] = {}


def get_user_context(user_id: str) -> Optional[str]:
    """Retorna texto de contexto do user_profile (ja formatado), com cache."""
    if not user_id:
        return None
    now = time.time()
    with _lock:
        cached = _user_cache.get(user_id)
        if cached and (now - cached[0]) < TTL_SECONDS:
            return cached[1]

    try:
        from app.models.user_profile import get_user_profile, build_user_context
        profile = get_user_profile(user_id)
        ctx = build_user_context(profile) or ""
    except Exception:
        return None

    with _lock:
        _user_cache[user_id] = (now, ctx)
    return ctx


def get_brand_context(brand_id: str) -> Optional[str]:
    """Retorna texto de contexto da brand (ja formatado), com cache."""
    if not brand_id:
        return None
    now = time.time()
    with _lock:
        cached = _brand_cache.get(brand_id)
        if cached and (now - cached[0]) < TTL_SECONDS:
            return cached[1]

    try:
        from app.models.brand import get_brand, build_brand_context
        brand = get_brand(brand_id)
        ctx = build_brand_context(brand) or ""
    except Exception:
        return None

    with _lock:
        _brand_cache[brand_id] = (now, ctx)
    return ctx


def invalidate_user(user_id: str) -> None:
    with _lock:
        _user_cache.pop(user_id, None)


def invalidate_brand(brand_id: str) -> None:
    with _lock:
        _brand_cache.pop(brand_id, None)


def clear_all() -> None:
    with _lock:
        _user_cache.clear()
        _brand_cache.clear()
