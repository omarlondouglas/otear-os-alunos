import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.core.security import verify_supabase_token
from app.core.supabase import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


class AssetCreate(BaseModel):
    type: str                    # 'video', 'carousel', 'script', 'image'
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[dict] = None


def save_asset(user_id: str, asset_type: str, title: str = None,
               description: str = None,
               url: str = None, thumbnail_url: str = None, metadata: dict = None,
               org_id: str = None, brand_id: str = None) -> dict:
    """Salva asset na biblioteca do usuário. Usado internamente pelas tools.
    Quando org_id/brand_id são passados, o asset fica associado à organização/marca."""
    try:
        # Resolve org/brand do thread-local se não passados explicitamente
        if not org_id:
            from app.agents.agno_tools import get_current_org_id
            org_id = get_current_org_id()
        if not brand_id:
            from app.agents.agno_tools import get_current_brand_id
            brand_id = get_current_brand_id()

        client = get_supabase()
        payload = {
            "user_id": user_id,
            "type": asset_type,
            "title": title,
            "description": description,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "metadata": metadata or {},
        }
        if org_id:
            payload["org_id"] = org_id
        if brand_id:
            payload["brand_id"] = brand_id

        result = client.table("content_assets").insert(payload).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.warning(f"Falha ao salvar asset na biblioteca: {e}")
        return {}


@router.get("")
async def list_assets(
    type: Optional[str] = Query(None, description="Filtrar por tipo: video, carousel, script, image"),
    org_id: Optional[str] = Query(None, description="Filtrar por organização"),
    brand_id: Optional[str] = Query(None, description="Filtrar por marca"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    user_data: dict = Depends(verify_supabase_token),
):
    """Lista os ativos de conteúdo. Filtra por org/brand se fornecidos."""
    client = get_supabase()

    # Se org_id fornecido, valida membership e lista assets da org inteira
    if org_id:
        from app.models.organization import get_user_membership
        membership = get_user_membership(org_id, user_data["user_id"])
        if not membership:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Você não é membro desta organização")
        query = (
            client.table("content_assets")
            .select("*")
            .eq("org_id", org_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if brand_id:
            query = query.eq("brand_id", brand_id)
    else:
        query = (
            client.table("content_assets")
            .select("*")
            .eq("user_id", user_data["user_id"])
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )

    if type:
        query = query.eq("type", type)

    result = query.execute()
    return {"assets": result.data or [], "total": len(result.data or [])}


@router.post("")
async def create_asset(
    body: AssetCreate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Salva um ativo manualmente na biblioteca."""
    asset = save_asset(
        user_id=user_data["user_id"],
        asset_type=body.type,
        title=body.title,
        description=body.description,
        url=body.url,
        thumbnail_url=body.thumbnail_url,
        metadata=body.metadata,
    )
    if not asset:
        raise HTTPException(status_code=500, detail="Nao foi possivel salvar o ativo")
    return {"message": "Ativo salvo", "asset": asset}


class AssetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    metadata: Optional[dict] = None


@router.patch("/{asset_id}")
async def update_asset(
    asset_id: str,
    body: AssetUpdate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Atualiza campos de um ativo (title, description, metadata.content para roteiros).

    Só atualiza os campos enviados — campos None são ignorados.
    """
    client = get_supabase()
    payload = {k: v for k, v in body.model_dump().items() if v is not None}
    if not payload:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    # Garante que so atualiza ativos do proprio user
    result = (
        client.table("content_assets")
        .update(payload)
        .eq("id", asset_id)
        .eq("user_id", user_data["user_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return {"message": "Ativo atualizado", "asset": result.data[0]}


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    user_data: dict = Depends(verify_supabase_token),
):
    """Remove um ativo da biblioteca do usuário."""
    client = get_supabase()
    result = (
        client.table("content_assets")
        .delete()
        .eq("id", asset_id)
        .eq("user_id", user_data["user_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return {"message": "Ativo removido"}
