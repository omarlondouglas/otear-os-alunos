"""
Endpoints de Marcas/Clientes — cada organização gerencia N marcas.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from app.core.security import verify_supabase_token
from app.models.brand import create_brand, get_brand, list_brands, update_brand, delete_brand
from app.models.organization import get_organization, get_user_membership

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BrandCreate(BaseModel):
    org_id: str
    name: str = Field(..., min_length=1, max_length=100)
    nicho: Optional[str] = None
    empresa: Optional[str] = None
    valores_texto: Optional[str] = None
    publico_texto: Optional[str] = None
    historia_texto: Optional[str] = None
    tom_de_voz: Optional[str] = None
    logo_url: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    instagram_handle: Optional[str] = None
    website: Optional[str] = None


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    nicho: Optional[str] = None
    empresa: Optional[str] = None
    valores_texto: Optional[str] = None
    publico_texto: Optional[str] = None
    historia_texto: Optional[str] = None
    tom_de_voz: Optional[str] = None
    logo_url: Optional[str] = None
    color_primary: Optional[str] = None
    color_secondary: Optional[str] = None
    instagram_handle: Optional[str] = None
    website: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("")
async def list_org_brands(
    org_id: str = Query(..., description="ID da organização"),
    user_data: dict = Depends(verify_supabase_token),
):
    """Lista marcas da organização."""
    _require_org_member(org_id, user_data["user_id"])
    brands = list_brands(org_id)
    return {
        "brands": [
            {
                "id": b.id,
                "name": b.name,
                "nicho": b.nicho,
                "empresa": b.empresa,
                "tom_de_voz": b.tom_de_voz,
                "logo_url": b.logo_url,
                "instagram_handle": b.instagram_handle,
                "active": b.active,
            }
            for b in brands
        ]
    }


@router.post("", status_code=201)
async def create_new_brand(body: BrandCreate, user_data: dict = Depends(verify_supabase_token)):
    """Cria nova marca na organização (editor+)."""
    _require_org_editor(body.org_id, user_data["user_id"])

    # Verifica limite de brands
    org = get_organization(body.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organização não encontrada")
    existing = list_brands(body.org_id)
    if org.max_brands != -1 and len(existing) >= org.max_brands:
        raise HTTPException(
            status_code=403,
            detail=f"Limite de {org.max_brands} marcas atingido. Faça upgrade do plano.",
        )

    data = body.model_dump(exclude={"org_id"}, exclude_none=True)
    brand = create_brand(org_id=body.org_id, **data)
    return {"message": "Marca criada", "brand": {"id": brand.id, "name": brand.name}}


@router.get("/{brand_id}")
async def get_brand_detail(brand_id: str, user_data: dict = Depends(verify_supabase_token)):
    """Retorna detalhes completos da marca."""
    brand = get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    _require_org_member(brand.org_id, user_data["user_id"])
    return {
        "id": brand.id,
        "org_id": brand.org_id,
        "name": brand.name,
        "nicho": brand.nicho,
        "empresa": brand.empresa,
        "valores_texto": brand.valores_texto,
        "publico_texto": brand.publico_texto,
        "historia_texto": brand.historia_texto,
        "tom_de_voz": brand.tom_de_voz,
        "logo_url": brand.logo_url,
        "color_primary": brand.color_primary,
        "color_secondary": brand.color_secondary,
        "instagram_handle": brand.instagram_handle,
        "website": brand.website,
        "active": brand.active,
    }


@router.put("/{brand_id}")
async def update_brand_detail(
    brand_id: str, body: BrandUpdate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Atualiza marca (editor+)."""
    brand = get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    _require_org_editor(brand.org_id, user_data["user_id"])

    data = {k: v for k, v in body.model_dump().items() if v is not None}
    updated = update_brand(brand_id, data)
    return {"message": "Marca atualizada", "brand": {"id": updated.id, "name": updated.name}}


@router.delete("/{brand_id}")
async def deactivate_brand(brand_id: str, user_data: dict = Depends(verify_supabase_token)):
    """Desativa marca (admin/owner)."""
    brand = get_brand(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Marca não encontrada")

    membership = get_user_membership(brand.org_id, user_data["user_id"])
    if not membership or membership.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Apenas admin/owner pode desativar marcas")

    delete_brand(brand_id)
    return {"message": "Marca desativada"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_org_member(org_id: str, user_id: str):
    membership = get_user_membership(org_id, user_id)
    if not membership:
        raise HTTPException(status_code=403, detail="Você não é membro desta organização")


def _require_org_editor(org_id: str, user_id: str):
    membership = get_user_membership(org_id, user_id)
    if not membership or membership.role == "viewer":
        raise HTTPException(status_code=403, detail="Permissão insuficiente. Requer editor ou superior.")
