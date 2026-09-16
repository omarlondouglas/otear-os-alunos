#!/usr/bin/env python3
"""Fetch RSS news through the O Tear API and structure it as a short script."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any

try:
    import httpx
except ImportError as exc:  # pragma: no cover - depends on Hermes env
    raise SystemExit(
        json.dumps(
            {
                "ok": False,
                "error": "Dependencia ausente: instale com `pip install -r requirements.txt` nesta skill.",
            },
            ensure_ascii=False,
        )
    ) from exc


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} nao configurado")
    return value.strip()


def _api_url() -> str:
    return _env("OTEAR_API_URL", "http://localhost:8000").rstrip("/")


def _api_key() -> str:
    return _env("OTEAR_API_KEY")


def _timeout(default: int = 30) -> float:
    raw = os.getenv("OTEAR_TIMEOUT_S", str(default)).strip()
    try:
        return float(raw)
    except ValueError:
        return float(default)


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "X-API-Key": api_key,
    }


def _request_json(url: str, *, api_key: str, timeout_s: float, params: dict[str, Any]) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            response = client.get(url, headers=_headers(api_key), params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise RuntimeError(f"O Tear API HTTP {exc.response.status_code}: {detail}") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"O Tear API indisponivel: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("O Tear API retornou resposta que nao e JSON") from exc


def fetch_feed(query: str, *, limit: int, api_url: str, api_key: str, timeout_s: float) -> dict[str, Any]:
    data = _request_json(
        f"{api_url}/api/v1/news/feed",
        api_key=api_key,
        timeout_s=timeout_s,
        params={
            "source": "rss",
            "search": query,
            "limit": limit,
        },
    )
    return {
        "ok": True,
        "mode": "feed",
        "query": query,
        "total": data.get("total", 0),
        "sources": data.get("sources") or {},
        "source_errors": data.get("source_errors") or {},
        "generated_at": data.get("generated_at"),
        "items": data.get("items") or [],
    }


def _text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    rendered = str(value).strip()
    return rendered or fallback


def _pick_primary(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    with_url = [item for item in items if _text(item.get("url"))]
    return (with_url or items)[0] if items else None


def _script_markdown(query: str, primary: dict[str, Any], alternatives: list[dict[str, Any]]) -> str:
    title = _text(primary.get("title"), "Noticia sem titulo")
    source = _text(primary.get("source_label"), "RSS")
    url = _text(primary.get("url"), "sem URL")
    published_at = _text(primary.get("published_at"), "data nao informada")
    summary = _text(primary.get("summary"), "Resumo nao informado pelo feed.")

    alt_lines = []
    for index, item in enumerate(alternatives[:4], start=1):
        alt_title = _text(item.get("title"), "Noticia sem titulo")
        alt_source = _text(item.get("source_label"), "RSS")
        alt_url = _text(item.get("url"), "")
        suffix = f" - {alt_url}" if alt_url else ""
        alt_lines.append(f"{index}. {alt_title} - {alt_source}{suffix}")
    alternatives_block = "\n".join(alt_lines) if alt_lines else "Sem alternativas relevantes retornadas pelo RSS."

    return f"""# Roteiro baseado em noticia RSS

## Query usada
{query}

## Noticia principal
- Titulo: {title}
- Fonte: {source}
- Publicado em: {published_at}
- URL: {url}
- Resumo: {summary}

## Angle
Explicar por que esta noticia importa agora e qual mudanca pratica ela sinaliza.

## Theme
{query}

## Primary Trigger
Ruptura / oportunidade.

## Script
Hook:
Saiu uma noticia que pode mudar como a gente olha para {query}: {title}

Development:
Segundo {source}, {summary}

O ponto importante nao e so a manchete. E o que ela indica: quem entender isso cedo consegue transformar uma noticia em decisao, conteudo ou vantagem pratica antes do mercado tratar como obvio.

Closing:
Se voce acompanha {query}, vale abrir a fonte original e olhar os detalhes antes de tirar conclusoes. O link esta aqui: {url}

## On-Screen Editing
- Abrir com a manchete em tela.
- Mostrar o nome da fonte e a data.
- Destacar 2 palavras-chave da noticia.
- Fechar com pergunta: "isso e oportunidade ou alerta?"

## Delivery Notes
- Tom direto, rapido e factual.
- Nao afirmar nada alem do que a fonte confirma.
- Marcar interpretacoes como leitura editorial.

## Alternativas
{alternatives_block}

## Checagens recomendadas
- Confirmar a noticia na URL original.
- Verificar se a data e recente o suficiente para o contexto.
- Evitar transformar inferencia editorial em fato.
"""


def build_script_result(feed: dict[str, Any]) -> dict[str, Any]:
    items = list(feed.get("items") or [])
    primary = _pick_primary(items)
    if not primary:
        return {
            **feed,
            "mode": "script",
            "selected_news": None,
            "alternatives": [],
            "script_markdown": "",
            "warning": "Nenhuma noticia retornada pelo RSS para estruturar roteiro.",
        }

    alternatives = [item for item in items if item is not primary][:4]
    return {
        **feed,
        "mode": "script",
        "selected_news": primary,
        "alternatives": alternatives,
        "script_markdown": _script_markdown(str(feed.get("query") or ""), primary, alternatives),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Busca noticias RSS via O Tear API e estrutura roteiro.")
    parser.add_argument("query", help="tema, nicho ou palavra-chave")
    parser.add_argument("--limit", type=int, default=20, help="quantidade maxima de noticias")
    parser.add_argument("--format", choices=["script", "json"], default="script", help="saida estruturada")
    parser.add_argument("--dry-run", action="store_true", help="imprime a chamada planejada sem executar")
    parser.add_argument("--timeout", type=float, default=None, help="timeout em segundos")
    args = parser.parse_args()

    started = time.time()
    try:
        query = args.query.strip()
        if not query:
            raise RuntimeError("query vazia")

        limit = max(1, min(args.limit, 100))
        api_url = _api_url()
        timeout_s = args.timeout if args.timeout is not None else _timeout()

        if args.dry_run:
            result = {
                "ok": True,
                "mode": "dry_run",
                "method": "GET",
                "url": api_url + "/api/v1/news/feed",
                "params": {
                    "source": "rss",
                    "search": query,
                    "limit": limit,
                },
                "format": args.format,
                "duration_ms": int((time.time() - started) * 1000),
            }
            print(json.dumps(result, ensure_ascii=False))
            return 0

        feed = fetch_feed(query, limit=limit, api_url=api_url, api_key=_api_key(), timeout_s=timeout_s)
        result = build_script_result(feed) if args.format == "script" else feed
        result["duration_ms"] = int((time.time() - started) * 1000)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(exc),
                    "duration_ms": int((time.time() - started) * 1000),
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
