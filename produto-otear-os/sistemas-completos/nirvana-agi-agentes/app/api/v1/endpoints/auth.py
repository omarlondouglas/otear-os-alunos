from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.security_admin import verify_admin_access
from app.core.supabase import get_supabase
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class InviteRequest(BaseModel):
    email: str


class InviteResponse(BaseModel):
    message: str
    email: str


@router.post("/invite", response_model=InviteResponse)
async def invite_user(
    body: InviteRequest,
    _: bool = Depends(verify_admin_access),
):
    """Admin convida um novo usuário por email (Supabase envia o link de acesso)."""
    client = get_supabase()
    try:
        client.auth.admin.invite_user_by_email(body.email)
        logger.info(f"Convite enviado para {body.email}")
        return InviteResponse(
            message="Convite enviado com sucesso",
            email=body.email,
        )
    except Exception as e:
        logger.error(f"Erro ao convidar {body.email}: {e}")
        raise HTTPException(status_code=400, detail=f"Erro ao enviar convite: {str(e)}")


@router.get("/users")
async def list_users(_: bool = Depends(verify_admin_access)):
    """Admin lista todos os usuários cadastrados."""
    client = get_supabase()
    try:
        result = client.auth.admin.list_users()
        users = [
            {
                "id": u.id,
                "email": u.email,
                "created_at": str(u.created_at),
                "last_sign_in": str(u.last_sign_in_at) if u.last_sign_in_at else None,
            }
            for u in result
        ]
        return {"users": users, "total": len(users)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, _: bool = Depends(verify_admin_access)):
    """Admin remove um usuário pelo ID."""
    client = get_supabase()
    try:
        client.auth.admin.delete_user(user_id)
        logger.info(f"Usuário {user_id} removido")
        return {"message": "Usuário removido com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao remover usuário: {str(e)}")
