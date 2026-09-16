"""
Modelo de Organização (multi-tenancy para agências).
Armazenado no Supabase — sem ORM SQLAlchemy.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from app.core.supabase import get_supabase
import logging

logger = logging.getLogger(__name__)


@dataclass
class Organization:
    id: str
    name: str
    slug: str
    owner_id: str
    logo_url: Optional[str] = None
    plan: str = "starter"  # starter, pro, agency, enterprise
    max_brands: int = 1
    max_members: int = 1
    created_at: Optional[str] = None


@dataclass
class OrgMember:
    id: str
    org_id: str
    user_id: str
    role: str = "editor"  # owner, admin, editor, viewer
    created_at: Optional[str] = None


# ---------------------------------------------------------------------------
# Plan limits
# ---------------------------------------------------------------------------
PLAN_LIMITS = {
    "starter":    {"max_brands": 1,  "max_members": 1,  "monthly_credits": 50},
    "pro":        {"max_brands": 5,  "max_members": 3,  "monthly_credits": 200},
    "agency":     {"max_brands": 20, "max_members": 10, "monthly_credits": -1},   # -1 = ilimitado
    "enterprise": {"max_brands": -1, "max_members": -1, "monthly_credits": -1},
}


def _row_to_org(row: dict) -> Organization:
    return Organization(**{k: v for k, v in row.items() if k in Organization.__dataclass_fields__})


def _row_to_member(row: dict) -> OrgMember:
    return OrgMember(**{k: v for k, v in row.items() if k in OrgMember.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Organization CRUD
# ---------------------------------------------------------------------------

def create_organization(owner_id: str, name: str, slug: str, plan: str = "starter") -> Organization:
    """Cria uma nova organização e adiciona o owner como membro."""
    client = get_supabase()
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])

    result = client.table("organizations").insert({
        "owner_id": owner_id,
        "name": name,
        "slug": slug,
        "plan": plan,
        "max_brands": limits["max_brands"],
        "max_members": limits["max_members"],
    }).execute()

    org = _row_to_org(result.data[0])

    # Adiciona owner como membro com role "owner"
    client.table("org_members").insert({
        "org_id": org.id,
        "user_id": owner_id,
        "role": "owner",
    }).execute()

    return org


def get_organization(org_id: str) -> Optional[Organization]:
    """Busca organização por ID."""
    try:
        client = get_supabase()
        result = client.table("organizations").select("*").eq("id", org_id).single().execute()
        return _row_to_org(result.data) if result.data else None
    except Exception as e:
        logger.warning(f"Org não encontrada: {org_id}: {e}")
        return None


def get_organization_by_slug(slug: str) -> Optional[Organization]:
    """Busca organização pelo slug (subdomínio)."""
    try:
        client = get_supabase()
        result = client.table("organizations").select("*").eq("slug", slug).single().execute()
        return _row_to_org(result.data) if result.data else None
    except Exception:
        return None


def get_user_organizations(user_id: str) -> List[Organization]:
    """Lista todas as orgs que um usuário é membro."""
    try:
        client = get_supabase()
        memberships = client.table("org_members").select("org_id").eq("user_id", user_id).execute()
        if not memberships.data:
            return []
        org_ids = [m["org_id"] for m in memberships.data]
        result = client.table("organizations").select("*").in_("id", org_ids).execute()
        return [_row_to_org(r) for r in (result.data or [])]
    except Exception as e:
        logger.warning(f"Erro ao listar orgs de user={user_id}: {e}")
        return []


def update_organization(org_id: str, data: dict) -> Optional[Organization]:
    """Atualiza campos da organização."""
    client = get_supabase()
    allowed = {"name", "logo_url", "plan", "max_brands", "max_members"}
    payload = {k: v for k, v in data.items() if k in allowed}
    if not payload:
        return get_organization(org_id)
    result = client.table("organizations").update(payload).eq("id", org_id).execute()
    return _row_to_org(result.data[0]) if result.data else None


# ---------------------------------------------------------------------------
# Member management
# ---------------------------------------------------------------------------

def get_org_members(org_id: str) -> List[OrgMember]:
    """Lista membros de uma organização."""
    try:
        client = get_supabase()
        result = client.table("org_members").select("*").eq("org_id", org_id).execute()
        return [_row_to_member(r) for r in (result.data or [])]
    except Exception as e:
        logger.warning(f"Erro ao listar membros de org={org_id}: {e}")
        return []


def get_user_membership(org_id: str, user_id: str) -> Optional[OrgMember]:
    """Verifica se um user é membro da org e retorna o membership."""
    try:
        client = get_supabase()
        result = (
            client.table("org_members")
            .select("*")
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return _row_to_member(result.data) if result.data else None
    except Exception:
        return None


def add_org_member(org_id: str, user_id: str, role: str = "editor") -> OrgMember:
    """Adiciona membro à organização."""
    client = get_supabase()
    result = client.table("org_members").insert({
        "org_id": org_id,
        "user_id": user_id,
        "role": role,
    }).execute()
    return _row_to_member(result.data[0])


def update_member_role(org_id: str, user_id: str, role: str) -> Optional[OrgMember]:
    """Atualiza role de um membro."""
    client = get_supabase()
    result = (
        client.table("org_members")
        .update({"role": role})
        .eq("org_id", org_id)
        .eq("user_id", user_id)
        .execute()
    )
    return _row_to_member(result.data[0]) if result.data else None


def remove_org_member(org_id: str, user_id: str) -> bool:
    """Remove membro da organização."""
    client = get_supabase()
    result = (
        client.table("org_members")
        .delete()
        .eq("org_id", org_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(result.data)
