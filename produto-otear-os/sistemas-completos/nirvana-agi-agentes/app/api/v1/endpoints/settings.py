from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
import time

from app.core.security_admin import verify_admin_access

router = APIRouter()

SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")
CLAUDE_CREDENTIALS_PATH = os.getenv("CLAUDE_CREDENTIALS_PATH", os.path.expanduser("~/.claude/.credentials.json"))
# Backup em storage/ (provavelmente tem volume persistente no Docker)
_STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage")
CLAUDE_CREDENTIALS_BACKUP = os.path.join(_STORAGE_PATH, ".claude_credentials_backup.json")


class Settings(BaseModel):
    allowed_numbers: List[str] = Field(default_factory=list, max_length=50)
    webhook_url: Optional[str] = Field(None, max_length=500)


def load_settings() -> Settings:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return Settings(**data)
        except Exception:
            pass
    return Settings()


def save_settings(settings: Settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=4)


@router.get("", response_model=Settings)
async def get_settings(_: bool = Depends(verify_admin_access)):
    return load_settings()


@router.post("", response_model=Settings)
async def update_settings(
    settings: Settings,
    _: bool = Depends(verify_admin_access),
):
    try:
        save_settings(settings)
        return settings
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao salvar configurações")


@router.get("/llm-status")
async def get_llm_status(_: bool = Depends(verify_admin_access)):
    """Retorna qual LLM está ativo e o estado do sistema."""
    from app.core.model_factory import get_llm_status
    return get_llm_status()


def _mask_token(token: str) -> str:
    """Mascara um token, mostrando apenas os primeiros 15 caracteres."""
    if len(token) <= 15:
        return token
    return token[:15] + "****"


def _save_credentials_to_disk(creds: dict):
    """Salva credenciais no path do CLI E faz backup no storage."""
    # 1. Salvar no path do Claude CLI
    creds_dir = os.path.dirname(CLAUDE_CREDENTIALS_PATH)
    os.makedirs(creds_dir, exist_ok=True)
    with open(CLAUDE_CREDENTIALS_PATH, "w") as f:
        json.dump(creds, f, indent=2)

    # 2. Backup no storage (volume persistente)
    try:
        os.makedirs(os.path.dirname(CLAUDE_CREDENTIALS_BACKUP), exist_ok=True)
        with open(CLAUDE_CREDENTIALS_BACKUP, "w") as f:
            json.dump(creds, f, indent=2)
    except Exception:
        pass  # Backup falhou, não é crítico


def restore_credentials_from_backup():
    """Chamado no startup: restaura credenciais do backup se o arquivo principal não existir."""
    if os.path.exists(CLAUDE_CREDENTIALS_PATH):
        return  # Já existe, não precisa restaurar

    if not os.path.exists(CLAUDE_CREDENTIALS_BACKUP):
        return  # Sem backup disponível

    try:
        with open(CLAUDE_CREDENTIALS_BACKUP, "r") as f:
            creds = json.load(f)
        # Validação básica
        if "claudeAiOauth" in creds:
            creds_dir = os.path.dirname(CLAUDE_CREDENTIALS_PATH)
            os.makedirs(creds_dir, exist_ok=True)
            with open(CLAUDE_CREDENTIALS_PATH, "w") as f:
                json.dump(creds, f, indent=2)
            import logging
            logging.getLogger(__name__).info(
                f"Claude credentials restauradas do backup → {CLAUDE_CREDENTIALS_PATH}"
            )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Falha ao restaurar credenciais do backup: {e}")


class ClaudeCredentialsRequest(BaseModel):
    credentials: str


def _smoke_test_cli() -> dict:
    """Executa um teste rápido do CLI para verificar se as credenciais funcionam."""
    return {"success": False, "message": "Camada CLI desativada; use provider LLM por API key."}


async def _background_smoke_test():
    """Roda smoke test em background e atualiza model_factory se sucesso."""
    return _smoke_test_cli()


@router.post("/claude-credentials")
async def save_claude_credentials(
    request: ClaudeCredentialsRequest,
    _: bool = Depends(verify_admin_access),
):
    """Salva as credenciais OAuth do Claude CLI (~/.claude/.credentials.json).

    Salva imediatamente e roda o smoke test em background para evitar timeout
    do proxy EasyPanel (~30s). O status real pode ser verificado via /claude-configured.
    """
    try:
        creds = json.loads(request.credentials)
    except json.JSONDecodeError:
        raise HTTPException(400, "JSON inválido. Cole o conteúdo completo do arquivo .credentials.json")

    if "claudeAiOauth" not in creds:
        raise HTTPException(400, "JSON inválido: campo 'claudeAiOauth' não encontrado")

    oauth = creds["claudeAiOauth"]
    if "accessToken" not in oauth or "refreshToken" not in oauth:
        raise HTTPException(400, "JSON inválido: accessToken ou refreshToken ausente")

    # Salvar no CLI path + backup
    _save_credentials_to_disk(creds)

    expires_at = oauth.get("expiresAt", 0)
    subscription = oauth.get("subscriptionType", "unknown")

    # Smoke test em background — não bloqueia a resposta (evita 502 no EasyPanel)
    import asyncio
    asyncio.create_task(_background_smoke_test())

    return {
        "status": "saved",
        "subscription": subscription,
        "expires_at": expires_at,
        "path": CLAUDE_CREDENTIALS_PATH,
        "cli_test": {"success": None, "message": "Teste em andamento em background"},
    }


def _check_claude_credentials() -> dict:
    """Verifica se as credenciais OAuth do Claude CLI estão configuradas (lógica compartilhada).

    IMPORTANTE: expiresAt refere-se ao accessToken, que expira em poucas horas.
    Mas o Claude CLI auto-renova usando o refreshToken. Então se temos refreshToken,
    consideramos como "configured=True" e "authenticated=True" (o CLI faz o refresh).
    """
    if not os.path.exists(CLAUDE_CREDENTIALS_PATH):
        return {"configured": False, "authenticated": False, "reason": "Arquivo de credenciais não encontrado"}

    try:
        with open(CLAUDE_CREDENTIALS_PATH, "r") as f:
            creds = json.load(f)
    except Exception:
        return {"configured": False, "authenticated": False, "reason": "Erro ao ler arquivo de credenciais"}

    oauth = creds.get("claudeAiOauth")
    if not oauth:
        return {"configured": False, "authenticated": False, "reason": "Campo claudeAiOauth ausente"}

    has_refresh_token = bool(oauth.get("refreshToken"))
    has_access_token = bool(oauth.get("accessToken"))
    expires_at = oauth.get("expiresAt", 0)
    now_ms = int(time.time() * 1000)
    access_token_expired = expires_at > 0 and expires_at < now_ms

    # Se tem refreshToken, o CLI consegue renovar sozinho → considerar autenticado
    is_usable = has_refresh_token or (has_access_token and not access_token_expired)

    return {
        "configured": True,
        "authenticated": is_usable,
        "expired": access_token_expired,
        "has_refresh_token": has_refresh_token,
        "subscription": oauth.get("subscriptionType", "unknown"),
        "rate_limit_tier": oauth.get("rateLimitTier", "unknown"),
        "expires_at": expires_at,
        "scopes": oauth.get("scopes", []),
        "access_token_preview": _mask_token(oauth.get("accessToken", "")),
    }


@router.get("/claude-configured")
async def check_claude_configured():
    """Endpoint legado: retorna se ha um provider LLM por API configurado."""
    try:
        from app.core.model_factory import get_llm_status
        llm_status = get_llm_status()
        provider = llm_status.get("active_provider")
        if provider and provider != "none":
            return {"configured": True, "authenticated": True, "provider": provider}
    except Exception:
        pass
    return {"configured": False, "authenticated": False, "provider": "none"}


@router.get("/claude-auth-status")
async def get_claude_auth_status(_: bool = Depends(verify_admin_access)):
    """Endpoint protegido: retorna status completo com tokens mascarados."""
    return _check_claude_credentials()


@router.delete("/claude-credentials")
async def reset_claude_credentials(_: bool = Depends(verify_admin_access)):
    """Remove credenciais do Claude CLI para forçar re-setup."""
    removed = []
    for path in [CLAUDE_CREDENTIALS_PATH, CLAUDE_CREDENTIALS_BACKUP]:
        if os.path.exists(path):
            try:
                os.remove(path)
                removed.append(path)
            except Exception as e:
                raise HTTPException(500, f"Erro ao remover {path}: {e}")

    return {"status": "removed", "files_removed": removed}
