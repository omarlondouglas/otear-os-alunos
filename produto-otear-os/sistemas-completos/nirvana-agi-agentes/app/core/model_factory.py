"""
Model Factory: seleciona um provider LLM por API, sem camada de CLI.

Prioridade quando MODEL_PROVIDER nao esta definido:
1. OpenRouter, se OPENROUTER_API_KEY existir
2. Anthropic SDK, se ANTHROPIC_API_KEY existir
3. Google Gemini, se GOOGLE_API_KEY existir
"""
import os

from agno.utils.log import logger


_MODEL_IDS = {
    "planner": lambda: os.getenv("MODEL_PLANNER", ""),
    "writer": lambda: os.getenv("MODEL_WRITER", ""),
    "fast": lambda: os.getenv("MODEL_FAST", ""),
}

_OPENROUTER_MODEL_IDS = {
    "planner": lambda: os.getenv("OPENROUTER_MODEL_PLANNER", os.getenv("OPENROUTER_MODEL", "")),
    "writer": lambda: os.getenv("OPENROUTER_MODEL_WRITER", os.getenv("OPENROUTER_MODEL", "")),
    "fast": lambda: os.getenv("OPENROUTER_MODEL_FAST", os.getenv("OPENROUTER_MODEL", "")),
}

_OPENROUTER_DEFAULTS = {
    "planner": "openai/gpt-4o-mini",
    "writer": "openai/gpt-4o-mini",
    "fast": "openai/gpt-4o-mini",
}

_CLAUDE_DEFAULTS = {
    "planner": "claude-sonnet-4-6",
    "writer": "claude-sonnet-4-6",
    "fast": "claude-haiku-4-5-20251001",
}

_GEMINI_DEFAULTS = {
    "planner": "gemini-3-flash-preview",
    "writer": "gemini-3-flash-preview",
    "fast": "gemini-3-flash-preview",
}


def _openrouter_headers() -> dict:
    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name
    return headers


def _normalize_provider(provider: str) -> str:
    provider = (provider or "").strip().lower()
    aliases = {
        "open-router": "openrouter",
        "open_router": "openrouter",
        "anthropic": "claude",
        "claude-sdk": "claude",
        "google": "gemini",
        "google-gemini": "gemini",
        "google_gemini": "gemini",
    }
    return aliases.get(provider, provider)


def _looks_like_gemini_model(model_id: str) -> bool:
    return (model_id or "").strip().lower().startswith("gemini")


def _provider_from_env() -> str:
    provider = _normalize_provider(os.getenv("MODEL_PROVIDER", ""))
    if provider:
        if provider in ("codex", "codex-cli", "codex_cli", "claude-cli", "claude_code"):
            logger.warning(
                "ModelFactory: provider CLI ignorado. Use openrouter, claude ou gemini com API key."
            )
            provider = ""
        else:
            return provider

    if os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    return "none"


def _openrouter_model_id(role: str) -> str:
    return (
        _OPENROUTER_MODEL_IDS.get(role, _OPENROUTER_MODEL_IDS["planner"])()
        or _OPENROUTER_DEFAULTS.get(role, _OPENROUTER_DEFAULTS["planner"])
    )


def _claude_model_id(role: str) -> str:
    model_id = _MODEL_IDS.get(role, _MODEL_IDS["planner"])()
    if not model_id or _looks_like_gemini_model(model_id) or model_id.lower().startswith(("gpt-", "o1", "o3", "o4")):
        return _CLAUDE_DEFAULTS.get(role, _CLAUDE_DEFAULTS["planner"])
    return model_id


def _gemini_model_id(role: str) -> str:
    return _MODEL_IDS.get(role, _MODEL_IDS["planner"])() or _GEMINI_DEFAULTS.get(role, _GEMINI_DEFAULTS["planner"])


def get_model(role: str = "planner"):
    """Retorna o model Agno configurado por API key. Nao usa CLI."""
    provider = _provider_from_env()

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("MODEL_PROVIDER=openrouter, mas OPENROUTER_API_KEY nao esta configurada")
        model_id = _openrouter_model_id(role)
        logger.info(f"ModelFactory: usando OpenRouter ({model_id})")
        from agno.models.openai import OpenAIChat

        return OpenAIChat(
            id=model_id,
            api_key=api_key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            extra_headers=_openrouter_headers() or None,
        )

    if provider == "claude":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise RuntimeError("MODEL_PROVIDER=claude, mas ANTHROPIC_API_KEY nao esta configurada")
        model_id = _claude_model_id(role)
        logger.info(f"ModelFactory: usando Claude SDK ({model_id})")
        from agno.models.anthropic import Claude

        return Claude(id=model_id)

    if provider == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            raise RuntimeError("MODEL_PROVIDER=gemini, mas GOOGLE_API_KEY nao esta configurada")
        model_id = _gemini_model_id(role)
        logger.info(f"ModelFactory: usando Gemini SDK ({model_id})")
        from agno.models.google import Gemini

        return Gemini(id=model_id)

    raise RuntimeError(
        "Nenhum provider LLM por API configurado. Configure OPENROUTER_API_KEY, "
        "ANTHROPIC_API_KEY ou GOOGLE_API_KEY."
    )


def get_llm_status() -> dict:
    """Return the active API LLM provider and model status."""
    provider = _provider_from_env()
    has_openrouter_key = bool(os.getenv("OPENROUTER_API_KEY"))
    has_anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_google_key = bool(os.getenv("GOOGLE_API_KEY"))

    if provider == "openrouter":
        label = "OpenRouter"
        models = {
            "planner": _openrouter_model_id("planner"),
            "writer": _openrouter_model_id("writer"),
            "fast": _openrouter_model_id("fast"),
        }
    elif provider == "claude":
        label = "Claude SDK (API Key)"
        models = {
            "planner": _claude_model_id("planner"),
            "writer": _claude_model_id("writer"),
            "fast": _claude_model_id("fast"),
        }
    elif provider == "gemini":
        label = "Google Gemini"
        models = {
            "planner": _gemini_model_id("planner"),
            "writer": _gemini_model_id("writer"),
            "fast": _gemini_model_id("fast"),
        }
    else:
        provider = "none"
        label = "Nenhum LLM API configurado"
        models = {}

    return {
        "active_provider": provider,
        "active_provider_label": label,
        "models": models,
        "openrouter_available": has_openrouter_key,
        "gemini_available": has_google_key,
        "claude_sdk_available": has_anthropic_key,
        "cli_layer_enabled": False,
        "gemini_images_only": provider != "gemini" and has_google_key,
    }
