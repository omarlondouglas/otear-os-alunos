"""
LLM cascade compartilhado: OpenRouter -> Anthropic -> OpenAI -> Gemini -> Groq.

Reaproveita o pattern do select_clips e fica acessivel pra qualquer servico
(news_digest, etc.). Use `call_llm(prompt)` que devolve o primeiro provider
que responder, ou None se todos falharem.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

ANTHROPIC_MODEL = os.getenv("LLM_CASCADE_ANTHROPIC_MODEL", "claude-sonnet-4-6")
OPENROUTER_MODEL = os.getenv("LLM_CASCADE_OPENROUTER_MODEL", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"))
OPENAI_MODEL = os.getenv("LLM_CASCADE_OPENAI_MODEL", "gpt-4.1-mini")
GEMINI_MODEL = os.getenv("LLM_CASCADE_GEMINI_MODEL", "gemini-2.5-flash")
GROQ_MODEL = os.getenv("LLM_CASCADE_GROQ_MODEL", "llama-3.3-70b-versatile")


def _openrouter_headers() -> dict:
    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name
    return headers


def _try_openrouter(prompt: str, max_tokens: int) -> Optional[str]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=key,
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            default_headers=_openrouter_headers() or None,
        )
        logger.info(f"[llm_cascade] -> OpenRouter ({OPENROUTER_MODEL})")
        resp = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"[llm_cascade] OpenRouter falhou: {e}")
        return None


def _try_anthropic(prompt: str, max_tokens: int) -> Optional[str]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=key)
        logger.info(f"[llm_cascade] -> Claude ({ANTHROPIC_MODEL})")
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text
    except Exception as e:
        logger.warning(f"[llm_cascade] Anthropic falhou: {e}")
        return None


def _try_openai(prompt: str, max_tokens: int) -> Optional[str]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        logger.info(f"[llm_cascade] -> OpenAI ({OPENAI_MODEL})")
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"[llm_cascade] OpenAI falhou: {e}")
        return None


def _try_gemini(prompt: str, max_tokens: int) -> Optional[str]:
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        logger.info(f"[llm_cascade] -> Gemini ({GEMINI_MODEL})")
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens},
        )
        return resp.text
    except Exception as e:
        logger.warning(f"[llm_cascade] Gemini falhou: {e}")
        return None


def _try_groq(prompt: str, max_tokens: int) -> Optional[str]:
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=key)
        logger.info(f"[llm_cascade] -> Groq ({GROQ_MODEL})")
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.warning(f"[llm_cascade] Groq falhou: {e}")
        return None


def call_llm(prompt: str, max_tokens: int = 4000) -> Optional[str]:
    """Cascata: OpenRouter -> Anthropic -> OpenAI -> Gemini -> Groq. Retorna primeiro sucesso."""
    for provider in (_try_openrouter, _try_anthropic, _try_openai, _try_gemini, _try_groq):
        text = provider(prompt, max_tokens)
        if text:
            return text
    logger.error("[llm_cascade] todos os providers falharam")
    return None
