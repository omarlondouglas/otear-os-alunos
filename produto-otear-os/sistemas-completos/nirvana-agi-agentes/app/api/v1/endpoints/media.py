import logging
import os
from io import BytesIO
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from app.core.security_admin import verify_admin_access
from app.services.storage import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()

STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage")
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:8000")

ALLOWED_EXTENSIONS = {
    "jpg", "jpeg", "png", "gif", "webp",
    "mp4", "webm", "mov",
    "txt", "md", "csv", "json", "srt", "vtt", "pdf", "doc", "docx",
}
TEXT_EXTENSIONS = {"txt", "md", "csv", "json", "srt", "vtt"}
READABLE_DOC_EXTENSIONS = TEXT_EXTENSIONS | {"pdf", "docx"}
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_TEXT_CONTEXT_CHARS = 40_000


class MediaItem(BaseModel):
    id: str
    type: str
    url: str
    thumbnail: Optional[str] = None
    title: str
    created_at: str


class UploadResponse(BaseModel):
    filename: str
    url: str
    asset_id: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    content_text: Optional[str] = None
    text_truncated: bool = False


class MediaResponse(BaseModel):
    items: List[MediaItem]
    total: int


@router.post("/media/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_data: Any = Depends(verify_admin_access),
):
    """Upload a file to storage (admin only). Validates type and size."""
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Tipo de arquivo não permitido. Aceitos: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(413, f"Arquivo muito grande. Máximo: {MAX_UPLOAD_SIZE // (1024*1024)}MB")

    await file.seek(0)

    storage = StorageService()
    content_text = None
    text_truncated = False
    if ext in READABLE_DOC_EXTENSIONS:
        content_text = _extract_text_content(ext, content)
        if len(content_text) > MAX_TEXT_CONTEXT_CHARS:
            content_text = content_text[:MAX_TEXT_CONTEXT_CHARS]
            text_truncated = True

    url = await storage.save_upload_file(file)
    asset_id = None

    if isinstance(user_data, dict) and _is_document_extension(ext):
        try:
            from app.api.v1.endpoints.library import save_asset

            saved = save_asset(
                user_id=user_data["user_id"],
                asset_type="other",
                title=filename,
                description=_build_document_description(content_text, filename),
                url=url,
                metadata={
                    "kind": "document",
                    "filename": filename,
                    "extension": ext,
                    "content_type": file.content_type,
                    "size": len(content),
                    "content": content_text or "",
                    "text_truncated": text_truncated,
                },
            )
            asset_id = saved.get("id") if saved else None
        except Exception as exc:
            logger.warning("Failed to save uploaded document to library: %s", exc)

    return UploadResponse(
        filename=filename,
        url=url,
        asset_id=asset_id,
        content_type=file.content_type,
        size=len(content),
        content_text=content_text,
        text_truncated=text_truncated,
    )


def _is_document_extension(ext: str) -> bool:
    return ext in {"txt", "md", "csv", "json", "srt", "vtt", "pdf", "doc", "docx"}


def _build_document_description(content_text: Optional[str], filename: str) -> str:
    if content_text:
        preview = " ".join(content_text.split())
        return preview[:300] + ("..." if len(preview) > 300 else "")
    return f"Documento enviado: {filename}"


def _extract_text_content(ext: str, content: bytes) -> str:
    if ext in TEXT_EXTENSIONS:
        return _decode_text_content(content)
    if ext == "pdf":
        return _extract_pdf_text(content)
    if ext == "docx":
        return _extract_docx_text(content)
    return ""


def _decode_text_content(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return content.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return ""


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        pages = [(page.extract_text() or "").strip() for page in reader.pages[:20]]
        return "\n\n".join(page for page in pages if page).strip()
    except Exception as exc:
        logger.warning("PDF text extraction failed: %s", exc)
        return ""


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document

        doc = Document(BytesIO(content))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs).strip()
    except Exception as exc:
        logger.warning("DOCX text extraction failed: %s", exc)
        return ""


@router.get("/media", response_model=MediaResponse)
async def get_media(
    type_filter: Optional[str] = Query(None, alias="type"),
    limit: int = Query(50, ge=1, le=200),
    _: bool = Depends(verify_admin_access),
):
    """Get media library items (admin only)."""
    items: List[MediaItem] = []

    try:
        if os.path.exists(STORAGE_PATH):
            for filename in os.listdir(STORAGE_PATH):
                filepath = os.path.join(STORAGE_PATH, filename)

                if not os.path.isfile(filepath):
                    continue

                ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

                if ext in ("jpg", "jpeg", "png", "gif", "webp"):
                    media_type = "image"
                elif ext in ("mp4", "webm", "mov", "avi", "mkv"):
                    media_type = "video"
                else:
                    continue

                if type_filter and media_type != type_filter:
                    continue

                file_stat = os.stat(filepath)
                created_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                media_url = f"{PUBLIC_URL}/static/{filename}"
                title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

                items.append(MediaItem(
                    id=f"media-{hash(filename)}",
                    type=media_type,
                    url=media_url,
                    thumbnail=media_url if media_type == "image" else None,
                    title=title,
                    created_at=created_at,
                ))

        items.sort(key=lambda x: x.created_at, reverse=True)
        items = items[:limit]

        if not items:
            items = _get_demo_media()

        return MediaResponse(items=items, total=len(items))

    except Exception:
        return MediaResponse(items=_get_demo_media(), total=len(_get_demo_media()))


def _get_demo_media() -> List[MediaItem]:
    """Return demo media items for testing."""
    return [
        MediaItem(id="demo-img-1", type="image",
                  url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400",
                  thumbnail="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=200",
                  title="Imagem Gerada - Abstrato", created_at=datetime.now().isoformat()),
        MediaItem(id="demo-img-2", type="image",
                  url="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=400",
                  thumbnail="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=200",
                  title="Gradiente Neon", created_at=datetime.now().isoformat()),
        MediaItem(id="demo-vid-1", type="video",
                  url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                  thumbnail=None, title="Vídeo Editado - Demo", created_at=datetime.now().isoformat()),
    ]
