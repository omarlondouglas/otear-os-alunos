from dataclasses import dataclass, field
from typing import Optional
from app.core.supabase import get_supabase
import logging

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    user_id: str
    empresa: Optional[str] = None
    nicho: Optional[str] = None
    valores_texto: Optional[str] = None
    publico_texto: Optional[str] = None
    historia_texto: Optional[str] = None
    tom_de_voz: Optional[str] = None
    # Rede social principal do cliente (Instagram ou TikTok)
    social_handle: Optional[str] = None       # ex: "@marlon"
    social_platform: Optional[str] = None     # "instagram" | "tiktok"
    # Nicho especifico do CONTEUDO (diferente de 'nicho' que eh da empresa)
    nicho_conteudo: Optional[str] = None
    # Lista de criadores que inspiram o cliente — JSON serializado
    # ex: '[{"platform":"tiktok","handle":"@hormozi"}, ...]'
    inspiracoes: Optional[str] = None
    onboarding_completed: bool = False


_PROFILE_FIELDS = {
    "user_id", "empresa", "nicho", "valores_texto", "publico_texto",
    "historia_texto", "tom_de_voz",
    "social_handle", "social_platform", "nicho_conteudo", "inspiracoes",
    "onboarding_completed",
}

def _row_to_profile(row: dict) -> "UserProfile":
    return UserProfile(**{k: v for k, v in row.items() if k in _PROFILE_FIELDS})


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Busca perfil do usuário no Supabase. Retorna None se não existir."""
    try:
        client = get_supabase()
        result = client.table("user_profiles").select("*").eq("user_id", user_id).single().execute()
        if result.data:
            return _row_to_profile(result.data)
        return None
    except Exception as e:
        logger.warning(f"Perfil não encontrado para user_id={user_id}: {e}")
        return None


def upsert_user_profile(user_id: str, data: dict) -> UserProfile:
    """Cria ou atualiza perfil do usuário no Supabase."""
    client = get_supabase()
    payload = {"user_id": user_id, **data}
    result = client.table("user_profiles").upsert(payload, on_conflict="user_id").execute()
    if result.data:
        return _row_to_profile(result.data[0])
    # Supabase pode retornar data vazio em alguns casos mesmo com sucesso — busca o perfil
    saved = get_user_profile(user_id)
    if saved:
        return saved
    # Retorna um objeto mínimo para não quebrar o fluxo
    return UserProfile(user_id=user_id, **{k: v for k, v in data.items() if k != "user_id"})


def build_user_context(profile: Optional[UserProfile]) -> str:
    """
    Monta o contexto de conhecimento do usuário para injetar nos agentes.
    Se não há perfil, retorna string vazia (agentes usarão defaults globais).
    """
    if not profile:
        return ""

    parts = []

    if profile.empresa:
        parts.append(f"## Empresa\n{profile.empresa}")
    if profile.nicho:
        parts.append(f"## Nicho / Área de Atuação\n{profile.nicho}")
    if profile.valores_texto:
        parts.append(f"## Valores e Propósito\n{profile.valores_texto}")
    if profile.publico_texto:
        parts.append(f"## Público-Alvo\n{profile.publico_texto}")
    if profile.historia_texto:
        parts.append(f"## História do Empreendedor\n{profile.historia_texto}")
    if profile.tom_de_voz:
        parts.append(f"## Tom de Voz\n{profile.tom_de_voz}")
    if profile.social_handle:
        platform = profile.social_platform or "rede social"
        parts.append(f"## Rede Social Principal\n{platform}: {profile.social_handle}")
    if profile.nicho_conteudo:
        parts.append(f"## Nicho do Conteúdo\n{profile.nicho_conteudo}")
    if profile.inspiracoes:
        parts.append(f"## Criadores que Inspiram\n{profile.inspiracoes}")

    if not parts:
        return ""

    return (
        "=== PERFIL DO CLIENTE ===\n"
        + "\n\n".join(parts)
        + "\n=== FIM DO PERFIL ===\n"
    )
