"""
Admin endpoints — operacoes que precisam de privilegio elevado.

Auth via Bearer token (Supabase) OU x-admin-password (legacy).
"""
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core.security_admin import verify_admin_access

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/vault/refresh")
async def refresh_vault(_: Any = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Faz `git pull` no vault Obsidian sem restart do container.

    Util quando voce editou USER.md/MEMORY.md ou adicionou criadores em
    references/ via Obsidian local e quer refletir imediatamente no Hermes
    sem precisar reiniciar o app.

    Tambem invalida o cache do user_memory para forcar re-leitura dos arquivos
    no proximo turno do agente.
    """
    vault_path = os.getenv("VAULT_PATH", "/app/vault")
    vault_dir = Path(vault_path)

    if not (vault_dir / ".git").exists():
        raise HTTPException(
            status_code=400,
            detail=f"Vault em {vault_path} nao eh um repo git (sem .git/). "
                   "Configure VAULT_REPO_URL e reinicie pra clonar.",
        )

    try:
        result = subprocess.run(
            ["git", "-C", str(vault_dir), "pull", "--ff-only"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="git pull timeout (60s)")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="git binary nao encontrado no container")

    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        logger.warning(f"vault refresh falhou: {output[:300]}")
        raise HTTPException(status_code=500, detail=f"git pull falhou: {output[:300]}")

    # Invalida cache do user_memory pra forcar re-leitura
    try:
        from app.services import user_memory
        user_memory._cache.clear()
    except Exception as e:
        logger.warning(f"falha ao limpar cache user_memory: {e}")

    # Reseta tambem os agentes Hermes em memoria pra recarregar contexto novo
    cleared_agents = 0
    try:
        from app.services import hermes_engine
        with hermes_engine._LOCK:
            cleared_agents = len(hermes_engine._AGENTS)
            hermes_engine._AGENTS.clear()
    except Exception as e:
        logger.warning(f"falha ao limpar cache hermes_engine: {e}")

    return {
        "status": "ok",
        "vault_path": vault_path,
        "git_output": output.strip().splitlines()[-3:],  # ultimas 3 linhas
        "user_memory_cache_cleared": True,
        "hermes_agents_reset": cleared_agents,
    }


@router.get("/vault/status")
async def vault_status(_: Any = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Status do vault: caminho, ultimo commit, mudancas pendentes."""
    vault_path = os.getenv("VAULT_PATH", "/app/vault")
    vault_dir = Path(vault_path)
    out: Dict[str, Any] = {"vault_path": vault_path, "exists": vault_dir.exists()}

    if not (vault_dir / ".git").exists():
        out["is_git_repo"] = False
        return out

    out["is_git_repo"] = True

    try:
        # Ultimo commit
        r = subprocess.run(
            ["git", "-C", str(vault_dir), "log", "-1", "--format=%H|%cI|%s"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split("|", 2)
            out["last_commit"] = {
                "sha": parts[0][:8] if len(parts) > 0 else None,
                "date": parts[1] if len(parts) > 1 else None,
                "message": parts[2] if len(parts) > 2 else None,
            }

        # Status (mudancas pendentes)
        r = subprocess.run(
            ["git", "-C", str(vault_dir), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        out["dirty_files"] = len(r.stdout.strip().splitlines()) if r.returncode == 0 else None

        # Branch + tracking
        r = subprocess.run(
            ["git", "-C", str(vault_dir), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        out["branch"] = r.stdout.strip() if r.returncode == 0 else None

        # Behind/ahead
        r = subprocess.run(
            ["git", "-C", str(vault_dir), "rev-list", "--left-right", "--count", "HEAD...@{u}"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            counts = r.stdout.strip().split()
            if len(counts) == 2:
                out["ahead"] = int(counts[0])
                out["behind"] = int(counts[1])
    except Exception as e:
        logger.warning(f"vault status check falhou: {e}")
        out["error"] = str(e)

    # Memory snapshot
    try:
        from app.services.user_memory import vault_status as memory_status
        out["memory"] = memory_status()
    except Exception:
        pass

    return out


@router.get("/claude/credentials/status")
async def claude_credentials_status(_: Any = Depends(verify_admin_access)) -> Dict[str, Any]:
    """Mostra estado das credenciais Claude OAuth (sem expor o token)."""
    from app.services.claude_credentials_refresher import status
    return status()


@router.post("/claude/credentials/refresh")
async def claude_credentials_refresh(
    force: bool = False,
    _: Any = Depends(verify_admin_access),
) -> Dict[str, Any]:
    """Forca refresh do token. force=true troca mesmo se ainda nao expirou."""
    from app.services.claude_credentials_refresher import refresh_claude_credentials
    return refresh_claude_credentials(force=force)
