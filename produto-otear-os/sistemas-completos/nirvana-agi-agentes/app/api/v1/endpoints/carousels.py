import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
import httpx

from app.core.security import verify_supabase_token

router = APIRouter()
logger = logging.getLogger(__name__)


class CarouselRenderRequest(BaseModel):
    slides: List[Dict[str, Any]] = Field(..., min_length=1, max_length=20)
    title: Optional[str] = None


class CarouselDownloadRequest(BaseModel):
    url: str
    filename: str = "carrossel-slide.png"


@router.post("/render")
async def render_carousel(
    body: CarouselRenderRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Renderiza slides pelo serviço interno de carrossel.

    Mantem a UI desacoplada do sidecar `carousel`: o browser fala com a API
    principal autenticada e a API chama o renderer pela rede interna.
    """
    try:
        from app.agents.agno_tools import generate_carousel_tool

        result = generate_carousel_tool(body.slides)
    except Exception as exc:
        logger.exception("Erro ao renderizar carrossel para user %s", user_data.get("user_id"))
        raise HTTPException(status_code=502, detail=f"Renderer indisponivel: {exc}") from exc

    if not result or not result.get("success"):
        detail = result.get("error") if isinstance(result, dict) else "Falha ao renderizar carrossel"
        raise HTTPException(status_code=502, detail=detail)

    return result


@router.post("/download")
async def download_carousel_slide(
    body: CarouselDownloadRequest,
    _: dict = Depends(verify_supabase_token),
):
    """Baixa um PNG persistido no storage sem depender de CORS do bucket."""
    storage_base = os.getenv("S3_PUBLIC_URL", "").strip().rstrip("/")
    if not storage_base or not body.url.startswith(f"{storage_base}/"):
        raise HTTPException(status_code=400, detail="URL de imagem do carrossel invÃ¡lida")

    filename = os.path.basename(body.filename) or "carrossel-slide.png"
    if not filename.endswith(".png"):
        filename = f"{filename}.png"

    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=False) as client:
            response = await client.get(body.url)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Arquivo persistido indisponÃ­vel: {exc}") from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Storage retornou HTTP {response.status_code}")

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "image/png"),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/image/{carousel_id}/{filename}")
async def proxy_carousel_image(carousel_id: str, filename: str, download: bool = False):
    """Serve imagens locais geradas pelo sidecar de carrossel via gateway."""
    from app.agents.agno_tools import get_carousel_url

    upstream = f"{get_carousel_url().rstrip('/')}/api/image/{carousel_id}/{filename}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(upstream)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Imagem do carrossel indisponivel: {exc}") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Imagem do carrossel nao encontrada")
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Renderer retornou HTTP {response.status_code}")

    headers = {"Cache-Control": "public, max-age=86400"}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return Response(
        content=response.content,
        media_type=response.headers.get("content-type", "image/png"),
        headers=headers,
    )
