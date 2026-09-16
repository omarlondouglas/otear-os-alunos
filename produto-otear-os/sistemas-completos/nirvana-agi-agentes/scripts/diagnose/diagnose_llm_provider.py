from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.core.model_factory import get_llm_status, get_model


def mask(value: str | None) -> str:
    if not value:
        return "empty"
    value = str(value)
    if len(value) <= 8:
        return "set"
    return f"{value[:4]}...{value[-4:]}"


if __name__ == "__main__":
    print("Environment:")
    for name in ("MODEL_PROVIDER", "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
        print(f"  {name}={mask(os.getenv(name))}")

    print("\nStatus:")
    print(get_llm_status())

    print("\nModel factory:")
    try:
        model = get_model("writer")
        print(f"  ok: {type(model).__module__}.{type(model).__name__} id={getattr(model, 'id', None)}")
    except Exception as exc:
        print(f"  error: {type(exc).__name__}: {exc}")
