"""
Refresh automatico do /root/.claude/.credentials.json.

Problema: em containers managed (EasyPanel), as env vars CLAUDE_OAUTH_* sao
imutaveis. O entrypoint cria o arquivo a partir delas, e quando o token
expira, o Claude CLI tenta refresh interno mas o arquivo eh sobrescrito no
proximo restart. Resultado: a cada deploy/restart o token volta pro valor
expirado da env var.

Solucao: o arquivo vive num volume persistente, e este servico faz refresh
proativo (Celery beat a cada 30min). Se token < 1h pra expirar, troca por
um novo via refresh_token. O arquivo persiste entre restarts.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = Path(os.getenv("CLAUDE_CREDENTIALS_PATH", "/root/.claude/.credentials.json"))
BACKUP_PATH = Path("/app/storage/.claude_credentials_backup.json")

# Reusa OAuth client_id e endpoint do anthropic_oauth.py
CLAUDE_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
CLAUDE_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"

# Janela de seguranca pra refresh: se faltar < 1h pro expiry, refresh agora
REFRESH_WINDOW_MS = 60 * 60 * 1000  # 1h em ms


def _load_credentials() -> Optional[Dict[str, Any]]:
    if not CREDENTIALS_PATH.exists():
        return None
    try:
        return json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[claude-refresh] credentials.json invalido: {e}")
        return None


def _save_credentials(data: Dict[str, Any]) -> None:
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Backup pro storage volume — sobrevive mesmo se /root/.claude resetar
    try:
        BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
        BACKUP_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning(f"[claude-refresh] backup falhou: {e}")


def _expires_at_ms(creds: Dict[str, Any]) -> int:
    """Le expiresAt do schema do Claude CLI (em milissegundos)."""
    oauth = creds.get("claudeAiOauth") or {}
    return int(oauth.get("expiresAt", 0) or 0)


def _needs_refresh(creds: Dict[str, Any]) -> bool:
    expires_at = _expires_at_ms(creds)
    if not expires_at:
        return True
    now_ms = int(time.time() * 1000)
    return now_ms >= (expires_at - REFRESH_WINDOW_MS)


def _do_refresh(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Chama OAuth endpoint pra trocar refresh_token por novo access_token."""
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLAUDE_CLIENT_ID,
    }
    try:
        r = httpx.post(
            CLAUDE_TOKEN_URL,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30,
        )
        if r.status_code != 200:
            logger.error(f"[claude-refresh] HTTP {r.status_code}: {r.text[:300]}")
            return None
        return r.json()
    except Exception as e:
        logger.error(f"[claude-refresh] falhou: {e}")
        return None


def refresh_claude_credentials(force: bool = False) -> Dict[str, Any]:
    """
    Faz refresh se o token estiver perto de expirar (ou force=True).

    Retorna:
        {"status": "refreshed"|"valid"|"missing"|"failed", "expires_at_iso": "..."}
    """
    creds = _load_credentials()
    if not creds:
        # Tenta restaurar do backup
        if BACKUP_PATH.exists():
            try:
                creds = json.loads(BACKUP_PATH.read_text(encoding="utf-8"))
                _save_credentials(creds)
                logger.info("[claude-refresh] restaurado do backup")
            except Exception:
                pass

    if not creds:
        return {"status": "missing", "message": "credentials.json nao encontrado"}

    oauth = creds.get("claudeAiOauth") or {}
    refresh_tok = oauth.get("refreshToken")
    if not refresh_tok:
        return {"status": "missing", "message": "refresh_token ausente"}

    if not force and not _needs_refresh(creds):
        expires_at = _expires_at_ms(creds)
        return {
            "status": "valid",
            "expires_at_ms": expires_at,
            "expires_in_minutes": max(0, (expires_at - int(time.time() * 1000)) // 60_000),
        }

    new = _do_refresh(refresh_tok)
    if not new or not new.get("access_token"):
        return {"status": "failed", "message": "endpoint Anthropic nao devolveu access_token"}

    # Schema do Claude CLI usa expiresAt em ms desde epoch
    expires_in_s = int(new.get("expires_in", 28800))  # default 8h
    new_expires_at_ms = int(time.time() * 1000) + (expires_in_s * 1000)

    oauth["accessToken"] = new["access_token"]
    if new.get("refresh_token"):
        oauth["refreshToken"] = new["refresh_token"]
    oauth["expiresAt"] = new_expires_at_ms
    creds["claudeAiOauth"] = oauth
    _save_credentials(creds)

    logger.info(f"[claude-refresh] token renovado, expira em {expires_in_s}s")
    return {
        "status": "refreshed",
        "expires_at_ms": new_expires_at_ms,
        "expires_in_minutes": expires_in_s // 60,
    }


def status() -> Dict[str, Any]:
    """Retorna estado das credenciais sem mexer nelas."""
    creds = _load_credentials()
    if not creds:
        return {"present": False}
    expires_at = _expires_at_ms(creds)
    now_ms = int(time.time() * 1000)
    minutes = (expires_at - now_ms) // 60_000 if expires_at else 0
    return {
        "present": True,
        "has_refresh_token": bool((creds.get("claudeAiOauth") or {}).get("refreshToken")),
        "expires_at_ms": expires_at,
        "expires_in_minutes": minutes,
        "expired": minutes <= 0,
        "needs_refresh_soon": _needs_refresh(creds),
    }
