"""
Modelo de Marca/Cliente (multi-brand dentro de uma organização).
Cada agência gerencia N marcas, cada uma com identidade visual e tom de voz próprios.
Armazenado no Supabase.
"""
from dataclasses import dataclass
from typing import Optional, List
from app.core.supabase import get_supabase
import logging

logger = logging.getLogger(__name__)


@dataclass
class Brand:
    id: str
    org_id: str
    name: str
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
    active: bool = True
    created_at: Optional[str] = None


_BRAND_FIELDS = set(Brand.__dataclass_fields__.keys())


def _row_to_brand(row: dict) -> Brand:
    return Brand(**{k: v for k, v in row.items() if k in _BRAND_FIELDS})


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_brand(org_id: str, name: str, **kwargs) -> Brand:
    """Cria uma nova marca dentro da organização."""
    client = get_supabase()
    payload = {"org_id": org_id, "name": name}
    allowed = _BRAND_FIELDS - {"id", "created_at"}
    payload.update({k: v for k, v in kwargs.items() if k in allowed and v is not None})

    result = client.table("brands").insert(payload).execute()
    return _row_to_brand(result.data[0])


def get_brand(brand_id: str) -> Optional[Brand]:
    """Busca marca por ID."""
    try:
        client = get_supabase()
        result = client.table("brands").select("*").eq("id", brand_id).single().execute()
        return _row_to_brand(result.data) if result.data else None
    except Exception:
        return None


def list_brands(org_id: str, active_only: bool = True) -> List[Brand]:
    """Lista todas as marcas de uma organização."""
    try:
        client = get_supabase()
        query = client.table("brands").select("*").eq("org_id", org_id).order("name")
        if active_only:
            query = query.eq("active", True)
        result = query.execute()
        return [_row_to_brand(r) for r in (result.data or [])]
    except Exception as e:
        logger.warning(f"Erro ao listar brands de org={org_id}: {e}")
        return []


def update_brand(brand_id: str, data: dict) -> Optional[Brand]:
    """Atualiza campos da marca."""
    client = get_supabase()
    allowed = _BRAND_FIELDS - {"id", "org_id", "created_at"}
    payload = {k: v for k, v in data.items() if k in allowed}
    if not payload:
        return get_brand(brand_id)
    result = client.table("brands").update(payload).eq("id", brand_id).execute()
    return _row_to_brand(result.data[0]) if result.data else None


def delete_brand(brand_id: str) -> bool:
    """Soft-delete: desativa a marca."""
    client = get_supabase()
    result = client.table("brands").update({"active": False}).eq("id", brand_id).execute()
    return bool(result.data)


def build_brand_context(brand: Optional[Brand]) -> str:
    """
    Monta o contexto de marca para injetar nos agentes.
    Substitui build_user_context quando uma brand está selecionada.
    """
    if not brand:
        return ""

    parts = []
    if brand.empresa:
        parts.append(f"## Empresa / Marca\n{brand.empresa}")
    if brand.name:
        parts.append(f"## Nome da Marca\n{brand.name}")
    if brand.nicho:
        parts.append(f"## Nicho / Área de Atuação\n{brand.nicho}")
    if brand.valores_texto:
        parts.append(f"## Valores e Propósito\n{brand.valores_texto}")
    if brand.publico_texto:
        parts.append(f"## Público-Alvo\n{brand.publico_texto}")
    if brand.historia_texto:
        parts.append(f"## História da Marca\n{brand.historia_texto}")
    if brand.tom_de_voz:
        parts.append(f"## Tom de Voz\n{brand.tom_de_voz}")
    if brand.instagram_handle:
        parts.append(f"## Instagram\n@{brand.instagram_handle}")
    if brand.website:
        parts.append(f"## Website\n{brand.website}")

    if not parts:
        return ""

    return (
        "=== PERFIL DA MARCA ===\n"
        + "\n\n".join(parts)
        + "\n=== FIM DO PERFIL DA MARCA ===\n"
    )
