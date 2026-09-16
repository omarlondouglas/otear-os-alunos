"""
Hermes Engine â€” wrapper do AIAgent (run_agent.AIAgent) embutido no FastAPI.

Cria 1 instancia de AIAgent por user_id (cache em memoria), reusa entre
mensagens da mesma sessao para preservar prompt caching e historico.

Importacao do hermes-agent eh LAZY (so quando chamar a primeira vez), para nao
quebrar o boot do FastAPI se o pacote nao estiver instalado em dev local.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Caches
_AGENTS: Dict[str, "AIAgentWrapper"] = {}
_LOCK = threading.Lock()

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "{OTEAR_VAULT_ROOT}"))
HERMES_HOME = Path(os.path.expanduser("~/.hermes"))


class HermesUnavailable(RuntimeError):
    """hermes-agent nao instalado ou nao inicializado."""


class AIAgentWrapper:
    """Encapsula o AIAgent e injeta o vault USER.md/MEMORY.md em cada turno."""

    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id or f"otear-{user_id}"
        self._agent = None  # criado lazy em ensure()

    def ensure(self):
        if self._agent is not None:
            return
        try:
            from run_agent import AIAgent
        except ImportError as e:
            raise HermesUnavailable(
                f"hermes-agent nao instalado: {e}. "
                "Rode `pip install hermes-agent` e `python scripts/init_hermes.py`."
            ) from e

        if not (HERMES_HOME / "config.yaml").exists():
            raise HermesUnavailable(
                f"~/.hermes nao inicializado. Rode `python scripts/init_hermes.py`."
            )

        # Modelo eh resolvido pelo Hermes via config.yaml automaticamente
        # quando model="" e nao passamos base_url/api_key.
        self._agent = AIAgent(
            session_id=self.session_id,
            user_id=self.user_id,
            user_name=self.user_id,
            chat_id=self.session_id,
            chat_type="otear",
            platform="otear",
            load_soul_identity=True,    # carrega ~/.hermes/SOUL.md
            skip_context_files=False,   # carrega USER.md/MEMORY.md de ~/.hermes/memories/
        )
        logger.info(f"[hermes_engine] AIAgent criado session={self.session_id}")

    def chat(self, user_message: str) -> Dict[str, Any]:
        """Processa 1 turno e retorna {response, tools_used, session_id}."""
        self.ensure()

        # Injeta o vault USER.md/MEMORY.md como prefixo ephemeral do system prompt.
        # Eh uma camada extra a documentos que o Hermes ja le de ~/.hermes/memories/,
        # garantindo que mudancas no vault Obsidian apareÃ§am imediatamente.
        ephemeral_prefix = self._build_vault_prefix()

        result = self._agent.run_conversation(
            user_message=user_message,
            system_message=ephemeral_prefix,  # Hermes faz append ao system prompt base
        )

        # AIAgent.run_conversation retorna dict com varias chaves; normalizamos:
        response_text = (
            result.get("final_response")
            or result.get("response")
            or ""
        )
        tools_used = []
        for msg in result.get("message_history", []) or []:
            if isinstance(msg, dict) and msg.get("role") == "tool":
                tools_used.append(msg.get("name", "unknown"))

        return {
            "response": response_text,
            "session_id": self.session_id,
            "tools_used": tools_used,
        }

    def _build_vault_prefix(self) -> str:
        """Le USER.md + MEMORY.md atualizados do vault e formata como context."""
        try:
            from app.services.user_memory import get_memory_prompt
            return f"## CONTEXTO DO VAULT (snapshot ao vivo)\n\n{get_memory_prompt()}"
        except Exception as e:
            logger.warning(f"[hermes_engine] vault prefix indisponivel: {e}")
            return ""


# â”€â”€â”€ API publica do modulo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def get_or_create_agent(user_id: str, session_id: Optional[str] = None) -> AIAgentWrapper:
    """Retorna agente cacheado por user_id (preserva historico cross-mensagens)."""
    key = f"{user_id}:{session_id or 'default'}"
    with _LOCK:
        wrapper = _AGENTS.get(key)
        if wrapper is None:
            wrapper = AIAgentWrapper(user_id=user_id, session_id=session_id)
            _AGENTS[key] = wrapper
        return wrapper


def chat(user_id: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    wrapper = get_or_create_agent(user_id, session_id)
    return wrapper.chat(message)


def reset_agent(user_id: str, session_id: Optional[str] = None) -> bool:
    key = f"{user_id}:{session_id or 'default'}"
    with _LOCK:
        return _AGENTS.pop(key, None) is not None


def is_available() -> Dict[str, Any]:
    """Health check rapido â€” diz se Hermes esta instalado e configurado."""
    try:
        import run_agent  # noqa: F401
        installed = True
    except ImportError:
        installed = False
    config_ok = (HERMES_HOME / "config.yaml").exists()
    soul_ok = (HERMES_HOME / "SOUL.md").exists()
    return {
        "installed": installed,
        "home": str(HERMES_HOME),
        "config_yaml": config_ok,
        "soul_md": soul_ok,
        "ready": installed and config_ok and soul_ok,
    }
