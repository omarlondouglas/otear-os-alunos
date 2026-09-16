#!/usr/bin/env python3
"""Call O Tear Agentes orchestrator from Hermes."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} nao configurado")
    return value.strip()


def _post_chat(
    api_url: str,
    api_key: str,
    message: str,
    session_id: str | None,
    source: str,
    brand_id: str | None,
    timeout_s: int,
) -> dict:
    url = api_url.rstrip("/") + "/api/v1/chat"
    context = {
        "source": source,
        "channel": "hermes",
    }
    if session_id:
        context["session_id"] = session_id

    payload: dict = {
        "message": message,
        "context": context,
    }
    if brand_id:
        payload["brand_id"] = brand_id

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Tear API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Tear API indisponivel: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("message", help="pedido completo para O Tear Agentes")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--source", default="hermes")
    parser.add_argument("--brand-id", default=None)
    parser.add_argument("--timeout", type=int, default=int(os.getenv("OTEAR_TIMEOUT_S", "150")))
    args = parser.parse_args()

    started = time.time()
    try:
        api_url = _env("OTEAR_API_URL", "http://localhost:8000")
        api_key = _env("OTEAR_API_KEY")
        brand_id = args.brand_id or os.getenv("OTEAR_DEFAULT_BRAND_ID")

        result = _post_chat(
            api_url=api_url,
            api_key=api_key,
            message=args.message,
            session_id=args.session_id,
            source=args.source,
            brand_id=brand_id,
            timeout_s=args.timeout,
        )
        duration_ms = int((time.time() - started) * 1000)
        print(json.dumps({
            "response": result.get("response", ""),
            "data": result.get("data") or {},
            "duration_ms": duration_ms,
        }, ensure_ascii=False))
        return 0
    except Exception as exc:
        duration_ms = int((time.time() - started) * 1000)
        print(json.dumps({
            "error": str(exc),
            "duration_ms": duration_ms,
        }, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
