"""
Credential Monitor — monitora e mantém credenciais do Claude CLI saudáveis.

Roda como tarefa asyncio em background:
- Verifica expiração do accessToken a cada 5 minutos
- Força refresh proativo quando token expira em < 30 min
- Sincroniza credenciais para backup após refresh
- Expõe status para health check
"""
import asyncio
import json
import logging
import os
import shutil
import subprocess
import time
from typing import Dict, Optional
from app.core.claude_cli_env import build_claude_cli_env

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = os.getenv(
    "CLAUDE_CREDENTIALS_PATH",
    os.path.expanduser("~/.claude/.credentials.json"),
)
_STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage")
CREDENTIALS_BACKUP = os.path.join(_STORAGE_PATH, ".claude_credentials_backup.json")

# Intervalo de verificação em segundos
CHECK_INTERVAL = 300  # 5 minutos
# Threshold para refresh proativo (em milissegundos)
REFRESH_THRESHOLD_MS = 30 * 60 * 1000  # 30 minutos

# Status global acessível pelo health check
_cli_status: Dict = {
    "authenticated": False,
    "expires_in_minutes": None,
    "last_check": None,
    "last_refresh": None,
    "error": None,
}


def get_cli_status() -> Dict:
    """Retorna o status atual do CLI para o health check."""
    return _cli_status.copy()


def _read_credentials() -> Optional[Dict]:
    """Lê e valida o arquivo de credenciais."""
    if not os.path.isfile(CREDENTIALS_PATH):
        return None
    try:
        with open(CREDENTIALS_PATH, "r") as f:
            creds = json.load(f)
        if "claudeAiOauth" not in creds:
            return None
        return creds
    except (json.JSONDecodeError, IOError):
        return None


def _check_expiry(creds: Dict) -> Dict:
    """Verifica o status de expiração do token."""
    oauth = creds.get("claudeAiOauth", {})
    expires_at = oauth.get("expiresAt", 0)
    has_refresh = bool(oauth.get("refreshToken"))
    now_ms = int(time.time() * 1000)

    if expires_at > 0:
        remaining_ms = expires_at - now_ms
        expires_in_minutes = max(0, remaining_ms // 60000)
        is_expired = remaining_ms <= 0
        needs_refresh = remaining_ms < REFRESH_THRESHOLD_MS
    else:
        expires_in_minutes = None
        is_expired = False
        needs_refresh = False

    return {
        "expires_in_minutes": expires_in_minutes,
        "is_expired": is_expired,
        "needs_refresh": needs_refresh,
        "has_refresh_token": has_refresh,
        "subscription": oauth.get("subscriptionType", "unknown"),
    }


def _force_refresh() -> bool:
    """Força refresh do token executando um comando simples no CLI."""
    try:
        env = build_claude_cli_env()

        result = subprocess.run(
            ["claude", "-p", "respond only with OK", "--output-format", "json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
            env=env,
        )

        if result.returncode == 0:
            # Sincronizar credenciais refreshadas para backup
            try:
                backup_dir = os.path.dirname(CREDENTIALS_BACKUP)
                os.makedirs(backup_dir, exist_ok=True)
                shutil.copy2(CREDENTIALS_PATH, CREDENTIALS_BACKUP)
            except Exception:
                pass
            return True

        logger.warning(
            f"CredentialMonitor: refresh falhou (code {result.returncode}): "
            f"{result.stderr[:200] if result.stderr else 'sem stderr'}"
        )
        return False

    except subprocess.TimeoutExpired:
        logger.warning("CredentialMonitor: refresh timeout (45s)")
        return False
    except Exception as e:
        logger.warning(f"CredentialMonitor: erro no refresh: {e}")
        return False


async def _monitor_loop():
    """Loop principal de monitoramento."""
    global _cli_status

    logger.info("CredentialMonitor: iniciando monitoramento (intervalo: %ds)", CHECK_INTERVAL)

    first_run = True

    while True:
        try:
            creds = _read_credentials()

            if creds is None:
                _cli_status = {
                    "authenticated": False,
                    "expires_in_minutes": None,
                    "last_check": time.time(),
                    "last_refresh": _cli_status.get("last_refresh"),
                    "error": "Credenciais não encontradas",
                }
                logger.debug("CredentialMonitor: sem credenciais")
                await asyncio.sleep(CHECK_INTERVAL)
                first_run = False
                continue

            expiry = _check_expiry(creds)

            # Na primeira iteração: SEMPRE fazer smoke test real para validar
            # que as credenciais no disco realmente funcionam com o CLI
            if first_run:
                logger.info("CredentialMonitor: primeiro check — executando smoke test real...")
                loop = asyncio.get_event_loop()
                smoke_ok = await loop.run_in_executor(None, _force_refresh)
                if smoke_ok:
                    logger.info("CredentialMonitor: smoke test inicial OK!")
                    _cli_status = {
                        "authenticated": True,
                        "expires_in_minutes": expiry["expires_in_minutes"],
                        "subscription": expiry["subscription"],
                        "last_check": time.time(),
                        "last_refresh": time.time(),
                        "error": None,
                    }
                else:
                    logger.warning("CredentialMonitor: smoke test inicial FALHOU — credenciais inválidas")
                    _cli_status = {
                        "authenticated": False,
                        "expires_in_minutes": expiry["expires_in_minutes"],
                        "subscription": expiry["subscription"],
                        "last_check": time.time(),
                        "last_refresh": _cli_status.get("last_refresh"),
                        "error": "CLI smoke test falhou — credenciais podem estar inválidas",
                    }
                first_run = False
                await asyncio.sleep(CHECK_INTERVAL)
                continue

            # Refresh proativo se necessário
            if expiry["needs_refresh"] and expiry["has_refresh_token"]:
                logger.info(
                    "CredentialMonitor: token expira em %s min — forçando refresh...",
                    expiry["expires_in_minutes"],
                )
                # Executar refresh em thread separada para não bloquear o event loop
                loop = asyncio.get_event_loop()
                refreshed = await loop.run_in_executor(None, _force_refresh)

                if refreshed:
                    logger.info("CredentialMonitor: refresh bem-sucedido!")
                    _cli_status["last_refresh"] = time.time()
                    # Re-ler credenciais atualizadas
                    creds = _read_credentials()
                    if creds:
                        expiry = _check_expiry(creds)
                else:
                    logger.warning("CredentialMonitor: refresh falhou")

            # Atualizar status
            _cli_status = {
                "authenticated": expiry["has_refresh_token"] or not expiry["is_expired"],
                "expires_in_minutes": expiry["expires_in_minutes"],
                "subscription": expiry["subscription"],
                "last_check": time.time(),
                "last_refresh": _cli_status.get("last_refresh"),
                "error": None,
            }

            if expiry["expires_in_minutes"] is not None:
                logger.debug(
                    "CredentialMonitor: token expira em %d min | autenticado: %s",
                    expiry["expires_in_minutes"],
                    _cli_status["authenticated"],
                )

        except Exception as e:
            logger.error(f"CredentialMonitor: erro no loop: {e}")
            _cli_status["error"] = str(e)
            first_run = False

        await asyncio.sleep(CHECK_INTERVAL)


async def start_monitor():
    """Inicia o monitor de credenciais como tarefa de background.

    Seta last_check imediatamente para que o endpoint /claude-configured
    saiba que o monitor está ativo (evita retornar dados stale do arquivo).
    """
    global _cli_status
    _cli_status["last_check"] = time.time()
    _cli_status["error"] = "Verificação inicial em andamento..."
    await _monitor_loop()
