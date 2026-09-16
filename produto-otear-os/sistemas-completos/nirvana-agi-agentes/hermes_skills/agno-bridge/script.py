#!/usr/bin/env python3
"""Call an O Tear Agentes specialist agent through the public API."""

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


def _post_agent(
    api_url: str,
    api_key: str,
    agent: str,
    task: str,
    user_id: str | None,
    org_id: str | None,
    brand_id: str | None,
    timeout_s: int,
) -> dict:
    url = api_url.rstrip("/") + f"/api/v1/agents/{agent}/run"
    context = {}
    if org_id:
        context["org_id"] = org_id
    if brand_id:
        context["brand_id"] = brand_id

    payload = {
        "task": task,
        "user_id": user_id,
        "context": context,
    }
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
        raise RuntimeError(f"O Tear API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"O Tear API indisponivel: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", help="nome canonico do agente")
    parser.add_argument("task", help="tarefa em portugues")
    parser.add_argument("--user-id", default=os.getenv("OTEAR_DEFAULT_USER_ID"))
    parser.add_argument("--org-id", default=os.getenv("OTEAR_DEFAULT_ORG_ID"))
    parser.add_argument("--brand-id", default=os.getenv("OTEAR_DEFAULT_BRAND_ID"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("OTEAR_TIMEOUT_S", "150")))
    args = parser.parse_args()

    started = time.time()
    try:
        result = _post_agent(
            api_url=_env("OTEAR_API_URL", "http://localhost:8000"),
            api_key=_env("OTEAR_API_KEY"),
            agent=args.agent,
            task=args.task,
            user_id=args.user_id,
            org_id=args.org_id,
            brand_id=args.brand_id,
            timeout_s=args.timeout,
        )
        duration_ms = int((time.time() - started) * 1000)
        print(json.dumps({
            "result": result.get("result", ""),
            "agent_name": result.get("agent_name", args.agent),
            "tools_used": result.get("tools_used", []),
            "duration_ms": result.get("duration_ms", duration_ms),
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
