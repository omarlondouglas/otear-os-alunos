"""Perplexity scraper — chama sonar-pro. Mantemos pago (~$5/mes ilimitado)."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

import httpx

logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "sonar-pro")


async def fetch_perplexity_news(niche: str, top_n: int = 3) -> str:
    """Pergunta ao Perplexity as top N noticias do dia para o nicho. Retorna texto bruto."""
    if not PERPLEXITY_API_KEY:
        logger.warning("[perplexity] PERPLEXITY_API_KEY ausente — pulando")
        return ""

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prompt = (
        f"Quais sao as top {top_n} noticias de {niche} hoje, {today}? "
        f"Para cada noticia, devolva: headline e content (resumo de 2-3 frases). "
        f"Sem citacoes do tipo [1]. Em portugues."
    )

    try:
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": PERPLEXITY_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            r.raise_for_status()
            data = r.json()
        text = data["choices"][0]["message"]["content"]
        # remove citacoes [1], [2][3]
        import re as _re
        return _re.sub(r"\[\d+\]", "", text).strip()
    except Exception as e:
        logger.warning(f"[perplexity] falhou: {e}")
        return ""
