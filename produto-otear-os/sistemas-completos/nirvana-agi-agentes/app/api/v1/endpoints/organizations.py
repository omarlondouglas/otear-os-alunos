"""
Endpoints de Organizações — multi-tenancy para agências.
"""
import re
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from app.core.security import verify_supabase_token
from app.models.organization import (
    create_organization, get_organization, get_user_organizations,
    update_organization, get_org_members, get_user_membership,
    add_org_member, update_member_role, remove_org_member,
    PLAN_LIMITS,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class OrgCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


class OrgUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None


class MemberAdd(BaseModel):
    email: str
    role: str = Field("editor", pattern=r"^(admin|editor|viewer)$")


class MemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern=r"^(admin|editor|viewer)$")


# ---------------------------------------------------------------------------
# Organization CRUD
# ---------------------------------------------------------------------------

@router.get("")
async def list_my_organizations(user_data: dict = Depends(verify_supabase_token)):
    """Lista as organizações do usuário autenticado."""
    orgs = get_user_organizations(user_data["user_id"])
    return {
        "organizations": [
            {
                "id": o.id,
                "name": o.name,
                "slug": o.slug,
                "plan": o.plan,
                "logo_url": o.logo_url,
                "max_brands": o.max_brands,
                "max_members": o.max_members,
            }
            for o in orgs
        ]
    }


@router.post("", status_code=201)
async def create_org(body: OrgCreate, user_data: dict = Depends(verify_supabase_token)):
    """Cria uma nova organização. O criador vira owner."""
    from app.models.organization import get_organization_by_slug
    if get_organization_by_slug(body.slug):
        raise HTTPException(status_code=409, detail="Slug já em uso")

    org = create_organization(
        owner_id=user_data["user_id"],
        name=body.name,
        slug=body.slug,
    )
    return {"message": "Organização criada", "organization": {"id": org.id, "name": org.name, "slug": org.slug}}


@router.get("/{org_id}")
async def get_org(org_id: str, user_data: dict = Depends(verify_supabase_token)):
    """Retorna detalhes da organização (apenas para membros)."""
    _require_member(org_id, user_data["user_id"])
    org = get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    limits = PLAN_LIMITS.get(org.plan, PLAN_LIMITS["starter"])
    return {
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "plan": org.plan,
        "logo_url": org.logo_url,
        "max_brands": org.max_brands,
        "max_members": org.max_members,
        "monthly_credits": limits["monthly_credits"],
    }


@router.put("/{org_id}")
async def update_org(org_id: str, body: OrgUpdate, user_data: dict = Depends(verify_supabase_token)):
    """Atualiza organização (admin/owner)."""
    _require_admin(org_id, user_data["user_id"])
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    org = update_organization(org_id, data)
    return {"message": "Organização atualizada", "organization": {"id": org.id, "name": org.name}}


# ---------------------------------------------------------------------------
# Members management
# ---------------------------------------------------------------------------

@router.get("/{org_id}/members")
async def list_members(org_id: str, user_data: dict = Depends(verify_supabase_token)):
    """Lista membros da organização."""
    _require_member(org_id, user_data["user_id"])
    members = get_org_members(org_id)

    # Enriquece com email do Supabase
    from app.core.supabase import get_supabase
    client = get_supabase()
    result = []
    for m in members:
        email = None
        try:
            user = client.auth.admin.get_user_by_id(m.user_id)
            email = user.user.email if user and user.user else None
        except Exception:
            pass
        result.append({
            "user_id": m.user_id,
            "role": m.role,
            "email": email,
            "created_at": m.created_at,
        })
    return {"members": result}


@router.post("/{org_id}/members", status_code=201)
async def invite_member(org_id: str, body: MemberAdd, user_data: dict = Depends(verify_supabase_token)):
    """Convida novo membro (admin/owner). Cria invite via Supabase se user não existe."""
    _require_admin(org_id, user_data["user_id"])

    # Verifica limite de membros
    org = get_organization(org_id)
    members = get_org_members(org_id)
    if org.max_members != -1 and len(members) >= org.max_members:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {org.max_members} membros atingido. Faça upgrade do plano.",
        )

    # Busca user por email no Supabase
    from app.core.supabase import get_supabase
    client = get_supabase()
    target_user_id = None
    try:
        users = client.auth.admin.list_users()
        for u in users:
            if u.email == body.email:
                target_user_id = str(u.id)
                break
    except Exception as e:
        logger.warning(f"Erro ao buscar user por email: {e}")

    if not target_user_id:
        # Convida via Supabase
        try:
            client.auth.admin.invite_user_by_email(body.email)
        except Exception as e:
            logger.warning(f"Erro ao convidar {body.email}: {e}")
        raise HTTPException(
            status_code=202,
            detail=f"Convite enviado para {body.email}. O membro será adicionado após aceitar.",
        )

    # Verifica se já é membro
    existing = get_user_membership(org_id, target_user_id)
    if existing:
        raise HTTPException(status_code=409, detail="Usuário já é membro desta organização")

    member = add_org_member(org_id, target_user_id, body.role)
    return {"message": "Membro adicionado", "member": {"user_id": member.user_id, "role": member.role}}


@router.put("/{org_id}/members/{member_user_id}")
async def change_member_role(
    org_id: str, member_user_id: str, body: MemberRoleUpdate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Altera role de um membro (admin/owner)."""
    _require_admin(org_id, user_data["user_id"])
    member = update_member_role(org_id, member_user_id, body.role)
    if not member:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"message": "Role atualizado", "member": {"user_id": member.user_id, "role": member.role}}


@router.delete("/{org_id}/members/{member_user_id}")
async def remove_member(
    org_id: str, member_user_id: str,
    user_data: dict = Depends(verify_supabase_token),
):
    """Remove membro da organização (admin/owner). Não pode remover o owner."""
    _require_admin(org_id, user_data["user_id"])

    target = get_user_membership(org_id, member_user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    if target.role == "owner":
        raise HTTPException(status_code=403, detail="Não é possível remover o owner da organização")

    remove_org_member(org_id, member_user_id)
    return {"message": "Membro removido"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_member(org_id: str, user_id: str) -> None:
    """Verifica se user é membro da org. Levanta 403 se não."""
    membership = get_user_membership(org_id, user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Você não é membro desta organização")


def _require_admin(org_id: str, user_id: str) -> None:
    """Verifica se user é admin/owner da org. Levanta 403 se não."""
    membership = get_user_membership(org_id, user_id)
    if not membership or membership.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Permissão insuficiente. Requer admin ou owner.")
