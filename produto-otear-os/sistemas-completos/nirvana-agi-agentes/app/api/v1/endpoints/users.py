from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.core.security import verify_supabase_token
from app.models.user_profile import get_user_profile, upsert_user_profile

router = APIRouter()


class ProfileUpdate(BaseModel):
    empresa: Optional[str] = Field(None, max_length=255)
    nicho: Optional[str] = Field(None, max_length=255)
    valores_texto: Optional[str] = Field(None, max_length=5000)
    publico_texto: Optional[str] = Field(None, max_length=5000)
    historia_texto: Optional[str] = Field(None, max_length=10000)
    tom_de_voz: Optional[str] = Field(None, max_length=255)
    social_handle: Optional[str] = Field(None, max_length=255)
    social_platform: Optional[str] = Field(None, max_length=50)
    nicho_conteudo: Optional[str] = Field(None, max_length=255)
    inspiracoes: Optional[str] = Field(None, max_length=5000)
    onboarding_completed: Optional[bool] = None


@router.get("/me")
async def get_my_profile(user_data: dict = Depends(verify_supabase_token)):
    """Retorna o perfil do usuário autenticado."""
    profile = get_user_profile(user_data["user_id"])
    if not profile:
        return {
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "onboarding_completed": False,
        }
    return {
        "user_id": profile.user_id,
        "email": user_data["email"],
        "empresa": profile.empresa,
        "nicho": profile.nicho,
        "valores_texto": profile.valores_texto,
        "publico_texto": profile.publico_texto,
        "historia_texto": profile.historia_texto,
        "tom_de_voz": profile.tom_de_voz,
        "social_handle": profile.social_handle,
        "social_platform": profile.social_platform,
        "nicho_conteudo": profile.nicho_conteudo,
        "inspiracoes": profile.inspiracoes,
        "onboarding_completed": profile.onboarding_completed,
    }


@router.put("/me")
async def update_my_profile(
    body: ProfileUpdate,
    user_data: dict = Depends(verify_supabase_token),
):
    """Atualiza o perfil do usuário autenticado."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    profile = upsert_user_profile(user_data["user_id"], data)
    return {"message": "Perfil atualizado com sucesso", "onboarding_completed": profile.onboarding_completed}
