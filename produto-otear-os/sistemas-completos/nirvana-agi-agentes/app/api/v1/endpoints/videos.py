import json
import logging
import math
import os
import re
import subprocess
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, BackgroundTasks
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.schemas.video import VideoEditRequest, JobResponse
from app.services.video_processor import VideoProcessor
from app.workers.video_tasks import process_video_task
from app.core.database import get_db
from app.core.security import verify_api_key, verify_supabase_token, verify_api_key_or_token
from app.services.storage import StorageService
from app.services.video_presets import VideoPresets

logger = logging.getLogger(__name__)
router = APIRouter()


def _save_completed_video_to_library(user_id: str, download_url: str, job_id: str):
    """Auto-save completed video to user's library (runs as background task)."""
    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        # Check if already saved (avoid duplicates from repeated polling)
        existing = client.table("content_assets").select("id").eq(
            "user_id", user_id
        ).eq("metadata->>job_id", job_id).execute()
        if existing.data:
            return
        from app.api.v1.endpoints.library import save_asset
        save_asset(
            user_id=user_id,
            asset_type="video",
            title="Vídeo editado",
            url=download_url,
            metadata={"job_id": job_id},
        )
        logger.info(f"[AutoSave] Video {job_id} saved to library for user {user_id}")
    except Exception as e:
        logger.warning(f"[AutoSave] Failed to save video to library: {e}")


# ─── Presets de edição (expandidos localmente) ────────────────────────────────

EDIT_PRESETS = {
    "VIRAL": {
        "description": "Legendas amarelas estilo viral + remoção de silêncio",
        "operations": [
            {"type": "auto_subtitle", "params": {"style": {"color": "#FFFF00", "font_size": 10, "animation": "typewriter", "position": "bottom"}}},
            {"type": "remove_silence", "params": {}},
        ],
    },
    "MODERN_SUBTITLES": {
        "description": "Legendas brancas modernas com destaque por palavra",
        "operations": [
            {"type": "auto_subtitle", "params": {"style": {"color": "#FFFFFF", "font_size": 10, "animation": "highlight-word", "position": "bottom"}}},
        ],
    },
    "CLEAN": {
        "description": "Legendas estáticas + remoção de silêncio",
        "operations": [
            {"type": "remove_silence", "params": {"threshold": -35, "padding": 0.08, "min_silence_duration": 0.45}},
            {"type": "auto_subtitle", "params": {"style": {"color": "#FFFFFF", "font_size": 10, "position": "bottom"}}},
        ],
    },
    "REACTION": {
        "description": "Otimizado para vídeos de reação",
        "operations": [
            {"type": "auto_subtitle", "params": {"style": {"color": "#FFFFFF", "font_size": 10, "position": "bottom"}}},
        ],
    },
    "TITLE_BAR": {
        "description": "Título com barra escura de fundo",
        "operations": [
            {"type": "add_text_overlay", "params": {
                "text": "",
                "position": "top",
                "font_size": 28,
                "font_color": "white",
                "box": True,
                "box_color": "black",
                "box_opacity": 0.7,
                "box_full_width": True,
                "box_padding": 20,
                "box_height": 80,
            }},
        ],
    },
    "MELHORES_MOMENTOS": {
        "description": "Extraindo os melhores momentos como clips individuais",
        "operations": [
            {"type": "extract_clips", "params": {
                "auto_detect": True,
                "max_clips": 5,
                "min_duration": 30.0,
                "min_energy_score": 6.0,
                "top_percent": 25.0,
                "padding": 0.5,
            }},
        ],
    },
    "VIRAL_AI": {
        "description": "Pipeline completo com IA: normalização + silêncio + cenas visuais inteligentes + Remotion",
        "operations": [],  # expanded from VideoPresets
    },
    "AULA_AI": {
        "description": "Aula com cenas visuais inteligentes (cards, flows, splits) + Remotion",
        "operations": [],  # expanded from VideoPresets
    },
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _extract_title_text(message: str) -> str:
    """Extrai texto do título da mensagem do usuário.
    Procura texto entre aspas, ou remove keywords e usa o restante."""
    # Texto entre aspas (simples ou duplas)
    match = re.search(r"""["'"'"](.+?)["'"'"]""", message)
    if match:
        return match.group(1).strip()

    # Sem aspas: remove keywords conhecidas e usa o restante
    cleaned = message
    remove_words = [
        "preset", "title_bar", "title bar", "titulo com barra", "título com barra",
        "barra de titulo", "barra de título", "adicionar", "colocar", "titulo", "título",
        "no topo", "embaixo", "no centro",
    ]
    for word in remove_words:
        cleaned = re.sub(re.escape(word), "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip().strip(":-–—").strip()
    return cleaned


def _parse_time_to_seconds(value: str) -> Optional[float]:
    text = value.strip().lower().replace(",", ".")
    text = re.sub(r"\s*(segundos?|secs?|s)\b", "", text).strip()
    if not text:
        return None
    if ":" in text:
        parts = text.split(":")
        try:
            nums = [float(part) for part in parts]
        except ValueError:
            return None
        if len(nums) == 2:
            return nums[0] * 60 + nums[1]
        if len(nums) == 3:
            return nums[0] * 3600 + nums[1] * 60 + nums[2]
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _parse_trim_request(message: str) -> Optional[Dict[str, Any]]:
    msg = message.lower()
    if not any(word in msg for word in ("corta", "cortar", "corte", "trim", "recorta", "recortar")):
        return None

    time_token = r"(\d{1,2}(?::\d{1,2}){1,2}|\d+(?:[,.]\d+)?\s*(?:s|seg|segundo|segundos)?)"
    patterns = [
        rf"(?:de|do|entre)\s*{time_token}\s*(?:ate|até|a|ao|e|-)\s*{time_token}",
        rf"{time_token}\s*(?:ate|até|a|ao|-)\s*{time_token}",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if not match:
            continue
        start = _parse_time_to_seconds(match.group(1))
        end = _parse_time_to_seconds(match.group(2))
        if start is None or end is None or end <= start:
            continue
        return {
            "preset": None,
            "operations": [{"type": "trim", "params": {"start": start, "end": end}}],
            "message": f"Cortando o video de {start:g}s ate {end:g}s",
        }

    first_seconds = re.search(rf"(?:primeiros?|inicio|início)\s*{time_token}", msg)
    if first_seconds:
        end = _parse_time_to_seconds(first_seconds.group(1))
        if end and end > 0:
            return {
                "preset": None,
                "operations": [{"type": "trim", "params": {"start": 0, "end": end}}],
                "message": f"Mantendo os primeiros {end:g}s do video",
            }

    return None


# ─── Intent Parser ────────────────────────────────────────────────────────────

def _parse_edit_intent(user_message: str) -> Dict[str, Any]:
    """
    Analisa a mensagem do usuário e retorna o preset/operações desejados.
    Usa keyword matching primeiro (instantâneo). LLM como fallback.
    """
    msg_lower = user_message.lower().strip()

    trim_intent = _parse_trim_request(user_message)
    if trim_intent:
        return trim_intent

    # 1. Detecção direta por keywords (instantâneo, sem LLM)
    # Melhores momentos PRIMEIRO (antes de "viral" para evitar falso match)
    momentos_keywords = ["melhores momentos", "best moments", "extract clips", "extrair clips",
                         "extraia os melhores", "clips individuais", "opus clip", "melhores momento"]
    if any(kw in msg_lower for kw in momentos_keywords):
        return {"preset": "MELHORES_MOMENTOS", "operations": None, "message": EDIT_PRESETS["MELHORES_MOMENTOS"]["description"]}

    # Viral AI / Aula AI (full pipeline with scene planning)
    ai_viral_kw = ["viral ai", "viral inteligente", "cenas inteligentes", "preset viral_ai", "viral com cenas"]
    if any(kw in msg_lower for kw in ai_viral_kw):
        return {"preset": "VIRAL_AI", "operations": None, "message": EDIT_PRESETS["VIRAL_AI"]["description"]}

    ai_aula_kw = ["aula ai", "aula inteligente", "preset aula_ai", "aula com cenas"]
    if any(kw in msg_lower for kw in ai_aula_kw):
        return {"preset": "AULA_AI", "operations": None, "message": EDIT_PRESETS["AULA_AI"]["description"]}

    # Presets editordofuturo (cascata LLM + analise de conteudo)
    # IMPORTANTE: precisa matchar ANTES de "viral" generico abaixo
    futuro_pro_kw = ["viral_futuro_pro", "viral futuro pro", "preset viral_futuro_pro"]
    if any(kw in msg_lower for kw in futuro_pro_kw):
        return {
            "preset": "VIRAL_FUTURO_PRO", "operations": None,
            "message": "Selecionando clipes virais via cascata LLM + eval automatico de boundaries",
        }
    futuro_kw = ["viral_futuro", "viral futuro", "preset viral_futuro"]
    if any(kw in msg_lower for kw in futuro_kw):
        return {
            "preset": "VIRAL_FUTURO", "operations": None,
            "message": "Selecionando clipes virais via cascata LLM (Claude/GPT/Gemini/Llama)",
        }
    clean_pro_kw = ["clean_pro", "clean pro", "preset clean_pro", "limpar fillers", "remove fillers"]
    if any(kw in msg_lower for kw in clean_pro_kw):
        return {
            "preset": "CLEAN_PRO", "operations": None,
            "message": "Removendo fillers ('uh', 'tipo', 'ne') + silencios via transcript",
        }
    fast_hormozi_kw = ["fast_hormozi", "fast hormozi", "preset fast_hormozi", "hormozi rapido"]
    if any(kw in msg_lower for kw in fast_hormozi_kw):
        return {
            "preset": "FAST_HORMOZI", "operations": None,
            "message": "Render Hormozi via FFmpeg+libass (10x mais rapido)",
        }

    keyword_map = {
        "AULA": ["aula", "preset aula", "curso", "palestra"],
        "VIRAL_PRO": ["viral_pro", "viral pro", "preset viral_pro"],
        "AULA_PRO": ["aula_pro", "aula pro", "preset aula_pro"],
        "HORMOZI": ["hormozi", "preset hormozi"],
        "PODCAST": ["podcast", "preset podcast"],
        "VIRAL": ["viral", "preset viral", "legendas amarelas", "amarelo"],
        "CLEAN": ["clean", "preset clean", "limpo", "simples"],
        "MODERN_SUBTITLES": ["moderno", "modern", "preset modern", "legendas brancas", "branco"],
        "REACTION": ["reação", "reaction", "react"],
        "TITLE_BAR": ["title_bar", "titulo com barra", "título com barra", "barra de titulo", "barra de título", "title bar"],
    }

    for preset_name, keywords in keyword_map.items():
        if any(kw in msg_lower for kw in keywords):
            description = EDIT_PRESETS.get(preset_name, {}).get("description") or f"Aplicando preset {preset_name}"
            return {"preset": preset_name, "operations": None, "message": description}

    # Legendas com cor específica — detectar cor antes de cair no preset genérico
    subtitle_keywords = ["legenda", "subtitle", "legendar", "adicionar legenda", "colocar legenda", "auto subtitle"]
    if any(kw in msg_lower for kw in subtitle_keywords):
        # Detectar cor na mensagem
        color_map = {
            "verde": "#00FF00", "green": "#00FF00",
            "vermelh": "#FF0000", "red": "#FF0000",
            "azul": "#0088FF", "blue": "#0088FF",
            "branc": "#FFFFFF", "white": "#FFFFFF",
            "amarel": "#FFFF00", "yellow": "#FFFF00",
            "rosa": "#FF69B4", "pink": "#FF69B4",
            "roxo": "#9B59B6", "purple": "#9B59B6",
            "laranja": "#FF8C00", "orange": "#FF8C00",
            "ciano": "#00FFFF", "cyan": "#00FFFF",
        }
        detected_color = None
        for color_word, hex_val in color_map.items():
            if color_word in msg_lower:
                detected_color = hex_val
                break

        if detected_color:
            return {
                "preset": None,
                "operations": [
                    {"type": "auto_subtitle", "params": {"style": {
                        "color": detected_color, "font_size": 10,
                        "position": "bottom", "animation": "highlight-word",
                        "margin_vertical": 60,
                    }}},
                ],
                "message": f"Adicionando legendas na cor {detected_color}",
            }
        return {"preset": "VIRAL", "operations": None, "message": "Adicionando legendas estilo viral (padrão)"}

    # Remoção de silêncio
    silence_keywords = ["silêncio", "silencio", "respiro", "cortar respiro", "remove silence", "pausas", "cortar pausas"]
    if any(kw in msg_lower for kw in silence_keywords):
        return {"preset": None, "operations": [{"type": "remove_silence", "params": {}}], "message": "Removendo silêncios e respiros"}

    # 2. Fallback: usar LLM para interpretar mensagem ambígua
    try:
        return _parse_intent_with_llm(user_message)
    except Exception as e:
        logger.warning(f"LLM intent parsing failed: {e}, defaulting to VIRAL")
        return {"preset": "VIRAL", "operations": None, "message": "Aplicando preset VIRAL (padrão)"}


def _parse_intent_with_llm(user_message: str) -> Dict[str, Any]:
    """Usa LLM para interpretar mensagem ambígua do usuário."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    if openrouter_key:
        return _parse_intent_openrouter(user_message, openrouter_key)
    elif api_key:
        return _parse_intent_anthropic(user_message, api_key)
    elif google_key:
        return _parse_intent_google(user_message, google_key)
    else:
        # Sem LLM disponível — fallback seguro
        return {"preset": "VIRAL", "operations": None, "message": "Aplicando preset VIRAL (padrão)"}


def _parse_intent_openrouter(user_message: str, api_key: str) -> Dict[str, Any]:
    """Parse intent usando OpenRouter (OpenAI-compatible)."""
    from openai import OpenAI

    headers = {}
    referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("PUBLIC_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME", "O Tear")
    if referer:
        headers["HTTP-Referer"] = referer
    if app_name:
        headers["X-Title"] = app_name

    client = OpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers=headers or None,
    )
    prompt = (
        "Voce e um parser de intencao para edicao de video. Retorne APENAS JSON.\n\n"
        "Presets: VIRAL, CLEAN, MODERN_SUBTITLES, REACTION, TITLE_BAR, MELHORES_MOMENTOS, VIRAL_AI, AULA_AI\n"
        "Operacoes: auto_subtitle, remove_silence, trim, resize, add_watermark, add_text_overlay, extract_clips\n\n"
        f'Pedido: "{user_message}"\n\n'
        'Se e edicao, retorne: {"preset": "VIRAL", "operations": null, "message": "descricao curta"}\n'
        'Se e operacao avulsa: {"preset": null, "operations": [{"type": "remove_silence", "params": {}}], "message": "descricao"}\n'
        'Se nao e edicao: {"preset": null, "operations": null, "message": "resposta ao usuario"}'
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL_FAST", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
    )

    text = (response.choices[0].message.content or "").strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def _parse_intent_anthropic(user_message: str, api_key: str) -> Dict[str, Any]:
    """Parse intent usando Anthropic Claude."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "Você é um parser de intenção para edição de vídeo. Analise o pedido do usuário e retorne APENAS JSON.\n\n"
        "Presets disponíveis: VIRAL, CLEAN, MODERN_SUBTITLES, REACTION, TITLE_BAR, MELHORES_MOMENTOS, VIRAL_AI, AULA_AI\n"
        "MELHORES_MOMENTOS = extrair clips individuais dos melhores momentos (best moments, opus clip style)\n"
        "VIRAL_AI = pipeline completo com IA: normalização + silêncio + cenas visuais inteligentes + Remotion\n"
        "AULA_AI = aula com cenas visuais inteligentes (cards, flows, splits) + Remotion\n"
        "Operações avulsas: auto_subtitle, remove_silence, trim, resize, add_watermark, add_text_overlay, extract_clips\n\n"
        'Se é edição, retorne: {"preset": "VIRAL", "operations": null, "message": "descrição curta"}\n'
        'Se é operação avulsa: {"preset": null, "operations": [{"type": "remove_silence", "params": {}}], "message": "descrição"}\n'
        'Se NÃO é edição: {"preset": null, "operations": null, "message": "resposta ao usuário"}\n\n'
        "Retorne SOMENTE o JSON, sem markdown."
    )

    response = client.messages.create(
        model=os.getenv("MODEL_FAST", "claude-haiku-4-5-20251001"),
        max_tokens=256,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def _parse_intent_google(user_message: str, api_key: str) -> Dict[str, Any]:
    """Parse intent usando Google Gemini."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = (
        "Analise o pedido de edição de vídeo e retorne APENAS JSON.\n\n"
        "Presets: VIRAL, CLEAN, MODERN_SUBTITLES, REACTION, TITLE_BAR, MELHORES_MOMENTOS, VIRAL_AI, AULA_AI\n"
        "MELHORES_MOMENTOS = extrair clips individuais dos melhores momentos\n"
        "VIRAL_AI = pipeline completo com cenas visuais inteligentes\n"
        "AULA_AI = aula com cenas visuais inteligentes\n"
        "Operações: auto_subtitle, remove_silence, trim, resize, extract_clips\n\n"
        f'Pedido: "{user_message}"\n\n'
        'Se é edição, retorne: {{"preset": "VIRAL", "operations": null, "message": "descrição curta"}}\n'
        'Se NÃO é edição: {{"preset": null, "operations": null, "message": "resposta ao usuário"}}\n'
        "SOMENTE JSON."
    )

    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


# ─── Editor Chat (LLM direta + job direto) ──────────────────────────────────


class EditorChatRequest(BaseModel):
    message: str
    video_url: str
    context: Optional[Dict[str, Any]] = None


class EditorChatResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
    job_response: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=EditorChatResponse)
async def editor_chat(
    request: EditorChatRequest,
    user_data: dict = Depends(verify_supabase_token),
    db: Session = Depends(get_db),
):
    """Chat com editor de vídeo. Interpreta intenção e cria job diretamente."""
    try:
        # 1. Interpretar intenção do usuário (rápido, sem agente)
        intent = _parse_edit_intent(request.message)
        logger.info(f"Editor chat intent: {intent}")

        preset_name = intent.get("preset")
        custom_ops = intent.get("operations")
        intent_message = intent.get("message", "")

        # Se não há preset nem operações, é só uma pergunta → responder sem criar job
        if not preset_name and not custom_ops:
            return EditorChatResponse(
                status="success",
                message=intent_message or "Não entendi o pedido de edição. Tente: 'adicionar legendas', 'preset VIRAL', 'cortar respiros'.",
                job_id=None,
            )

        # 2. Montar operações
        if preset_name and preset_name in EDIT_PRESETS:
            operations = [dict(op) for op in EDIT_PRESETS[preset_name]["operations"]]
            description = EDIT_PRESETS[preset_name]["description"]

            # Presets with empty operations are expanded by VideoPresets in the worker
            if not operations:
                operations = [{"type": "preset", "params": {"name": preset_name}}]

            # TITLE_BAR: extrair texto do usuário e injetar na operação
            if preset_name == "TITLE_BAR":
                title_text = _extract_title_text(request.message)
                if title_text:
                    operations[0] = {**operations[0], "params": {**operations[0]["params"], "text": title_text}}
        elif preset_name and preset_name in VideoPresets.list_available():
            # Presets do VideoPresets (VIRAL_FUTURO, CLEAN_PRO, FAST_HORMOZI, etc.)
            # — expansao acontece no worker via VideoPresets.get_operations()
            operations = [{"type": "preset", "params": {"name": preset_name}}]
            description = intent_message or f"Aplicando preset {preset_name}"
        elif custom_ops:
            operations = custom_ops
            description = intent_message
        else:
            operations = EDIT_PRESETS["VIRAL"]["operations"]
            description = EDIT_PRESETS["VIRAL"]["description"]

        # 3. Criar job diretamente no banco (sem passar pelo agente)
        edit_request = VideoEditRequest(
            video_url=request.video_url,
            operations=[{"type": op["type"], "params": op.get("params", {})} for op in operations],
            output_format="mp4",
            priority=7,
        )

        processor = VideoProcessor(db)
        job = await processor.create_job(edit_request)

        # 4. Disparar task Celery
        process_video_task.apply_async(
            args=[job.id],
            priority=edit_request.priority,
        )

        logger.info(f"Editor chat created job {job.id} with operations: {[op['type'] for op in operations]}")

        return EditorChatResponse(
            status="success",
            message=f"{description}. O vídeo está sendo processado.",
            job_id=job.id,
            job_response={"operations": [op["type"] for op in operations], "preset": preset_name},
        )

    except Exception as e:
        logger.error(f"Editor chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv"}
MAX_VIDEO_SIZE = int(os.getenv("MAX_UPLOAD_SIZE_MB", "2048")) * 1024 * 1024  # Default 2GB

CONTENT_TYPE_MAP = {
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "mkv": "video/x-matroska",
}


class VideoUploadResult(BaseModel):
    video_id: str
    video_url: str
    filename: str
    size: int
    storage: str


class PresignedUploadResponse(BaseModel):
    upload_url: str
    video_url: str
    video_id: str
    object_key: str


class ConfirmUploadRequest(BaseModel):
    video_id: str
    object_key: str
    filename: str
    size: int


def _get_s3_client():
    """Cria e retorna um cliente S3 compatível (R2/MinIO/S3)."""
    import boto3
    from botocore.client import Config

    s3_endpoint = os.getenv("S3_ENDPOINT_URL", "").strip().rstrip("/")
    s3_access_key = os.getenv("S3_ACCESS_KEY")
    s3_secret_key = os.getenv("S3_SECRET_KEY")
    s3_region = os.getenv("S3_REGION", "auto")

    if not all([s3_endpoint, s3_access_key, s3_secret_key]):
        return None, None, None

    client = boto3.client(
        "s3",
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key,
        config=Config(signature_version="s3v4"),
        region_name=s3_region,
    )
    bucket = os.getenv("S3_BUCKET_NAME", "videos_agi")
    return client, bucket, s3_endpoint


@router.post("/presign-upload", response_model=PresignedUploadResponse)
async def presign_upload(
    filename: str = Form(...),
    content_type: str = Form("video/mp4"),
    user_data: dict = Depends(verify_supabase_token),
):
    """
    Gera uma presigned URL para upload direto ao MinIO/S3.
    O browser faz PUT diretamente ao MinIO, sem passar pelo backend.
    Suporta vídeos de qualquer tamanho (1GB+).
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Tipo não permitido. Aceitos: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

    s3_client, bucket, s3_endpoint = _get_s3_client()
    if not s3_client:
        raise HTTPException(500, "S3/MinIO não configurado. Configure S3_ENDPOINT_URL, S3_ACCESS_KEY e S3_SECRET_KEY.")

    video_id = str(uuid.uuid4())
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = filename.rsplit(".", 1)[0].replace(" ", "_").lower() if "." in filename else filename
    object_key = f"videos/{clean_name}_{timestamp}_{video_id[:8]}.{ext}"

    # Gerar presigned URL para PUT (válida por 2 horas para uploads grandes)
    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=7200,
    )

    # URL pública para acessar o vídeo depois do upload
    # R2: pub-xxx.r2.dev/{key} (sem bucket no path — URL já é bucket-scoped)
    # Supabase: .../storage/v1/object/public/<bucket>/{key}
    # MinIO: https://minio.example.com/<bucket>/{key}
    s3_public_url = os.getenv("S3_PUBLIC_URL", "").strip().rstrip("/")
    is_r2 = "r2.cloudflarestorage.com" in s3_endpoint or "r2.dev" in s3_public_url
    if s3_public_url:
        if is_r2 or s3_public_url.endswith(f"/{bucket}"):
            video_url = f"{s3_public_url}/{object_key}"
        else:
            video_url = f"{s3_public_url}/{bucket}/{object_key}"
    else:
        video_url = f"{s3_endpoint.rstrip('/')}/{bucket}/{object_key}"

    return PresignedUploadResponse(
        upload_url=upload_url,
        video_url=video_url,
        video_id=video_id,
        object_key=object_key,
    )


# ─── Multipart Presigned Upload (browser → MinIO direto, em partes) ──────────

class MultipartPartInfo(BaseModel):
    part_number: int
    upload_url: str

class MultipartStartResponse(BaseModel):
    upload_id: str
    object_key: str
    video_id: str
    video_url: str
    parts: List[MultipartPartInfo]

class MultipartCompleteRequest(BaseModel):
    upload_id: str
    object_key: str
    video_id: str
    parts: List[Dict]  # [{part_number, etag}]


def _build_video_url(bucket: str, object_key: str) -> str:
    s3_public_url = os.getenv("S3_PUBLIC_URL", "").strip().rstrip("/")
    s3_endpoint = os.getenv("S3_ENDPOINT_URL", "").strip().rstrip("/")
    base = s3_public_url or s3_endpoint
    # R2: URL pública já é bucket-scoped (pub-xxx.r2.dev/{key}, sem bucket no path)
    is_r2 = "r2.cloudflarestorage.com" in s3_endpoint or "r2.dev" in base
    if is_r2 or base.endswith(f"/{bucket}"):
        return f"{base}/{object_key}"
    return f"{base}/{bucket}/{object_key}"


@router.post("/presign-multipart/start", response_model=MultipartStartResponse)
async def presign_multipart_start(
    filename: str = Form(...),
    content_type: str = Form("video/mp4"),
    file_size: int = Form(...),
    user_data: dict = Depends(verify_supabase_token),
):
    """
    Inicia um multipart upload presigned para o R2/S3.
    Retorna presigned URLs para cada parte (5MB cada).
    O browser faz PUT de cada parte diretamente ao storage — sem passar pelo backend,
    sem limite de tamanho de proxy, suporta vídeos de qualquer tamanho.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Tipo não permitido. Aceitos: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

    s3_client, bucket, _ = _get_s3_client()
    if not s3_client:
        raise HTTPException(500, "S3/MinIO não configurado.")

    video_id = str(uuid.uuid4())
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = filename.rsplit(".", 1)[0].replace(" ", "_").lower() if "." in filename else filename
    object_key = f"videos/{clean_name}_{timestamp}_{video_id[:8]}.{ext}"

    # Criar multipart upload no R2/S3
    mpu = s3_client.create_multipart_upload(
        Bucket=bucket, Key=object_key, ContentType=content_type,
    )
    upload_id = mpu["UploadId"]

    # Gerar presigned URL para cada parte (5MB por parte — evita limite de body do Traefik/MinIO)
    part_size = 5 * 1024 * 1024  # 5MB
    num_parts = max(1, math.ceil(file_size / part_size))

    parts = []
    for part_num in range(1, num_parts + 1):
        url = s3_client.generate_presigned_url(
            "upload_part",
            Params={
                "Bucket": bucket,
                "Key": object_key,
                "UploadId": upload_id,
                "PartNumber": part_num,
            },
            ExpiresIn=7200,
        )
        parts.append(MultipartPartInfo(part_number=part_num, upload_url=url))

    return MultipartStartResponse(
        upload_id=upload_id,
        object_key=object_key,
        video_id=video_id,
        video_url=_build_video_url(bucket, object_key),
        parts=parts,
    )


@router.post("/presign-multipart/complete")
async def presign_multipart_complete(
    req: MultipartCompleteRequest,
    user_data: dict = Depends(verify_supabase_token),
):
    """Finaliza o multipart upload após todas as partes terem sido enviadas."""
    s3_client, bucket, _ = _get_s3_client()
    if not s3_client:
        raise HTTPException(500, "S3/MinIO não configurado.")

    # Read ETags from R2/S3 itself. Browsers can only read the ETag response
    # header when bucket CORS exposes it.
    uploaded_parts = []
    marker = 0
    while True:
        response = s3_client.list_parts(
            Bucket=bucket,
            Key=req.object_key,
            UploadId=req.upload_id,
            PartNumberMarker=marker,
        )
        uploaded_parts.extend(response.get("Parts", []))
        if not response.get("IsTruncated"):
            break
        marker = response.get("NextPartNumberMarker", 0)

    expected_numbers = sorted(p["part_number"] for p in req.parts)
    actual_numbers = sorted(p["PartNumber"] for p in uploaded_parts)
    if not uploaded_parts or actual_numbers != expected_numbers:
        raise HTTPException(
            400,
            f"Multipart incompleto: esperadas {len(expected_numbers)} partes, encontradas {len(actual_numbers)}.",
        )

    s3_client.complete_multipart_upload(
        Bucket=bucket,
        Key=req.object_key,
        UploadId=req.upload_id,
        MultipartUpload={
            "Parts": [
                {"PartNumber": p["PartNumber"], "ETag": p["ETag"]}
                for p in sorted(uploaded_parts, key=lambda item: item["PartNumber"])
            ]
        },
    )
    return {"video_url": _build_video_url(bucket, req.object_key), "video_id": req.video_id}


@router.post("/presign-multipart/abort")
async def presign_multipart_abort(
    upload_id: str = Form(...),
    object_key: str = Form(...),
    user_data: dict = Depends(verify_supabase_token),
):
    """Cancela um multipart upload em caso de erro."""
    s3_client, bucket, _ = _get_s3_client()
    if s3_client:
        try:
            s3_client.abort_multipart_upload(Bucket=bucket, Key=object_key, UploadId=upload_id)
        except Exception:
            pass
    return {"status": "aborted"}


@router.post("/upload", response_model=VideoUploadResult)
async def upload_video(
    file: UploadFile = File(...),
    user_data: dict = Depends(verify_supabase_token),
):
    """Upload a video file. Envia para S3/Supabase se configurado, senão salva localmente."""
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Tipo não permitido. Aceitos: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}")

    # Streaming upload — tenta S3 primeiro, fallback para local
    storage = StorageService()
    url, file_size = await storage.save_upload_file_streaming(file, MAX_VIDEO_SIZE)

    video_id = str(uuid.uuid4())
    is_s3 = url.startswith("https://") and "supabase" in url or "s3" in url.lower()

    return VideoUploadResult(
        video_id=video_id,
        video_url=url,
        filename=filename,
        size=file_size,
        storage="s3" if is_s3 else "local",
    )

# URL validation for ffprobe — only allow http/https, block internal IPs
_BLOCKED_HOSTS = re.compile(
    r"^(localhost|127\.|10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.|169\.254\.|0\.0\.0\.0|::1|\[::1\])",
    re.IGNORECASE,
)


def _validate_video_url(url: str) -> str:
    """Valida URL de vídeo — bloqueia file://, IPs internos e SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(400, "URL inválida: apenas http/https permitidos")
    if not parsed.hostname:
        raise HTTPException(400, "URL inválida: hostname ausente")
    if _BLOCKED_HOSTS.match(parsed.hostname):
        raise HTTPException(400, "URL inválida: endereço não permitido")
    return url


def get_processor(db: Session = Depends(get_db)):
    return VideoProcessor(db)


@router.post("/edit", response_model=JobResponse)
async def edit_video(
    request_str: str = Form(..., alias="request"),
    video: Optional[UploadFile] = File(None),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    try:
        request_data = json.loads(request_str)
        request = VideoEditRequest(**request_data)

        if not video and not request.video_url:
            raise HTTPException(400, "Forneça um arquivo de vídeo ou video_url")

        if video and not video.content_type.startswith("video/"):
            raise HTTPException(400, "Arquivo deve ser um vídeo")

        if request.video_url:
            _validate_video_url(request.video_url)

        job = await processor.create_job(request, video)

        process_video_task.apply_async(
            args=[job.id],
            priority=request.priority
        )

        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit video error: {e}", exc_info=True)
        raise HTTPException(500, "Erro ao processar vídeo")


@router.post("/transcribe", response_model=JobResponse)
async def transcribe_video(
    video: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    language: str = Form(None),
    model: str = Form("base"),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    if not video and not video_url:
        raise HTTPException(400, "Forneça um arquivo de vídeo ou video_url")

    if video_url:
        _validate_video_url(video_url)

    request = VideoEditRequest(
        video_url=video_url,
        operations=[
            {
                "type": "transcribe",
                "params": {
                    "language": language,
                    "model": model
                }
            }
        ],
        output_format="mp4"
    )

    job = await processor.create_job(request, video)
    process_video_task.apply_async(args=[job.id], priority=10)

    return JobResponse.from_orm(job)


@router.post("/analyze-profile", response_model=JobResponse)
async def analyze_profile_video(
    video: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    language: str = Form(None),
    model: str = Form("base"),
    profile_name: str = Form(""),
    platform: str = Form("unknown"),
    niche: str = Form(""),
    objective: str = Form("analise de perfil e melhoria de roteiro"),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    """
    Analisa um vídeo de perfil/criador: transcreve e gera diagnóstico de
    posicionamento, padrões de roteiro, pilares e sugestões de próximos vídeos.

    Caminho local/VPS: video upload/url -> transcribe -> analyze_profile -> JSON + review.md.
    """
    if not video and not video_url:
        raise HTTPException(400, "Forneça um arquivo de vídeo ou video_url")

    if video_url:
        _validate_video_url(video_url)

    request = VideoEditRequest(
        video_url=video_url,
        operations=[
            {
                "type": "transcribe",
                "params": {
                    "language": language,
                    "model": model,
                },
            },
            {
                "type": "analyze_profile",
                "params": {
                    "profile_name": profile_name,
                    "platform": platform,
                    "niche": niche,
                    "objective": objective,
                    "output_language": "pt-BR",
                },
            },
        ],
        output_format="mp4",
        priority=9,
    )

    job = await processor.create_job(request, video)
    process_video_task.apply_async(args=[job.id], priority=9)

    return JobResponse.from_orm(job)


@router.get("/status/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    background_tasks: BackgroundTasks,
    processor: VideoProcessor = Depends(get_processor),
    user_data: dict | None = Depends(verify_api_key_or_token),
):
    job = processor.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job não encontrado")

    # Auto-save completed video to library
    if user_data and user_data.get("user_id") and job.status == "completed" and job.download_url:
        background_tasks.add_task(
            _save_completed_video_to_library,
            user_data["user_id"], job.download_url, str(job.id)
        )

    return JobResponse.from_orm(job)


@router.post("/probe")
async def probe_video(
    video_url: str = Form(...),
    api_key: str = Depends(verify_api_key),
):
    """Retorna metadados técnicos de um vídeo via ffprobe."""
    _validate_video_url(video_url)

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                "-select_streams", "v:0",
                video_url
            ],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            logger.warning(f"ffprobe failed for URL: {result.stderr[:200]}")
            raise HTTPException(400, "Não foi possível analisar o vídeo")

        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})

        duration = float(fmt.get("duration", 0))
        size_bytes = int(fmt.get("size", 0))

        fps_raw = stream.get("avg_frame_rate", "30/1")
        try:
            num, den = fps_raw.split("/")
            fps = round(int(num) / max(int(den), 1), 2)
        except Exception:
            fps = 30.0

        return {
            "duration_seconds": round(duration, 2),
            "duration_human": f"{int(duration // 60)}m {int(duration % 60)}s",
            "width": stream.get("width", 0),
            "height": stream.get("height", 0),
            "fps": fps,
            "codec": stream.get("codec_name", "unknown"),
            "estimated_size_mb": round(size_bytes / 1e6, 1),
            "is_long_video": duration > 600,
            "processing_estimate_minutes": round(duration / 60 * 1.5, 1)
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(408, "Timeout ao analisar vídeo")
    except json.JSONDecodeError:
        logger.error("ffprobe output parse error")
        raise HTTPException(500, "Erro ao analisar vídeo")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Probe error: {e}", exc_info=True)
        raise HTTPException(500, "Erro ao analisar vídeo")


@router.post("/detect-highlights", response_model=JobResponse)
async def detect_highlights(
    video: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    window_seconds: float = Form(5.0),
    top_percent: float = Form(30.0),
    max_highlights: int = Form(20),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    """Analisa o áudio de um vídeo e detecta os momentos mais energéticos/virais."""
    if not video and not video_url:
        raise HTTPException(400, "Forneça um arquivo de vídeo ou video_url")

    if video_url:
        _validate_video_url(video_url)

    request = VideoEditRequest(
        video_url=video_url,
        operations=[
            {
                "type": "detect_highlights",
                "params": {
                    "window_seconds": window_seconds,
                    "top_percent": top_percent,
                    "max_highlights": max_highlights
                }
            }
        ],
        output_format="mp4"
    )

    job = await processor.create_job(request, video)
    process_video_task.apply_async(args=[job.id], priority=8)

    return JobResponse.from_orm(job)


@router.post("/extract-clips", response_model=JobResponse)
async def extract_clips(
    video: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    max_clips: int = Form(5),
    min_duration: float = Form(30.0),
    min_energy_score: float = Form(6.0),
    top_percent: float = Form(25.0),
    segments: Optional[str] = Form(None),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    """
    Extrai clips individuais dos melhores momentos de um vídeo (estilo Opus Clip).

    Retorna N vídeos separados, cada um com um highlight.
    - Se 'segments' não for fornecido, detecta automaticamente os melhores momentos.
    - Se 'segments' for fornecido (JSON: [[start, end], ...]), extrai esses trechos.
    """
    if not video and not video_url:
        raise HTTPException(400, "Forneça um arquivo de vídeo ou video_url")

    if video_url:
        _validate_video_url(video_url)

    params = {
        "max_clips": max_clips,
        "min_duration": min_duration,
        "min_energy_score": min_energy_score,
        "top_percent": top_percent,
        "padding": 0.5,
    }

    if segments:
        import json as json_mod
        try:
            params["segments"] = json_mod.loads(segments)
        except Exception:
            raise HTTPException(400, "segments deve ser um JSON válido: [[start, end], ...]")
    else:
        params["auto_detect"] = True

    request = VideoEditRequest(
        video_url=video_url,
        operations=[
            {
                "type": "extract_clips",
                "params": params
            }
        ],
        output_format="mp4"
    )

    job = await processor.create_job(request, video)
    process_video_task.apply_async(args=[job.id], priority=8)

    return JobResponse.from_orm(job)


# ─── Scene Plan API (for review screen) ──────────────────────────────────────


class ScenePlanRequest(BaseModel):
    video_url: str
    words: Optional[List[Dict[str, Any]]] = None
    provider: str = "auto"
    custom_prompt: str = ""
    fps: int = 30


@router.post("/plan-scenes", response_model=JobResponse)
async def create_scene_plan(
    request: ScenePlanRequest,
    processor: VideoProcessor = Depends(get_processor),
    auth: str = Depends(verify_api_key_or_token),
):
    """
    Transcribes the video and generates a scene plan as a background job.
    Returns a job_id — poll /status/{job_id} for the result.
    The final download_url will be a JSON with the scene plan + words.
    """
    if not request.video_url:
        raise HTTPException(400, "video_url is required")

    # Build pipeline: transcribe → plan_scenes
    operations = [
        {"type": "transcribe", "params": {"word_timestamps": True, "language": None}},
        {"type": "plan_scenes", "params": {
            "provider": request.provider,
            "custom_prompt": request.custom_prompt,
            "fps": request.fps,
        }},
    ]

    edit_request = VideoEditRequest(
        video_url=request.video_url,
        operations=operations,
        output_format="mp4",
        priority=8,
    )

    job = await processor.create_job(edit_request)
    process_video_task.apply_async(args=[job.id], priority=8)

    return JobResponse.from_orm(job)


@router.post("/render-with-scenes", response_model=JobResponse)
async def render_with_scenes(
    video_url: str = Form(...),
    scenes: str = Form(...),
    palette: str = Form("{}"),
    mode: str = Form("viral"),
    subtitles_config: str = Form("{}"),
    branding_config: str = Form("{}"),
    text_overlays: str = Form("[]"),
    b_rolls: str = Form("[]"),
    hook_visuals: str = Form("[]"),
    processor: VideoProcessor = Depends(get_processor),
    api_key: str = Depends(verify_api_key),
):
    """
    Renders a video with a reviewed/edited scene plan.
    Use after /plan-scenes and user review.
    """
    import json as json_mod

    try:
        scenes_data = json_mod.loads(scenes)
        palette_data = json_mod.loads(palette)
        subtitles_data = json_mod.loads(subtitles_config)
        branding_data = json_mod.loads(branding_config)
        text_overlays_data = json_mod.loads(text_overlays)
        b_rolls_data = json_mod.loads(b_rolls)
        hook_visuals_data = json_mod.loads(hook_visuals)
    except Exception:
        raise HTTPException(400, "Invalid JSON in render payload")

    render_params = {
        "mode": mode,
        "scenes": scenes_data,
        "palette": palette_data,
        "quality": "high",
    }
    if subtitles_data:
        render_params["subtitles"] = subtitles_data
    if branding_data:
        render_params["branding"] = branding_data
    if text_overlays_data:
        render_params["textOverlays"] = text_overlays_data
    if b_rolls_data:
        render_params["bRolls"] = b_rolls_data
    if hook_visuals_data:
        render_params["hookVisuals"] = hook_visuals_data

    edit_request = VideoEditRequest(
        video_url=video_url,
        operations=[
            {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
            {"type": "remove_silence", "params": {"threshold": -40, "padding": 0.3, "min_silence_duration": 1.0}},
            {"type": "remotion_render", "params": render_params},
        ],
        output_format="mp4",
        priority=7,
    )

    job = await processor.create_job(edit_request)
    process_video_task.apply_async(args=[job.id], priority=7)

    return JobResponse.from_orm(job)


# ─── Render Template (video from scratch, no source video) ────────────────────


class RenderTemplateRequest(BaseModel):
    template: str = "listicle"  # listicle, quote, cta, stats, comparison, steps
    format: str = "9:16"        # 9:16, 1:1, 16:9
    title: str
    subtitle: Optional[str] = ""
    items: Optional[List[str]] = []
    items_right: Optional[List[str]] = []
    stat_number: Optional[str] = ""
    stat_label: Optional[str] = ""
    cta_text: Optional[str] = "Saiba Mais"
    author: Optional[str] = ""
    accent_color: Optional[str] = "#A3F12E"
    bg_color: Optional[str] = "#0a0a0a"
    text_color: Optional[str] = "#FFFFFF"
    quality: Optional[str] = "high"


@router.post("/render-template")
async def render_template(
    request: RenderTemplateRequest,
    user_data: dict | None = Depends(verify_api_key_or_token),
):
    """
    Renders an animated video from scratch using Remotion templates.
    No source video needed — generates motion graphics from text/data.

    Templates: listicle, quote, cta, stats, comparison, steps
    Formats: 9:16 (Reels), 1:1 (Feed), 16:9 (YouTube)
    """
    import httpx

    remotion_url = os.getenv("REMOTION_SERVICE_URL", "http://localhost:8003")

    # Check Remotion availability
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            health = await client.get(f"{remotion_url}/health")
            if health.status_code != 200:
                raise HTTPException(503, "Remotion service not available")
    except Exception:
        raise HTTPException(503, "Remotion service not reachable")

    # Send to Remotion render-template endpoint
    payload = {
        "template": request.template,
        "format": request.format,
        "quality": request.quality,
        "title": request.title,
        "subtitle": request.subtitle or "",
        "items": request.items or [],
        "itemsRight": request.items_right or [],
        "statNumber": request.stat_number or "",
        "statLabel": request.stat_label or "",
        "ctaText": request.cta_text or "Saiba Mais",
        "author": request.author or "",
        "accentColor": request.accent_color or "#A3F12E",
        "bgColor": request.bg_color or "#0a0a0a",
        "textColor": request.text_color or "#FFFFFF",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{remotion_url}/render-template", json=payload)
        if resp.status_code != 200:
            raise HTTPException(500, f"Remotion render-template failed: {resp.text}")
        job_data = resp.json()

    # Poll for completion and return result
    job_id = job_data.get("id")
    public_url = os.getenv("PUBLIC_API_URL", "").rstrip("/")

    import asyncio
    for _ in range(120):  # max 10 min
        await asyncio.sleep(5)
        async with httpx.AsyncClient(timeout=10) as client:
            status_resp = await client.get(f"{remotion_url}/status/{job_id}")
            status = status_resp.json()

        if status.get("status") == "completed":
            output_url = status.get("outputUrl", "")
            # Download from Remotion and save to our storage
            async with httpx.AsyncClient(timeout=120) as client:
                dl_resp = await client.get(f"{remotion_url}{output_url}")
                if dl_resp.status_code == 200:
                    from app.core.storage import STORAGE_PATH
                    final_filename = f"template_{job_id}.mp4"
                    final_path = os.path.join(str(STORAGE_PATH), final_filename)
                    with open(final_path, "wb") as f:
                        f.write(dl_resp.content)

                    download_url = f"{public_url}/static/{final_filename}" if public_url else f"/static/{final_filename}"
                    return {
                        "status": "completed",
                        "download_url": download_url,
                        "template": request.template,
                        "format": request.format,
                    }

            return {"status": "completed", "download_url": f"{remotion_url}{output_url}"}

        if status.get("status") == "failed":
            raise HTTPException(500, f"Render failed: {status.get('error', 'unknown')}")

    raise HTTPException(504, "Render timed out")
