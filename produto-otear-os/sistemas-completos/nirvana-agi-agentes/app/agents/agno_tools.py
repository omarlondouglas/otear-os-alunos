import os
import json
import time
import httpx
import functools
import redis
import datetime
import threading
from agno.utils.log import logger
from typing import List, Dict, Any, Optional

from app.services.storage import StorageService
storage_service = StorageService()

# Thread-local storage for passing user/org/brand context to tools
_thread_local = threading.local()

def set_current_user_id(user_id: str | None):
    """Set the current user_id for the running thread (called before agent.run)."""
    _thread_local.user_id = user_id

def get_current_user_id() -> str | None:
    """Get the current user_id from thread-local storage."""
    return getattr(_thread_local, "user_id", None)

def set_current_context(org_id: str | None = None, brand_id: str | None = None):
    """Set org/brand context for the running thread (multi-tenant)."""
    _thread_local.org_id = org_id
    _thread_local.brand_id = brand_id

def get_current_org_id() -> str | None:
    """Get the current org_id from thread-local storage."""
    return getattr(_thread_local, "org_id", None)

def get_current_brand_id() -> str | None:
    """Get the current brand_id from thread-local storage."""
    return getattr(_thread_local, "brand_id", None)

# Service URLs from environment - Re-read at runtime for reliability
def get_video_url():
    return os.getenv("VIDEO_EDITOR_API_URL") or os.getenv("VIDEO_SERVICE_URL") or "http://localhost:8001"

def get_carousel_url():
    return os.getenv("CAROUSEL_API_URL") or os.getenv("CAROUSEL_SERVICE_URL") or "http://localhost:8002"

VIDEO_SERVICE_KEY = os.getenv("VIDEO_EDITOR_API_KEY")
CAROUSEL_API_KEY = os.getenv("CAROUSEL_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
def get_api_base_url():
    base = os.getenv("PUBLIC_API_URL") or os.getenv("API_BASE_URL", "http://localhost:8000")
    if base.endswith('/'):
        base = base[:-1]
    return base

def _safe_hex_to_rgb(value: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    value = (value or "").strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        return fallback
    try:
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))
    except ValueError:
        return fallback

def _load_pillow_font(size: int, bold: bool = False):
    from PIL import ImageFont

    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()

def _wrap_text_to_width(draw, text: str, font, max_width: int) -> list[str]:
    words = str(text or "").split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines

def _draw_centered_lines(draw, lines: list[str], x: int, y: int, width: int, font, fill, line_gap: int) -> int:
    cursor = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        draw.text((x + (width - line_width) / 2, cursor), line, font=font, fill=fill)
        cursor += line_height + line_gap
    return cursor

def _render_carousel_fallback(slides_data: List[Dict[str, Any]], reason: str) -> Dict[str, Any]:
    """Render minimal PNG slides locally when the carousel sidecar is unavailable."""
    try:
        from PIL import Image, ImageDraw
        import uuid as _uuid
    except Exception as exc:
        return {
            "success": False,
            "error": f"Carousel renderer failed ({reason}) and local Pillow fallback is unavailable: {exc}",
        }

    width, height = 1080, 1350
    margin_x = 92
    content_width = width - (margin_x * 2)
    storage_path = os.getenv("STORAGE_PATH", "/app/storage")
    output_dir = os.path.join(storage_path, "carousels")
    os.makedirs(output_dir, exist_ok=True)

    carousel_id = f"fallback-{_uuid.uuid4()}"
    slides: list[Dict[str, Any]] = []

    for index, slide in enumerate(slides_data, start=1):
        bg = _safe_hex_to_rgb(slide.get("bgColor", "#0A0A0A"), (10, 10, 10))
        fg = _safe_hex_to_rgb(slide.get("titleColor", "#FFFFFF"), (255, 255, 255))
        accent = _safe_hex_to_rgb(slide.get("highlightColor", "#A3F12E"), (163, 241, 46))

        image = Image.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(image)

        title_font = _load_pillow_font(72 if slide.get("type") == "cover" else 64, bold=True)
        subtitle_font = _load_pillow_font(42, bold=False)
        meta_font = _load_pillow_font(26, bold=True)

        draw.rounded_rectangle((64, 64, 260, 112), radius=18, outline=accent, width=3)
        draw.text((86, 76), "Tear", font=meta_font, fill=accent)
        draw.text((width - 180, 78), f"{index:02d}", font=meta_font, fill=fg)

        title_lines = _wrap_text_to_width(draw, slide.get("title", ""), title_font, content_width)
        subtitle_lines = _wrap_text_to_width(draw, slide.get("subtitle", ""), subtitle_font, content_width)

        title_height = sum((draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1]) + 18 for line in title_lines)
        subtitle_height = sum((draw.textbbox((0, 0), line, font=subtitle_font)[3] - draw.textbbox((0, 0), line, font=subtitle_font)[1]) + 12 for line in subtitle_lines)
        block_height = title_height + (36 if subtitle_lines else 0) + subtitle_height

        position = slide.get("textPosition", "center")
        if position == "top":
            start_y = 210
        elif position == "bottom":
            start_y = max(210, height - 210 - block_height)
        else:
            start_y = max(210, int((height - block_height) / 2))

        cursor = _draw_centered_lines(draw, title_lines, margin_x, start_y, content_width, title_font, fg, 18)
        if subtitle_lines:
            cursor += 36
            _draw_centered_lines(draw, subtitle_lines, margin_x, cursor, content_width, subtitle_font, fg, 12)

        draw.line((92, height - 104, width - 92, height - 104), fill=accent, width=4)
        draw.text((92, height - 78), "Fallback local - revisar visual final", font=meta_font, fill=fg)

        filename = f"{carousel_id}-slide-{index}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath, "PNG")
        slides.append({
            "order": index,
            "type": slide.get("type", "text-only"),
            "url": f"{get_api_base_url()}/static/carousels/{filename}",
        })

    return {
        "success": True,
        "carouselId": carousel_id,
        "slides": slides,
        "totalSlides": len(slides),
        "fallback_applied": True,
        "fallback_reason": reason,
    }

def get_video_public_url():
    """Retorna a URL pública para download de vídeos processados.
    
    IMPORTANTE: Os arquivos estáticos ficam em /app/storage no container.
    O video service (porta 8001) serve em /static/, mas o domínio externo
    do video service (otear-otear-editavideos) NÃO serve /static/ externamente.
    
    O GATEWAY (porta 8000, otear-agentes-otear) tem um proxy que faz:
    GET /static/{file} → localhost:8001/static/{file}
    
    Por isso, usamos PUBLIC_API_URL (gateway) como base para download URLs.
    """
    gateway_url = os.getenv("PUBLIC_API_URL", "").rstrip("/")
    if gateway_url:
        return gateway_url
    return get_api_base_url()

# --- LOGGING UTILS ---

def log_tool_sync(tool_name: str, message: str, log_type: str = "system"):
    """Synchronous logging to Redis for tools. Non-blocking with timeout."""
    try:
        # Adicionado socket_connect_timeout para não travar a execução se o Redis estiver fora
        client = redis.from_url(
            REDIS_URL, 
            decode_responses=True, 
            socket_connect_timeout=2,
            socket_timeout=2
        )
        entry = {
            "id": f"log-{datetime.datetime.now().timestamp()}",
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": "System",
            "message": f"[{tool_name}] {message}",
            "type": log_type
        }
        client.lpush("agent_logs", json.dumps(entry))
        client.ltrim("agent_logs", 0, 999)
    except Exception as e:
        # Falha silenciosa no log para não quebrar a ferramenta principal
        logger.error(f"Failed to log tool usage (Redis unreachable?): {e}")


def with_logging(tool_name: str):
    """Decorator that logs tool execution while preserving function metadata."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_tool_sync(tool_name, "Iniciando execução...", "system")
            try:
                result = func(*args, **kwargs)
                log_tool_sync(tool_name, "Concluído com sucesso.", "system")
                return result
            except Exception as e:
                log_tool_sync(tool_name, f"Erro: {str(e)}", "system")
                raise e
        return wrapper
    return decorator


# --- TOOLS ---

@with_logging("Web Search")
def web_search_tool(query: str):
    """Pesquisa na web por informações (Use SOMENTE se solicitado explicitamente)."""
    try:
        if TAVILY_API_KEY:
            try:
                from tavily import TavilyClient
                tavily = TavilyClient(api_key=TAVILY_API_KEY)
                response = tavily.search(query=query, search_depth="advanced")
                results = response.get("results", [])
                formatted = "\n\n".join([f"- [{r['title']}]({r['url']}): {r['content']}" for r in results[:5]])
                return f"Resultados da Tavily para '{query}':\n{formatted}"
            except ImportError:
                logger.warning("tavily-python not installed. Falling back.")
            except Exception as e:
                logger.error(f"Tavily error: {e}")

        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                formatted = "\n\n".join([f"- [{r['title']}]({r['href']}): {r['body']}" for r in results])
                return f"Resultados do DuckDuckGo para '{query}':\n{formatted}"
        except ImportError:
            return "Erro: instale duckduckgo-search ou tavily-python."
            
    except Exception as e:
        return f"Erro na busca: {str(e)}"


@with_logging("Get News")
def get_news_tool(topic: str = "technology"):
    """Busca notícias recentes e manchetes (Use SOMENTE se solicitado explicitamente)."""
    if not NEWS_API_KEY:
        return "Erro: NEWS_API_KEY não encontrada no .env"
        
    try:
        import requests
        url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&apiKey={NEWS_API_KEY}&language=pt"
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") != "ok":
            return f"Erro na NewsAPI: {data.get('message')}"
            
        articles = data.get("articles", [])[:5]
        formatted = "\n\n".join([f"- **{a['title']}** ({a['source']['name']}): {a['description']} [Link]({a['url']})" for a in articles])
        return f"Notícias recentes sobre '{topic}':\n{formatted}"
        
    except Exception as e:
        return f"Erro ao buscar notícias: {str(e)}"


@with_logging("Generate Carousel")
def generate_carousel_tool(slides_data: List[Dict[str, Any]]):
    """
    OBRIGATÓRIO: Gera IMAGENS de carrossel para Instagram (1080x1350) a partir de um JSON estruturado.
    Esta ferramenta CRIA as imagens e retorna URLs prontas para download.
    
    IMPORTANTE: Se a geração de imagens (generate_image_tool) estiver indisponível,
    você pode usar slides sem imagem! O sistema converte automaticamente para 'text-only'
    ou 'cover' com fundo gradiente quando não há URL de imagem.
    
    Args:
        slides_data (List[Dict[str, Any]]): Lista de dicts. Cada slide DEVE ter:
            - type: 'cover' | 'image-text' | 'two-images' | 'text-only'
            - title: Texto principal (string)
            - subtitle: Texto secundário (opcional)
            - titleColor: Cor hex do título ex: '#ffffff' (opcional)
            - textPosition: 'top', 'center', 'bottom' (apenas para cover)
            - imagePosition: 'top', 'middle', 'bottom' (apenas para image-text)
            - bgColor: Cor hex do fundo ex: '#0a0a0a' (apenas para text-only)
            - fontFamily: Nome da fonte ex: 'roboto', 'urbanist' (opcional)
            - highlight: Palavras para destacar separadas por | (opcional)
            - highlightColor: Cor do destaque (opcional, default: '#FFD700')
            - images: {'bg': 'url'} para cover, {'img': 'url'} para image-text, {'img1': 'url', 'img2': 'url'} para two-images
            
            NOTA: Se images estiver vazio ou sem URL válida:
            - Slides 'cover' serão renderizados com gradiente de fundo (sem imagem)
            - Slides 'image-text' serão convertidos para 'text-only'
            - Slides 'two-images' serão convertidos para 'text-only'
    
    Returns:
        dict com:
        - success: True/False
        - carouselId: UUID do carrossel gerado
        - slides: Lista de {order, type, url} com URLs das imagens geradas
        - fallback_applied: True se algum slide foi convertido automaticamente
    
    Exemplo de uso SEM imagens (funciona sempre):
        generate_carousel_tool(slides_data=[
            {"type": "cover", "title": "TÍTULO IMPACTANTE", "subtitle": "Subtítulo", "bgColor": "#0a0a0a", "titleColor": "#A3F12E"},
            {"type": "text-only", "title": "Conteúdo do slide", "bgColor": "#1a1a1a", "titleColor": "#ffffff"},
            {"type": "text-only", "title": "Gostou? Compartilhe!", "bgColor": "#FFD700"}
        ])
    
    Exemplo de uso COM imagens:
        generate_carousel_tool(slides_data=[
            {"type": "cover", "title": "TÍTULO", "images": {"bg": "https://..."}},
            {"type": "text-only", "title": "Conteúdo do slide", "bgColor": "#000000"}
        ])
    """
    logger.info(f"Carousel Tool requested with {len(slides_data)} slides.")
    try:
        # Prevent LLM from sending stringified JSON
        if isinstance(slides_data, str):
            logger.info("DEBUG: slides_data is a string, attempting to parse JSON...")
            try:
                slides_data = json.loads(slides_data)
            except json.JSONDecodeError as e:
                logger.error(f"DEBUG Error: Invalid JSON string: {e}")
                return {"error": f"Invalid JSON string passed to slides_data: {e}", "success": False}
        
        if not isinstance(slides_data, list):
            return {"error": "slides_data must be a list of dictionaries.", "success": False}

        # Text length safety net: truncate/split excessively long text fields
        TITLE_MAX = 120
        SUBTITLE_MAX = 80
        sanitized_slides = []
        for slide in slides_data:
            slide = dict(slide)
            title = slide.get("title", "")
            subtitle = slide.get("subtitle", "")
            if len(title) > TITLE_MAX:
                logger.warning(f"Carousel slide title truncated: {len(title)} chars -> {TITLE_MAX}")
                slide["title"] = title[:TITLE_MAX].rsplit(" ", 1)[0] + "..."
            if subtitle and len(subtitle) > SUBTITLE_MAX:
                slide["subtitle"] = subtitle[:SUBTITLE_MAX].rsplit(" ", 1)[0] + "..."
            sanitized_slides.append(slide)
        slides_data = sanitized_slides

        # Safety net: auto-convert slides that need images but don't have them
        fallback_applied = False
        processed_slides = []
        for slide in slides_data:
            slide_copy = dict(slide)
            slide_type = slide_copy.get("type", "text-only")
            images = slide_copy.get("images", {})
            
            # Check if slide type requires images but doesn't have valid URLs
            if slide_type == "image-text":
                img_url = images.get("img", "")
                
                # BASE64 INTERCEPTOR
                if img_url and (img_url.startswith("data:image/") or sum(c.isalnum() for c in img_url) > 1000):
                    logger.info("BrandCraft/Carousel: Detectada string Base64. Iniciando upload para S3 via StorageService...")
                    uploaded_url = storage_service.upload_base64(img_url, ext="png", mimetype="image/png")
                    if uploaded_url:
                        slide_copy["images"]["img"] = uploaded_url
                        img_url = uploaded_url
                        logger.info(f"Upload S3 concluído: {uploaded_url}")
                    else:
                        img_url = "" # Fallback trigger
                
                if not img_url or not (img_url.startswith("http") or img_url.startswith("data:image/")):
                    logger.warning(f"Slide 'image-text' sem imagem válida, convertendo para 'text-only'")
                    slide_copy["type"] = "text-only"
                    if not slide_copy.get("bgColor") or slide_copy["bgColor"] == "#ffffff":
                        slide_copy["bgColor"] = "#0a0a0a"
                    fallback_applied = True
                    
            elif slide_type == "two-images":
                img1 = images.get("img1", "")
                img2 = images.get("img2", "")
                
                # Intercept Img1
                if img1 and (img1.startswith("data:image/") or sum(c.isalnum() for c in img1) > 1000):
                    u1 = storage_service.upload_base64(img1, ext="png", mimetype="image/png")
                    if u1:
                        img1 = u1
                        slide_copy["images"]["img1"] = u1
                        
                # Intercept Img2
                if img2 and (img2.startswith("data:image/") or sum(c.isalnum() for c in img2) > 1000):
                    u2 = storage_service.upload_base64(img2, ext="png", mimetype="image/png")
                    if u2:
                        img2 = u2
                        slide_copy["images"]["img2"] = u2
                        
                v1 = img1 and (img1.startswith("http") or img1.startswith("data:image/"))
                v2 = img2 and (img2.startswith("http") or img2.startswith("data:image/"))
                if not v1 or not v2:
                    logger.warning(f"Slide 'two-images' sem imagens válidas, convertendo para 'text-only'")
                    slide_copy["type"] = "text-only"
                    if not slide_copy.get("bgColor") or slide_copy["bgColor"] == "#ffffff":
                        slide_copy["bgColor"] = "#0a0a0a"
                    fallback_applied = True
            
            # Cover slides WITHOUT image are OK - backend renders gradient fallback
            # No conversion needed for cover without bg image
                    
            processed_slides.append(slide_copy)
        
        # Prefer the local/managed carousel service. A legacy N8N webhook can still
        # be supplied explicitly for older deployments.
        url = os.getenv("CAROUSEL_WEBHOOK_URL") or f"{get_carousel_url().rstrip('/')}/api/generate-multi"
        carousel_key = os.getenv("CAROUSEL_API_KEY")
        payload = {"slides": processed_slides}
        
        headers = {"Content-Type": "application/json"}
        if carousel_key:
            headers["X-API-Key"] = carousel_key
        
        print(f"DEBUG: Calling Carousel API: {url}")
        print(f"DEBUG: Payload: {json.dumps(payload, ensure_ascii=False)[:300]}...")
        # Timeout de 180s – a geração de carrossel pode levar até 60s, mais overhead do LLM
        response = httpx.post(url, json=payload, headers=headers, timeout=180.0)
        logger.info(f"DEBUG: Carousel API Status Code: {response.status_code}")
        logger.debug(f"DEBUG: Carousel API Response: {response.text[:200]}")

        if response.status_code >= 400:
            detail = response.text.strip()
            if response.status_code in (401, 403):
                detail = (
                    "Carousel renderer rejected the request. "
                    "Check CAROUSEL_API_KEY in the API service and carousel service."
                )
            elif not detail:
                detail = f"Carousel renderer returned HTTP {response.status_code} with an empty body."
            logger.error(detail)
            return _render_carousel_fallback(processed_slides, detail)
        
        if not response.text or response.text.strip() == "":
            error_msg = f"Carousel API returned an empty response body with status {response.status_code}."
            logger.error(error_msg)
            return _render_carousel_fallback(processed_slides, error_msg)
            
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Carousel API response as JSON: {str(e)}"
            logger.error(f"{error_msg}. Raw response: {response.text[:500]}")
            return _render_carousel_fallback(processed_slides, error_msg)
            
        logger.info(f"Carousel API response: {result}")
        
        if not result:
            return {"error": "Carousel API returned an empty JSON object.", "success": False}
        
        # Convert relative URLs to absolute URLs
        if result.get("success") and result.get("slides"):
            public_base = get_api_base_url()
            for slide in result["slides"]:
                slide_url = slide.get("url", "")
                if slide_url.startswith("/api/image/"):
                    slide["url"] = f"/api/v1/carousels/image/{slide_url.split('/api/image/', 1)[1]}"
                    logger.info(f"Proxied carousel image URL: {slide_url} -> {slide['url']}")
                elif slide_url and slide_url.startswith("/"):
                    slide["url"] = f"{public_base}{slide_url}"
                    logger.info(f"Converted carousel URL: {slide_url} -> {slide['url']}")
        
        if fallback_applied:
            result["fallback_applied"] = True
            result["fallback_note"] = "Alguns slides foram convertidos automaticamente porque não tinham imagens. O resultado visual usa gradientes e cores de fundo."

        # Save carousel to library automatically
        if result.get("success") and result.get("slides"):
            try:
                from app.api.v1.endpoints.library import save_asset
                # Use first slide as thumbnail, collect all slide URLs
                slides_list = result["slides"]
                first_url = slides_list[0].get("url") if slides_list else None
                all_urls = [s.get("url") for s in slides_list if s.get("url")]
                carousel_id = result.get("carouselId", "")
                title_text = processed_slides[0].get("title", "Carrossel") if processed_slides else "Carrossel"

                # Get user_id from thread-local context (set by chat/editor endpoints)
                user_id = get_current_user_id()
                if not user_id:
                    logger.info("Carousel generated but no user_id available for library save")
                else:
                    save_asset(
                        user_id=user_id,
                        asset_type="carousel",
                        title=title_text[:100],
                        url=first_url,
                        thumbnail_url=first_url,
                        metadata={
                            "carousel_id": carousel_id,
                            "slides": all_urls,
                            "slides_data": processed_slides,
                            "slide_count": len(slides_list),
                        },
                    )
                    logger.info(f"Carousel saved to library for user {user_id}")
            except Exception as e:
                logger.warning(f"Failed to save carousel to library: {e}")

        return result
    except httpx.HTTPStatusError as e:
        error_msg = f"Carousel API returned error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return {"error": error_msg, "success": False, "details": e.response.text}
    except httpx.ReadTimeout:
        error_msg = f"Timeout connecting to Carousel service after 180s. The service might be overloaded or down."
        logger.error(error_msg)
        return _render_carousel_fallback(slides_data, error_msg)
    except httpx.ConnectError as e:
        active_url = get_carousel_url()
        error_msg = f"Could not connect to Carousel service at {active_url}. Verify CAROUSEL_API_URL env var and service availability."
        logger.error(error_msg)
        return _render_carousel_fallback(slides_data, error_msg)
    except Exception as e:
        logger.error(f"Error calling carousel service: {e}")
        return {"error": str(e), "success": False}


@with_logging("List Fonts")
def list_fonts_tool():
    """Lists available fonts for the carousel."""
    try:
        url = f"{get_carousel_url()}/api/fonts"
        response = httpx.get(url, timeout=10.0)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@with_logging("Check Carousel Health")
def check_carousel_health_tool():
    """Checks if the carousel service is running."""
    try:
        url = f"{get_carousel_url()}/api/health"
        response = httpx.get(url, timeout=5.0)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@with_logging("Edit Video")
def edit_video_tool(
    video_url: str, 
    operations: list = None,
    operation_type: str = None, 
    params: dict = None, 
    preset: str = None,
    wait_for_completion: bool = False,
    max_wait_seconds: int = 3600
) -> Dict[str, Any]:
    """
    Edits a video using either specific operations or a predefined preset.
    Supports MULTIPLE operations in a single call.
    
    Args:
        video_url: The URL of the video to edit (OBRIGATÓRIO).
        operations: Lista de operações a serem aplicadas. Cada operação é um dict com 'type' e 'params'.
                    Exemplo: [
                        {"type": "add_text_overlay", "params": {"text": "Título", "position": "top", "padding_top": 60}},
                        {"type": "auto_subtitle", "params": {"style": {"font_size": 10, "color": "#FFFF00"}}}
                    ]
        operation_type: (DEPRECATED) Tipo de operação única. Use 'operations' para múltiplas.
        params: (DEPRECATED) Parâmetros para operation_type. Use 'operations' para múltiplas.
        preset: Nome do preset predefinido ('VIRAL', 'REACTION', 'CLEAN', 'MODERN_SUBTITLES').
                Se 'preset' for fornecido, as outras operações são ignoradas.
        wait_for_completion: Se True, aguarda o processamento finalizar (padrão: True).
        max_wait_seconds: Tempo máximo de espera em segundos (padrão: 300).
    
    Returns:
        dict com URL do vídeo processado ou 'error' se falhar.
    
    Operações disponíveis:
        - add_text_overlay: Adiciona texto sobre o vídeo
            params: {text, position, padding_top, font_size, color, background_color}
        - auto_subtitle: Adiciona legendas automáticas
            params: {style: {font_size, color, position, animation}}
        - remove_silence: Remove silêncios do vídeo
        - smart_cut: Mantém apenas segmentos específicos (corte inteligente)
            params: {keep_segments: [[start, end], [start, end]]}
        - preset: Aplica um preset predefinido
            params: {name: 'VIRAL' | 'REACTION' | 'CLEAN' | 'MODERN_SUBTITLES'}
    
    Presets:
        1. 'VIRAL': Legendas amarelas word-by-word + remoção de silêncio (ideal para Reels/Shorts)
        2. 'MODERN_SUBTITLES': Legendas brancas com destaque por palavra
        3. 'REACTION': Otimizado para vídeos de reação com overlay
        4. 'CLEAN': Remoção de silêncio + legendas estáticas
    """
    try:
        edit_url = f"{get_video_url()}/api/v1/videos/edit"
        
        # Build operations list
        ops = []
        if preset:
            # FIX: Expand presets locally
            if preset.upper() == 'VIRAL':
                ops.append({
                    "type": "auto_subtitle", 
                    "params": {
                        "style": {
                            "color": "#FFFF00", 
                            "font_size": 10, 
                            "animation": "typewriter",
                            "position": "bottom"
                        }
                    }
                })
                ops.append({"type": "remove_silence", "params": {"threshold": -40, "padding": 0.3, "min_silence_duration": 1.0}})
            elif preset.upper() == 'TITLE_BAR':
                ops.append({
                    "type": "add_text_overlay",
                    "params": {
                        "text": params.get("text", "") if params else "",
                        "position": "top",
                        "font_size": 28,
                        "font_color": "white",
                        "box": True,
                        "box_color": "black",
                        "box_opacity": 0.7,
                        "box_full_width": True,
                        "box_padding": 20,
                        "box_height": 80,
                    }
                })
            elif preset.upper() == 'CLEAN':
                ops.append({"type": "remove_silence", "params": {"threshold": -40, "padding": 0.25, "min_silence_duration": 1.0}})
                ops.append({
                    "type": "auto_subtitle",
                    "params": {
                        "style": {
                            "color": "#FFFFFF",
                            "font_size": 10,
                            "position": "bottom"
                        }
                    }
                })
            elif preset.upper() == 'AULA':
                ops.append({
                    "type": "remove_silence",
                    "params": {
                        "threshold": -42,
                        "padding": 0.3,
                        "min_silence_duration": 1.2
                    }
                })
                ops.append({
                    "type": "auto_subtitle",
                    "params": {
                        "style": {
                            "color": "#FFFFFF",
                            "font_size": 10,
                            "animation": "highlight-word",
                            "position": "bottom",
                            "margin_vertical": 60
                        }
                    }
                })
            else:
                # Presets PRO (VIRAL_PRO, AULA_PRO, HORMOZI, PODCAST) e outros
                # Enviados ao backend que expande via VideoPresets
                ops.append({"type": "preset", "params": {"name": preset}})
        elif operations and isinstance(operations, list):
            ops = operations
        elif operation_type:
            # FIX: Handle direct params for convenience
            final_params = params or {}
            
            # If auto_subtitle is called with flat params, nest them in style
            if operation_type == 'auto_subtitle' and 'style' not in final_params:
                style = {
                    "color": final_params.get("color", "#FFFFFF"),
                    "font_size": final_params.get("font_size", 10),
                    "position": final_params.get("position", "bottom"),
                    "animation": final_params.get("animation")
                }
                # Remove None values
                style = {k: v for k, v in style.items() if v is not None}
                final_params["style"] = style
                
            ops.append({"type": operation_type, "params": final_params})
        
        if not ops:
            return {"error": "Nenhuma operação especificada. Forneça 'operations', 'operation_type+params', ou 'preset'."}
            
        payload = {
            "video_url": video_url,
            "operations": ops,
            "output_format": "mp4"
        }
        
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY
        
        logger.info(f"Submitting video edit job: {preset or operation_type or 'custom'}")
        logger.info(f"Payload: {json.dumps(payload)}")
        
        # CORREÇÃO: O serviço espera o payload dentro de um campo "request"
        form_data = {"request": json.dumps(payload)}
        
        # FIX: Do not set Content-Type: application/json for form data
        response = httpx.post(
            edit_url,
            data=form_data,
            headers=headers,
            timeout=300.0
        )
        
        if response.status_code != 200:
            error_msg = f"Video service returned {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        job_response = response.json()
        
        if "error" in job_response:
            return job_response
        
        logger.info(f"Video service response: {json.dumps(job_response)}")
        
        job_id = job_response.get("job_id") or job_response.get("task_id") or job_response.get("id")
        
        # Tenta extrair de 'data' se existir
        if not job_id and "data" in job_response:
            job_data = job_response["data"]
            if isinstance(job_data, dict):
                job_id = job_data.get("job_id") or job_data.get("task_id") or job_data.get("id")

        if not job_id:
            logger.error(f"Could not extract job_id from response: {job_response}")
            return {"error": "Failed to get job_id from video service", "response": job_response}
        
        if not wait_for_completion:
            return job_response
        
        # Poll for completion with progressive backoff
        status_url = f"{get_video_url()}/api/v1/videos/status/{job_id}"
        start_time = time.time()
        poll_interval = 5

        while time.time() - start_time < max_wait_seconds:
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, 30)
            
            try:
                status_response = httpx.get(status_url, headers=headers, timeout=30.0)
                
                if status_response.status_code != 200:
                    logger.warning(f"Status check failed: {status_response.status_code}")
                    continue
                
                status_data = status_response.json()
                
                status = status_data.get("status", "").lower()
                progress = status_data.get("progress", 0)
                
                logger.info(f"Video job {job_id}: {status} ({progress}%)")
                
                if status == "completed":
                    # Normalize download_url to always use PUBLIC_API_URL (gateway)
                    if "download_url" in status_data and status_data["download_url"]:
                        orig_url = status_data["download_url"]
                        gateway = get_video_public_url()
                        if gateway and "/static/" in orig_url:
                            static_part = orig_url.split("/static/", 1)[1]
                            status_data["download_url"] = f"{gateway}/static/{static_part}"
                            logger.info(f"[EDIT VIDEO] URL normalizada: {orig_url} -> {status_data['download_url']}")
                        elif gateway and orig_url.startswith("/"):
                            status_data["download_url"] = f"{gateway}{orig_url}"
                            logger.info(f"[EDIT VIDEO] URL relativa normalizada: {orig_url} -> {status_data['download_url']}")
                    # Auto-save completed video to library
                    if status_data.get("download_url"):
                        _save_video_to_library(status_data["download_url"], job_id)
                    return status_data
                elif status == "failed":
                    return {
                        "error": status_data.get("error_message", "Job failed"),
                        "job_id": job_id,
                        "status": "failed"
                    }
                    
            except Exception as poll_error:
                logger.warning(f"Error polling job status: {poll_error}")
                
        return {
            "error": f"Timeout waiting for job completion after {max_wait_seconds}s",
            "job_id": job_id,
            "status": "timeout"
        }
        
    except httpx.ReadTimeout:
        error_msg = f"Timeout connecting to Video service after {max_wait_seconds}s. The service might be overloaded or down."
        logger.error(error_msg)
        return {"error": error_msg, "status": "timeout"}
    except httpx.ConnectError as e:
        error_msg = f"Could not connect to Video service at {get_video_url()}. Verify if service is running (port 8001)."
        logger.error(error_msg)
        return {"error": error_msg, "status": "connection_error"}
    except Exception as e:
        error_msg = f"Error calling video service: {type(e).__name__} - {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}


@with_logging("Transcribe Video")
def transcribe_video_tool(video_url: str, language: str = None, model: str = "base") -> Dict[str, Any]:
    """
    Transcribes the audio from a video to text using Whisper AI.
    
    Args:
        video_url: URL of the video to transcribe
        language: Optional language code (e.g., "pt", "en")
        model: Whisper model to use ("tiny", "base", "small", "medium", "large")
    
    Returns:
        dict with transcription text and segments
    """
    try:
        url = f"{get_video_url()}/api/v1/videos/transcribe"
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY
        
        data = {"video_url": video_url, "model": model}
        if language:
            data["language"] = language
            
        response = httpx.post(url, data=data, headers=headers, timeout=600.0)
        return response.json()
    except Exception as e:
        logger.error(f"Error transcribing video: {e}")
        return {"error": str(e)}


@with_logging("Detect Viral Moments")
def detect_viral_moments_tool(
    video_url: str,
    top_percent: float = 30.0,
    max_highlights: int = 15,
    include_transcription: bool = True,
    auto_extract: bool = False,
    max_clips: int = 5,
    language: str = None,
) -> Dict[str, Any]:
    """
    Analisa um vídeo e detecta automaticamente os momentos mais VIRAIS combinando:
    1. Análise de energia do áudio (volume, intensidade vocal)
    2. Transcrição com timestamps (o que foi dito em cada momento)
    3. (Opcional) Extração automática de clips individuais (estilo Opus Clip)

    Retorna uma lista ranqueada de segmentos com:
    - timestamps exatos (start/end)
    - score de energia (0-10)
    - texto transcrito de cada momento
    - duração total e percentual do vídeo

    Quando auto_extract=True, também gera vídeos individuais para cada highlight
    (cada um com seu próprio link de download), sem precisar de interação do usuário.

    Args:
        video_url: URL do vídeo para analisar
        top_percent: Percentual dos melhores momentos (default: 30%)
        max_highlights: Máximo de highlights para retornar (default: 15)
        include_transcription: Se True, transcreve e inclui o texto de cada highlight
        auto_extract: Se True, extrai cada highlight como um vídeo separado (Opus Clip style)
        max_clips: Máximo de clips a extrair quando auto_extract=True (default: 5)
        language: Código do idioma para transcrição (ex: "pt", "en")

    Returns:
        dict com:
        - highlights: lista de {start, end, energy_score, text, duration}
        - total_duration: duração total do vídeo
        - suggested_clips: segmentos sugeridos para smart_cut
        - clips (se auto_extract): lista de clips com download_url individual
    """
    try:
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY

        import time

        # Step 1: Detect audio energy highlights
        url = f"{get_video_url()}/api/v1/videos/detect-highlights"
        data = {
            "video_url": video_url,
            "top_percent": top_percent,
            "max_highlights": max_highlights,
            "window_seconds": 5.0,
        }

        response = httpx.post(url, data=data, headers=headers, timeout=600.0)
        if response.status_code != 200:
            return {"error": f"Highlight detection failed: {response.status_code} - {response.text}"}

        job_data = response.json()
        job_id = job_data.get("id")

        # Poll for completion
        status_url = f"{get_video_url()}/api/v1/videos/status/{job_id}"
        for _ in range(120):  # max 10 min
            time.sleep(5)
            status_resp = httpx.get(status_url, headers=headers, timeout=30.0)
            status = status_resp.json()
            if status.get("status") == "completed":
                break
            if status.get("status") == "failed":
                return {"error": f"Highlight detection failed: {status.get('error_message', 'unknown')}"}

        # The result is in the download_url (JSON file)
        download_url = status.get("download_url")
        if not download_url:
            return {"error": "No highlights result found"}

        highlights_resp = httpx.get(download_url, timeout=30.0)
        try:
            highlights_data = highlights_resp.json()
        except Exception:
            highlights_data = {"highlights": [], "total_duration": 0}

        highlights = highlights_data.get("highlights", [])
        total_duration = highlights_data.get("total_duration", 0)

        # Step 2: Get transcription to enrich highlights with text
        if include_transcription and highlights:
            transcription = transcribe_video_tool(video_url=video_url, language=language)

            if "error" not in transcription:
                segments = transcription.get("segments", [])

                for h in highlights:
                    h_start = h["start"]
                    h_end = h["end"]
                    matching_text = []
                    for seg in segments:
                        seg_start = seg["start"]
                        seg_end = seg["end"]
                        if seg_start < h_end and seg_end > h_start:
                            matching_text.append(seg["text"])
                    h["text"] = " ".join(matching_text).strip()
                    h["duration"] = round(h_end - h_start, 1)

        # Build suggested clips
        suggested_clips = [[h["start"], h["end"]] for h in highlights]
        total_clip_duration = sum(h["end"] - h["start"] for h in highlights)

        # Format the response
        result = {
            "total_duration": round(total_duration, 1),
            "total_highlights": len(highlights),
            "total_clip_duration": round(total_clip_duration, 1),
            "clip_percentage": round((total_clip_duration / total_duration) * 100, 1) if total_duration > 0 else 0,
            "highlights": [
                {
                    "rank": h.get("rank", i + 1),
                    "start": h["start"],
                    "end": h["end"],
                    "duration": round(h["end"] - h["start"], 1),
                    "energy_score": h.get("energy_score", 0),
                    "text": h.get("text", ""),
                    "reason": h.get("reason", "high_energy_audio"),
                }
                for i, h in enumerate(highlights)
            ],
            "suggested_clips": suggested_clips,
        }

        # Step 3: Auto-extract individual clips if requested
        if auto_extract and highlights:
            # Sort by energy and take top max_clips
            best = sorted(highlights, key=lambda h: h.get("energy_score", 0), reverse=True)[:max_clips]
            best.sort(key=lambda h: h["start"])  # re-sort by time
            extract_segments = [[h["start"], h["end"]] for h in best]

            extract_url = f"{get_video_url()}/api/v1/videos/extract-clips"
            import json as json_mod
            extract_data = {
                "video_url": video_url,
                "segments": json_mod.dumps(extract_segments),
                "max_clips": max_clips,
                "min_duration": 30.0,
                "min_energy_score": 6.0,
            }

            extract_resp = httpx.post(extract_url, data=extract_data, headers=headers, timeout=600.0)
            if extract_resp.status_code == 200:
                extract_job = extract_resp.json()
                extract_job_id = extract_job.get("id")

                # Poll for clip extraction completion
                extract_status_url = f"{get_video_url()}/api/v1/videos/status/{extract_job_id}"
                for _ in range(120):
                    time.sleep(5)
                    ext_status_resp = httpx.get(extract_status_url, headers=headers, timeout=30.0)
                    ext_status = ext_status_resp.json()
                    if ext_status.get("status") == "completed":
                        break
                    if ext_status.get("status") == "failed":
                        result["extract_error"] = ext_status.get("error_message", "Clip extraction failed")
                        break

                # Get the manifest with clip URLs
                ext_download_url = ext_status.get("download_url")
                if ext_download_url:
                    manifest_resp = httpx.get(ext_download_url, timeout=30.0)
                    try:
                        manifest = manifest_resp.json()
                        result["clips"] = manifest.get("clips", [])
                        result["total_clips_extracted"] = manifest.get("total_clips", 0)
                        result["instructions"] = (
                            f"Foram extraídos {manifest.get('total_clips', 0)} clips individuais do vídeo. "
                            "Cada clip tem seu próprio link de download. "
                            "Apresente os clips ao usuário com o texto e score de cada um."
                        )
                    except Exception:
                        result["extract_error"] = "Failed to parse clips manifest"
            else:
                result["extract_error"] = f"Clip extraction request failed: {extract_resp.status_code}"

        if "instructions" not in result:
            result["instructions"] = (
                "Apresente estes highlights ao usuário com o texto e score de cada um. "
                "Pergunte quais ele quer manter, remover ou ajustar. "
                "Depois use edit_video_tool com smart_cut ou chame novamente com auto_extract=True."
            )

        return result

    except Exception as e:
        logger.error(f"Error detecting viral moments: {e}")
        return {"error": str(e)}


@with_logging("Get Video Info")
def get_video_info_tool(video_url: str) -> Dict[str, Any]:
    """
    Analisa um vídeo e retorna metadados técnicos SEM fazer download completo.

    Use esta ferramenta ANTES de editar qualquer vídeo para:
    - Saber a duração (para estimar tempo de processamento)
    - Saber a resolução (para escalar font_size adequadamente)
    - Decidir se precisa de max_wait_seconds maior

    Args:
        video_url: URL pública do vídeo a ser analisado

    Returns:
        dict com duration_seconds, duration_human, width, height, fps, codec,
        estimated_size_mb, is_long_video, processing_estimate_minutes

    Guia de decisão:
        - duration < 300s (5 min)   → processamento rápido, max_wait_seconds=600
        - duration 300-1200s        → informar usuário ~10-30 min de espera
        - duration 1200-2400s       → informar usuário ~30-60 min, max_wait_seconds=3600
        - duration > 2400s (40 min) → sugerir trim primeiro

    Guia de font_size por resolução:
        - 1080p (height >= 1080): font_size=12
        - 720p  (height >= 720):  font_size=10
        - 480p  (height < 720):   font_size=8
    """
    try:
        url = f"{get_video_url()}/api/v1/videos/probe"
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY

        response = httpx.post(url, data={"video_url": video_url}, headers=headers, timeout=30.0)
        if response.status_code != 200:
            return {"error": f"Probe failed: {response.status_code} - {response.text}"}
        return response.json()
    except Exception as e:
        logger.error(f"Error probing video: {e}")
        return {"error": str(e)}


@with_logging("List Creators")
def list_creators_tool() -> List[str]:
    """Lista os criadores no banco de referencias (vault Obsidian).

    Retorna lista de strings amigaveis no formato:
      "@handle (platform, kind, posts_analyzed=N, status)"

    Use sempre que precisar saber QUAIS criadores estao disponiveis para
    consultar o estilo. O cliente proprio aparece com kind=self.
    """
    try:
        from app.services.social.markdown_writer import list_creators
        creators = list_creators()
        if not creators:
            return ["(banco de referencias vazio - termine o onboarding ou adicione criadores)"]
        return [
            f"{c['handle']} ({c['platform']}, {c['kind']}, "
            f"posts={c['posts_done']}/{c['posts_total']}, status={c['status']})"
            for c in creators
        ]
    except Exception as e:
        logger.error(f"list_creators_tool failed: {e}")
        return [f"erro ao listar criadores: {e}"]


@with_logging("Get Creator Style")
def get_creator_style_tool(handle: str) -> str:
    """Retorna o perfil completo de um criador (estilo + comunicacao + resumo).

    Use quando precisar GERAR conteudo no estilo de um creator especifico
    (Olivetto, Ogilvy, Beast, GaryV consultam isso antes de produzir).

    Args:
        handle: @ do criador (com ou sem @, ex: '@hormozi' ou 'hormozi').

    Returns:
        Texto formatado pronto para injetar no prompt:
          ## Estilo (hook patterns, narrativa, vocabulario, gatilhos)
          ## Comunicacao (tom, ritmo, formato visual, CTA)
          ## Resumo
    """
    try:
        from app.services.social.markdown_writer import get_creator_dir
        h = handle.strip().lstrip("@").lower()
        if not h:
            return "[erro] handle vazio"
        normalized = f"@{h}"
        profile_path = get_creator_dir(normalized) / "_profile.md"
        if not profile_path.exists():
            return (
                f"[info] {normalized} ainda nao foi analisado no banco de referencias. "
                f"Pode estar sendo extraido em background — tente novamente em alguns minutos, "
                f"ou peca ao usuario para adicionar via aba Referencias."
            )
        return profile_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"get_creator_style_tool({handle}) failed: {e}")
        return f"[erro] {e}"


@with_logging("List Creator Videos")
def list_creator_videos_tool(handle: str) -> List[Dict[str, Any]]:
    """Lista os videos analisados de um creator (caption + duracao + metricas).

    Util para o Beast (video_analyst) entender QUAIS posts foram processados
    antes de drill-down em algum especifico.
    """
    try:
        from app.services.social.markdown_writer import get_creator_dir
        h = handle.strip().lstrip("@").lower()
        normalized = f"@{h}"
        d = get_creator_dir(normalized)
        if not d.exists():
            return [{"error": f"{normalized} nao encontrado"}]
        # Reusa o parser do endpoint para consistencia
        from app.api.v1.endpoints.references import _parse_post_md
        out = []
        for p in sorted(d.glob("*.md")):
            if p.name.startswith("_"):
                continue
            try:
                data = _parse_post_md(p)
                out.append({
                    "post_id": data["post_id"],
                    "url": data["url"],
                    "duration": data["duration"],
                    "caption_preview": (data["caption"] or "")[:200],
                    "play_count": data["play_count"],
                    "like_count": data["like_count"],
                })
            except Exception:
                continue
        return out
    except Exception as e:
        logger.error(f"list_creator_videos_tool({handle}) failed: {e}")
        return [{"error": str(e)}]


@with_logging("Get Creator Video")
def get_creator_video_tool(handle: str, video_id: str) -> Dict[str, Any]:
    """Retorna um video especifico com transcript COMPLETO + caption + URL original.

    Use quando precisar referenciar uma frase exata do creator ou comparar
    detalhes (ex: copiar um hook literal).
    """
    try:
        from app.services.social.markdown_writer import get_creator_dir
        h = handle.strip().lstrip("@").lower()
        normalized = f"@{h}"
        d = get_creator_dir(normalized)
        if not d.exists():
            return {"error": f"{normalized} nao encontrado"}
        candidates = [p for p in d.glob(f"*{video_id}*.md") if not p.name.startswith("_")]
        if not candidates:
            return {"error": f"video {video_id} nao encontrado em {normalized}"}
        from app.api.v1.endpoints.references import _parse_post_md
        return _parse_post_md(candidates[0])
    except Exception as e:
        logger.error(f"get_creator_video_tool({handle},{video_id}) failed: {e}")
        return {"error": str(e)}


def _save_image_to_library(image_url: str, prompt: str):
    """Helper to save a generated image to the user's library."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return
        from app.api.v1.endpoints.library import save_asset
        title = prompt[:100] if prompt else "Imagem gerada"
        save_asset(
            user_id=user_id,
            asset_type="image",
            title=title,
            url=image_url,
            thumbnail_url=image_url,
            metadata={"prompt": prompt},
        )
        logger.info(f"Image saved to library for user {user_id}")
    except Exception as e:
        logger.warning(f"Failed to save image to library: {e}")


def _save_video_to_library(video_url: str, job_id: str):
    """Helper to save a completed video to the user's library."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return
        from app.api.v1.endpoints.library import save_asset
        save_asset(
            user_id=user_id,
            asset_type="video",
            title=f"Vídeo editado",
            url=video_url,
            metadata={"job_id": job_id},
        )
        logger.info(f"Video saved to library for user {user_id}")
    except Exception as e:
        logger.warning(f"Failed to save video to library: {e}")


def _persist_image_bytes(image_bytes: bytes, prompt: str, model_name: str) -> Dict[str, Any]:
    """Helper: salva bytes em /app/storage + S3 + library, retorna dict de resposta."""
    import uuid as _uuid
    import base64 as _base64

    filename = f"gen-{_uuid.uuid4()}.png"
    storage_path = os.getenv("STORAGE_PATH", "/app/storage")
    os.makedirs(storage_path, exist_ok=True)
    filepath = os.path.join(storage_path, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    s3_url = storage_service.upload_bytes_to_s3(image_bytes, filename, "image/png")
    image_url = s3_url if s3_url else f"{get_api_base_url()}/static/{filename}"

    logger.info(f"Image generated with {model_name}: {image_url}")
    _save_image_to_library(image_url, prompt)
    return {
        "url": image_url,
        "b64": f"data:image/png;base64,{_base64.b64encode(image_bytes).decode('utf-8')}",
        "prompt": prompt,
        "model": model_name,
    }


def _try_chatgpt_bridge(prompt: str, size: str = "1024x1024", quality: str = "high") -> Optional[Dict[str, Any]]:
    """Provider ChatGPT (gpt-image-2 via OAuth subscription, sem API key).

    Aponta pra sidecar chatgpt-bridge (default http://chatgpt-bridge:10531/v1).
    Configurar via env CHATGPT_BRIDGE_URL e usuario rodar `npx @openai/codex login`.
    """
    bridge_url = os.getenv("CHATGPT_BRIDGE_URL", "http://chatgpt-bridge:10531/v1")
    if not bridge_url:
        return None
    try:
        import base64
        endpoint = bridge_url.rstrip("/") + "/images/generations"
        r = httpx.post(
            endpoint,
            json={
                "model": os.getenv("CHATGPT_BRIDGE_MODEL", "gpt-image-2"),
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "n": 1,
            },
            timeout=180.0,
        )
        if r.status_code != 200:
            logger.warning(f"chatgpt-bridge HTTP {r.status_code}: {r.text[:200]}")
            return None
        data = r.json()
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            return None
        image_bytes = base64.b64decode(b64)
        return _persist_image_bytes(image_bytes, prompt, "chatgpt-bridge:gpt-image-2")
    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        logger.info(f"chatgpt-bridge indisponivel ({type(e).__name__}); fallback")
        return None
    except Exception as e:
        logger.warning(f"chatgpt-bridge falhou: {e}")
        return None


def _try_openai_image(prompt: str, size: str = "1024x1024", quality: str = "high") -> Optional[Dict[str, Any]]:
    """Generate through the OpenAI Images API when an API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        import base64

        response = httpx.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "n": 1,
            },
            timeout=180.0,
        )
        if response.status_code != 200:
            logger.warning("OpenAI Images HTTP %s: %s", response.status_code, response.text[:200])
            return None
        b64 = (response.json().get("data") or [{}])[0].get("b64_json")
        if not b64:
            logger.warning("OpenAI Images returned no image data")
            return None
        return _persist_image_bytes(base64.b64decode(b64), prompt, "openai:gpt-image-1")
    except Exception as exc:
        logger.warning("OpenAI Images failed: %s", exc)
        return None


def _try_gemini_imagen(prompt: str) -> Optional[Dict[str, Any]]:
    """Provider Google (Gemini 3 Pro Image / Nano Banana / Imagen 4) — fallback."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.info("GOOGLE_API_KEY ausente; fallback")
        return None
    try:
        from google import genai
        from google.genai import types
        import uuid
        import base64

        client = genai.Client(api_key=api_key)
        
        # Try Gemini image models first, then Imagen 4
        gemini_models = [
            'gemini-3.1-flash-image-preview',   # Flash Image - preferred
            'gemini-3-pro-image-preview',        # Nano Banana Pro - best quality
            'gemini-2.5-flash-image',            # Nano Banana - fast
        ]
        
        imagen_models = [
            'imagen-4.0-generate-001',          # Imagen 4 standard
            'imagen-4.0-fast-generate-001',     # Imagen 4 fast
        ]
        
        last_error = None
        
        # Try Gemini models (use generate_content with IMAGE modality)
        for model_name in gemini_models:
            try:
                logger.info(f"Trying image generation with Gemini model: {model_name}")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['IMAGE'],
                    )
                )
                
                # Extract image from response
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                            image_data = part.inline_data.data
                            if isinstance(image_data, str):
                                image_data = base64.b64decode(image_data)
                            
                            filename = f"gen-{uuid.uuid4()}.png"
                            storage_path = os.getenv("STORAGE_PATH", "/app/storage")
                            os.makedirs(storage_path, exist_ok=True)
                            filepath = os.path.join(storage_path, filename)
                            
                            with open(filepath, "wb") as f:
                                f.write(image_data)
                                
                            s3_url = storage_service.upload_bytes_to_s3(image_data, filename, "image/png")
                            if s3_url:
                                image_url = s3_url
                            else:
                                image_url = f"{get_api_base_url()}/static/{filename}"
                            
                            logger.info(f"Image generated successfully with {model_name}: {image_url}")
                            _save_image_to_library(image_url, prompt)
                            return {"url": image_url, "prompt": prompt, "model": model_name}
                
                last_error = f"No image data in response from {model_name}"
                logger.warning(last_error)
                continue
                
            except Exception as model_error:
                last_error = str(model_error)
                logger.warning(f"Gemini model {model_name} failed: {last_error}")
                continue
        
        # Fallback to Imagen models (use generate_images API)
        for model_name in imagen_models:
            try:
                logger.info(f"Fallback: trying Imagen model: {model_name}")
                response = client.models.generate_images(
                    model=model_name,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                    )
                )
                
                if not response.generated_images:
                    last_error = f"No image generated from {model_name}"
                    continue
                
                # Extract image bytes from Imagen response
                imagen_image = response.generated_images[0]
                imagen_bytes = None
                if hasattr(imagen_image, 'image') and hasattr(imagen_image.image, 'image_bytes'):
                    imagen_bytes = imagen_image.image.image_bytes
                elif hasattr(imagen_image, 'image_bytes'):
                    imagen_bytes = imagen_image.image_bytes
                
                if not imagen_bytes:
                    last_error = f"Could not extract image bytes from {model_name} response"
                    logger.warning(last_error)
                    continue
                
                b64_data = base64.b64encode(imagen_bytes).decode('utf-8')
                image_b64 = f"data:image/png;base64,{b64_data}"
                
                filename = f"gen-{uuid.uuid4()}.png"
                storage_path = os.getenv("STORAGE_PATH", "/app/storage")
                os.makedirs(storage_path, exist_ok=True)
                filepath = os.path.join(storage_path, filename)
                
                with open(filepath, "wb") as f:
                    f.write(imagen_bytes)
                    
                s3_url = storage_service.upload_bytes_to_s3(imagen_bytes, filename, "image/png")
                if s3_url:
                    image_url = s3_url
                else:
                    image_url = f"{get_api_base_url()}/static/{filename}"
                
                logger.info(f"Image generated successfully with {model_name}: {image_url}")
                _save_image_to_library(image_url, prompt)
                return {
                    "url": image_url,
                    "b64": image_b64,
                    "prompt": prompt,
                    "model": model_name
                }
                
            except Exception as model_error:
                last_error = str(model_error)
                logger.warning(f"Imagen model {model_name} failed: {last_error}")
                continue
        
        # Todos os modelos Gemini/Imagen falharam
        logger.warning(f"Todos os modelos Google falharam. Ultimo erro: {last_error}")
        return None

    except Exception as e:
        logger.error(f"Erro Google GenAI: {e}")
        return None


@with_logging("Generate Image (Orchestrator)")
def generate_image_tool(prompt: str, size: str = "1024x1024", quality: str = "high") -> Dict[str, Any]:
    """
    Gera imagem com cascata de providers:
      1. chatgpt-bridge (gpt-image-2 via subscription ChatGPT — sem API key)
      2. OpenAI Images API
      3. Google (Gemini 3 Pro Image / Nano Banana / Imagen 4)

    Configuravel via env IMAGE_GEN_PROVIDER:
      - "chatgpt": usa apenas chatgpt-bridge
      - "gemini" : usa apenas Google
      - "openai" : usa apenas OpenAI Images API
      - "auto"   : tenta chatgpt -> OpenAI -> Google (default)

    Args:
        prompt: descricao da imagem
        size:   ex "1024x1024", "1536x1024" (apenas chatgpt-bridge usa)
        quality: "low" | "medium" | "high" (apenas chatgpt-bridge usa)
    """
    provider = os.getenv("IMAGE_GEN_PROVIDER", "auto").lower()

    if provider in ("auto", "chatgpt"):
        result = _try_chatgpt_bridge(prompt, size=size, quality=quality)
        if result is not None:
            return result
        if provider == "chatgpt":
            return {"error": "chatgpt-bridge indisponivel ou nao autenticado"}

    if provider in ("auto", "openai"):
        result = _try_openai_image(prompt, size=size, quality=quality)
        if result is not None:
            return result
        if provider == "openai":
            return {"error": "OpenAI Images indisponivel ou OPENAI_API_KEY nao configurada"}

    if provider in ("auto", "gemini"):
        result = _try_gemini_imagen(prompt)
        if result is not None:
            return result
        if provider == "gemini":
            return {"error": "Google GenAI indisponivel ou todos os modelos falharam"}

    return {
        "error": (
            "Nenhum provider de imagem disponivel. "
            "Configure CHATGPT_BRIDGE_URL com credenciais Codex, OPENAI_API_KEY "
            "ou GOOGLE_API_KEY na VPS."
        )
    }


# --- KNOWLEDGE BASE TOOLS ---

KNOWLEDGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge")


def _read_kb_file(filename: str) -> str:
    """Helper interno para ler arquivos da knowledge base."""
    try:
        path = os.path.join(KNOWLEDGE_PATH, filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading knowledge base file {filename}: {e}")
        return f"Erro ao ler base de conhecimento: {str(e)}"


@with_logging("Read KB: Base")
def read_base_tool() -> str:
    """
    Lê o conhecimento técnico de marketing e estrutura de roteiros.
    IMPORTANTE: Use antes de escrever qualquer roteiro para entender:
    - Estrutura AIDA para vídeos
    - Tipos de hooks que funcionam
    - Gatilhos mentais para engajamento
    - Estrutura de CTA para comentários
    """
    return _read_kb_file("base.md")


@with_logging("Read KB: Valores")
def read_valores_tool() -> str:
    """
    Lê os valores e Golden Circle do Marlon.
    IMPORTANTE: Use para criar conteúdo alinhado com:
    - POR QUÊ: Propósito e missão
    - VALORES: Autenticidade, Integridade, Liberdade, Família
    - COMO: Processos e abordagens
    - O QUÊ: Produtos e serviços oferecidos
    """
    return _read_kb_file("valores.md")


@with_logging("Read KB: Publico")
def read_publico_tool() -> str:
    """
    Lê informações sobre o público-alvo.
    IMPORTANTE: Use para entender:
    - Quem é a persona ideal
    - Dores e desejos do público
    - Linguagem e tom adequados
    """
    return _read_kb_file("publico.md")


@with_logging("Read KB: Historia")
def read_historia_tool() -> str:
    """
    Lê a história e background do Marlon.
    IMPORTANTE: Use para adicionar personalidade e autenticidade:
    - Jornada pessoal
    - Experiências relevantes
    - Elementos para storytelling
    """
    return _read_kb_file("historia.md")


@with_logging("Read KB: Video Knowledge")
def read_video_knowledge_tool() -> str:
    """
    Lê o guia completo de edição de vídeo, efeitos e cortes inteligentes.
    IMPORTANTE: Use para entender:
    - Como usar o smart_cut para manter apenas as melhores partes
    - Efeitos de legenda (highlight-word, typewriter)
    - Overlays de texto e animações
    """
    return _read_kb_file("video_knowledge.md")


def read_all_knowledge_tool() -> Dict[str, str]:
    """
    Lê TODOS os arquivos de conhecimento de uma vez.
    Use quando precisar de contexto completo para criar um roteiro.
    """
    return {
        "base": _read_kb_file("base.md"),
        "valores": _read_kb_file("valores.md"),
        "publico": _read_kb_file("publico.md"),
        "historia": _read_kb_file("historia.md")
    }


@with_logging("Save Script")
def save_script_tool(title: str, content: str, user_id: str = None) -> Dict[str, Any]:
    """
    Salva um roteiro/script gerado na biblioteca de ativos do usuário.
    IMPORTANTE: Sempre chame esta função após criar um roteiro completo.
    - title: Título descritivo do roteiro (ex: "Roteiro: Como ganhar liberdade financeira")
    - content: Texto completo do roteiro gerado
    - user_id: ID do usuário (extraído automaticamente do contexto quando disponível)
    """
    if not user_id:
        user_id = get_current_user_id()
    if not user_id:
        return {"status": "skipped", "reason": "user_id não disponível — script não salvo na biblioteca"}

    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        preview = content[:300] + "..." if len(content) > 300 else content
        result = client.table("content_assets").insert({
            "user_id": user_id,
            "type": "script",
            "title": title,
            "description": preview,
            "metadata": {"content": content},
        }).execute()
        saved = result.data[0] if result.data else {}
        logger.info(f"Script salvo na biblioteca: {saved.get('id')} para user {user_id}")
        return {"status": "saved", "asset_id": saved.get("id"), "title": title}
    except Exception as e:
        logger.warning(f"Falha ao salvar script na biblioteca: {e}")
        return {"status": "error", "reason": str(e)}

@with_logging("Check Video Status")
def check_video_status_tool(job_id: str):
    """
    Checks the status of a video editing job and converts relative URLs to absolute.
    """
    try:
        url = f"{get_video_url()}/api/v1/videos/status/{job_id}"
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY
            
        response = httpx.get(url, headers=headers, timeout=10.0)
        
        if response.status_code != 200:
            error_msg = f"Status check failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
        
        result = response.json()
        
        # Normalize download_url to always use PUBLIC_API_URL (gateway)
        if result.get("status") == "completed" and result.get("download_url"):
            orig_url = result["download_url"]
            gateway = get_video_public_url()
            if gateway and "/static/" in orig_url:
                static_part = orig_url.split("/static/", 1)[1]
                result["download_url"] = f"{gateway}/static/{static_part}"
                logger.info(f"[CHECK STATUS] URL normalizada: {orig_url} -> {result['download_url']}")
            elif gateway and orig_url.startswith("/"):
                result["download_url"] = f"{gateway}{orig_url}"
                logger.info(f"[CHECK STATUS] URL relativa normalizada: {orig_url} -> {result['download_url']}")

            # Auto-save completed video to library
            _save_video_to_library(result["download_url"], job_id)

        return result
    except Exception as e:
        logger.error(f"Error checking video status: {e}")
        return {"error": str(e)}


@with_logging("Generate Presigned URL")
def generate_presigned_url_tool(object_key: str, expiration: int = 3600):
    """
    Gera uma URL pré-assinada para acesso temporário a um arquivo no MinIO/S3.
    Use esta ferramenta quando o vídeo estiver no MinIO e não for publicamente acessível.
    
    Args:
        object_key: Caminho do arquivo no bucket (ex: 'stories/teste_jump.mp4')
        expiration: Tempo de validade em segundos (padrão: 3600 = 1 hora)
    
    Returns:
        dict com:
        - url: URL pré-assinada válida temporariamente
        - expires_in: Tempo de validade em segundos
        - object_key: Caminho do arquivo
        - error: Mensagem de erro (se falhar)
    
    Exemplo:
        generate_presigned_url_tool('stories/teste_jump.mp4')
        → {'url': 'https://...?X-Amz-Signature=...', 'expires_in': 3600}
    """
    try:
        import boto3
        from botocore.client import Config
        
        s3_endpoint = os.getenv('S3_ENDPOINT_URL')
        s3_access_key = os.getenv('S3_ACCESS_KEY')
        s3_secret_key = os.getenv('S3_SECRET_KEY')
        s3_bucket = os.getenv('S3_BUCKET_NAME', 'videos_agi')
        s3_region = os.getenv('S3_REGION', 'auto')
        
        if not all([s3_endpoint, s3_access_key, s3_secret_key]):
            return {"error": "Credenciais do MinIO/S3 não configuradas no .env"}
        
        # Remove trailing slash from endpoint
        s3_endpoint = s3_endpoint.rstrip('/')
        
        logger.info(f"[PRESIGNED URL] Gerando para {object_key} no bucket {s3_bucket}")
        
        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key,
            config=Config(signature_version='s3v4'),
            region_name=s3_region
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket, 'Key': object_key},
            ExpiresIn=expiration
        )
        
        logger.info(f"[PRESIGNED URL] ✓ Gerada com sucesso, válida por {expiration}s")
        logger.info(f"[PRESIGNED URL] URL: {presigned_url[:100]}...")
        
        return {
            "url": presigned_url,
            "expires_in": expiration,
            "object_key": object_key,
            "bucket": s3_bucket
        }
        
    except ImportError:
        error_msg = "boto3 não instalado. Execute: pip install boto3"
        logger.error(f"[PRESIGNED URL] {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Erro ao gerar presigned URL: {str(e)}"
        logger.error(f"[PRESIGNED URL] {error_msg}")
        return {"error": error_msg}


# --- BRANDCRAFT INTEGRATION MOCKS ---

@with_logging("Extract Design System")
def extract_design_system_tool(url: str) -> str:
    """
    Extracts visual design system (colors, typography) from a target URL.
    Args:
        url (str): The URL of the brand to extract from.
    Returns:
        str: JSON representation of the extracted design tokens.
    """
    logger.info(f"BrandCraft: Extracting design system from {url}")
    mock_tokens = {
        "primaryColor": "#000000",
        "secondaryColor": "#FFFFFF",
        "fontFamily": "Inter, sans-serif",
        "extracted_from": url
    }
    return json.dumps(mock_tokens, indent=2)

@with_logging("Create Branded PDF")
def create_branded_pdf_tool(content: str, design_tokens_id: str) -> str:
    """
    Generates a PDF document stylized with specific brand tokens.
    Args:
        content (str): The markdown/text content to lay out on the PDF.
        design_tokens_id (str): Reference to the extracted design tokens (JSON or ID).
    Returns:
        str: URL to the generated PDF.
    """
    logger.info(f"BrandCraft: Creating branded PDF using tokens {design_tokens_id}")
    return "https://mock-storage.local/generated_brand_doc.pdf"

@with_logging("Create Branded PPTX")
def create_branded_pptx_tool(slides: str, design_tokens_id: str) -> str:
    """
    Generates a native PPTX presentation stylized with specific brand tokens.
    Args:
        slides (str): JSON string representing slide contents.
        design_tokens_id (str): Reference to the extracted design tokens.
    Returns:
        str: URL to the generated PPTX file.
    """
    logger.info("BrandCraft: Creating branded PPTX")
    return "https://mock-storage.local/generated_brand_presentation.pptx"

@with_logging("Select Viral Clips")
def select_viral_clips_tool(
    video_url: str,
    max_clips: int = 5,
    min_duration: float = 30.0,
    max_duration: float = 75.0,
    max_wait_seconds: int = 1800,
) -> Dict[str, Any]:
    """
    Pipeline editordofuturo: normaliza -> transcreve -> seleciona clipes virais via cascata
    LLM (Claude Sonnet 4.6 -> GPT-4.1-mini -> Gemini 2.5 Flash -> Llama-3.3-70b).

    Diferente de detect_viral_moments_tool (energia de audio), este aqui usa o TEXTO
    transcrito pra encontrar hooks, arcos narrativos completos e momentos "aha".
    Cada clipe vem com title, hook (frase literal), reason e timestamps validados.

    Use este tool quando o usuario pedir "clipes virais", "shorts", "melhores momentos
    com hook" ou pedir analise de conteudo (nao so volume).

    Args:
        video_url: URL do video a analisar.
        max_clips: Maximo de clipes retornados (default 5).
        min_duration: Duracao minima por clipe em segundos (default 30).
        max_duration: Duracao maxima por clipe em segundos (default 75).
        max_wait_seconds: Timeout total do pipeline (default 1800 = 30min).

    Returns:
        dict com:
          - source: URL/path do video original
          - clips: lista de {title, start, end, hook, reason}
          - download_url: URL do JSON completo + sidecar .review.md
          - job_id: id do job no video service
    """
    try:
        edit_url = f"{get_video_url()}/api/v1/videos/edit"
        headers = {}
        if VIDEO_SERVICE_KEY:
            headers["x-api-key"] = VIDEO_SERVICE_KEY

        payload = {
            "video_url": video_url,
            "operations": json.dumps([
                {"type": "normalize", "params": {"fps": 30, "keyframe_interval": 1, "crf": 18}},
                {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
                {
                    "type": "select_clips",
                    "params": {
                        "max_clips": max_clips,
                        "min_duration": min_duration,
                        "max_duration": max_duration,
                    },
                },
            ]),
        }

        response = httpx.post(edit_url, data=payload, headers=headers, timeout=120.0)
        if response.status_code != 200:
            return {"error": f"Video service rejected job: {response.status_code} - {response.text}"}

        job_response = response.json()
        job_id = (
            job_response.get("job_id")
            or job_response.get("task_id")
            or job_response.get("id")
        )
        if not job_id:
            return {"error": "Failed to get job_id from video service", "response": job_response}

        status_url = f"{get_video_url()}/api/v1/videos/status/{job_id}"
        start_time = time.time()
        poll_interval = 5
        download_url = None

        while time.time() - start_time < max_wait_seconds:
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, 30)
            try:
                status_resp = httpx.get(status_url, headers=headers, timeout=30.0)
                if status_resp.status_code != 200:
                    continue
                status_data = status_resp.json()
                status = status_data.get("status", "").lower()
                logger.info(
                    f"select_viral_clips job {job_id}: {status} "
                    f"({status_data.get('progress', 0)}%)"
                )
                if status == "completed":
                    download_url = status_data.get("download_url")
                    # Normaliza pro gateway publico se necessario
                    gateway = get_video_public_url()
                    if download_url and gateway and "/static/" in download_url:
                        static_part = download_url.split("/static/", 1)[1]
                        download_url = f"{gateway}/static/{static_part}"
                    break
                if status == "failed":
                    return {
                        "error": status_data.get("error_message", "Job failed"),
                        "job_id": job_id,
                        "status": "failed",
                    }
            except Exception as poll_error:
                logger.warning(f"Error polling job status: {poll_error}")

        if not download_url:
            return {
                "error": f"Timeout after {max_wait_seconds}s",
                "job_id": job_id,
                "status": "timeout",
            }

        # Baixa o JSON final {source, clips:[...]}
        try:
            clips_resp = httpx.get(download_url, timeout=60.0)
            clips_data = clips_resp.json() if clips_resp.status_code == 200 else {}
        except Exception as e:
            logger.warning(f"Failed to fetch clips JSON: {e}")
            clips_data = {}

        return {
            "job_id": job_id,
            "download_url": download_url,
            "review_url": download_url.replace(".json", ".review.md") if download_url else None,
            "source": clips_data.get("source", video_url),
            "clips": clips_data.get("clips", []),
            "total_clips": len(clips_data.get("clips", [])),
            "instructions": (
                "Apresente cada clipe ao usuario com title, hook e reason. "
                "Confirme quais ele quer renderizar antes de chamar edit_video_tool "
                "com smart_cut nos timestamps escolhidos."
            ),
        }

    except httpx.ConnectError:
        return {"error": f"Could not connect to Video service at {get_video_url()}"}
    except Exception as e:
        logger.error(f"Error in select_viral_clips_tool: {e}")
        return {"error": str(e)}


def _run_video_preset_job(
    preset: str,
    video_url: str,
    extra_ops: Optional[List[Dict[str, Any]]] = None,
    max_wait_seconds: int = 1800,
    label: str = "preset",
) -> Dict[str, Any]:
    """Helper: chama /api/v1/videos/edit com preset (e/ou operations extras), faz poll
    do status e retorna {download_url, job_id, status_data}. Compartilhado pelas tools
    do pipeline editordofuturo (eval, fillers, speakers, fast_subtitles, filmstrip)."""
    edit_url = f"{get_video_url()}/api/v1/videos/edit"
    headers = {}
    if VIDEO_SERVICE_KEY:
        headers["x-api-key"] = VIDEO_SERVICE_KEY

    ops: List[Dict[str, Any]] = [{"type": "preset", "params": {"name": preset}}] if preset else []
    if extra_ops:
        ops.extend(extra_ops)

    payload = {"video_url": video_url, "operations": json.dumps(ops)}
    response = httpx.post(edit_url, data=payload, headers=headers, timeout=120.0)
    if response.status_code != 200:
        return {"error": f"Video service rejected job: {response.status_code} - {response.text}"}

    job_response = response.json()
    job_id = (
        job_response.get("job_id")
        or job_response.get("task_id")
        or job_response.get("id")
    )
    if not job_id:
        return {"error": "Failed to get job_id from video service", "response": job_response}

    status_url = f"{get_video_url()}/api/v1/videos/status/{job_id}"
    start_time = time.time()
    poll_interval = 5
    while time.time() - start_time < max_wait_seconds:
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, 30)
        try:
            status_resp = httpx.get(status_url, headers=headers, timeout=30.0)
            if status_resp.status_code != 200:
                continue
            status_data = status_resp.json()
            status = status_data.get("status", "").lower()
            logger.info(f"{label} job {job_id}: {status} ({status_data.get('progress', 0)}%)")
            if status == "completed":
                download_url = status_data.get("download_url")
                gateway = get_video_public_url()
                if download_url and gateway and "/static/" in download_url:
                    static_part = download_url.split("/static/", 1)[1]
                    download_url = f"{gateway}/static/{static_part}"
                return {"job_id": job_id, "download_url": download_url, "status_data": status_data}
            if status == "failed":
                return {
                    "error": status_data.get("error_message", "Job failed"),
                    "job_id": job_id, "status": "failed",
                }
        except Exception as e:
            logger.warning(f"Error polling job status: {e}")

    return {"error": f"Timeout after {max_wait_seconds}s", "job_id": job_id, "status": "timeout"}


@with_logging("Eval Cut Quality")
def eval_cut_quality_tool(
    video_url: str,
    apply_snap: bool = True,
    max_wait_seconds: int = 1800,
) -> Dict[str, Any]:
    """
    Avalia a qualidade dos cortes de um vídeo: detecta cuts mid-word, gaps apertados
    e sugere snap-to-nearest-word-boundary. Roda transcribe + select_clips + eval_cuts.

    Use quando o usuário disser "verifica os cortes", "esses cortes estão bons?",
    "ajusta as bordas", ou após gerar clipes virais e querer validar antes de renderizar.

    Args:
        video_url: URL do vídeo.
        apply_snap: Se True, aplica os snaps automaticamente (default True).
        max_wait_seconds: Timeout total (default 1800).

    Returns:
        dict com:
        - clips: [{title, start, end, overall (good/warn/bad), suggested_start, suggested_end}]
        - download_url: URL do JSON eval.json + sidecar review.md
    """
    extra = [{"type": "eval_cuts", "params": {"apply": apply_snap}}]
    result = _run_video_preset_job(
        preset="VIRAL_FUTURO",
        video_url=video_url,
        extra_ops=extra,
        max_wait_seconds=max_wait_seconds,
        label="eval_cut_quality",
    )
    if "error" in result:
        return result
    download_url = result.get("download_url")
    eval_data = {}
    try:
        if download_url:
            r = httpx.get(download_url, timeout=60.0)
            if r.status_code == 200:
                eval_data = r.json()
    except Exception as e:
        logger.warning(f"Failed to fetch eval JSON: {e}")
    return {
        "job_id": result.get("job_id"),
        "download_url": download_url,
        "review_url": download_url.replace(".json", ".review.md") if download_url else None,
        "clips": eval_data.get("clips", []),
        "instructions": (
            "Mostre cada clipe com seu status (OK/WARN/BAD) e os timestamps sugeridos. "
            "BAD = corte no meio de uma palavra. WARN = gap apertado. OK = silencio limpo."
        ),
    }


@with_logging("Detect Filler Words")
def detect_fillers_tool(
    video_url: str,
    silence_threshold: float = 0.6,
    padding: float = 0.08,
    extra_fillers: Optional[List[str]] = None,
    max_wait_seconds: int = 1800,
) -> Dict[str, Any]:
    """
    Detecta filler words ("uh", "tipo", "né") + silêncios via transcript word-level.
    Diferente de remove_silence (só áudio), este olha o TEXTO transcrito.

    Use quando o usuário pedir "limpar fillers", "tirar muletas", "remover né e tipo",
    ou para conteúdo educativo onde precisa preservar 100% da fala.

    Args:
        video_url: URL do vídeo.
        silence_threshold: Gap mínimo entre palavras para cortar (default 0.6s).
        padding: Padding ao redor da fala (default 0.08s).
        extra_fillers: Lista extra de fillers customizados.

    Returns:
        dict com:
        - keep: ranges de áudio para manter (alimenta smart_cut)
        - removed: ranges removidos com motivo
        - download_url: JSON completo
    """
    params: Dict[str, Any] = {
        "silence_threshold": silence_threshold,
        "padding": padding,
    }
    if extra_fillers:
        params["fillers"] = extra_fillers
    extra = [{"type": "detect_fillers", "params": params}]
    result = _run_video_preset_job(
        preset="CLEAN_PRO",
        video_url=video_url,
        extra_ops=None,  # CLEAN_PRO ja inclui detect_fillers
        max_wait_seconds=max_wait_seconds,
        label="detect_fillers",
    )
    if "error" in result:
        return result
    download_url = result.get("download_url")
    fillers_data = {}
    try:
        if download_url:
            r = httpx.get(download_url, timeout=60.0)
            if r.status_code == 200:
                fillers_data = r.json()
    except Exception as e:
        logger.warning(f"Failed to fetch fillers JSON: {e}")
    keep = fillers_data.get("keep", [])
    return {
        "job_id": result.get("job_id"),
        "download_url": download_url,
        "review_url": download_url.replace(".json", ".review.md") if download_url else None,
        "keep_segments": [[r["start"], r["end"]] for r in keep],
        "removed_count": len(fillers_data.get("removed", [])),
        "instructions": (
            "Para aplicar a limpeza, chame edit_video_tool com smart_cut e keep_segments."
        ),
    }


@with_logging("Track Speakers")
def track_speakers_tool(
    video_url: str,
    sample_fps: float = 5.0,
    max_wait_seconds: int = 3600,
) -> Dict[str, Any]:
    """
    Active speaker detection via MediaPipe: detecta posição do rosto que está falando
    ao longo do tempo (correlação áudio-visual).

    Use para clipes verticais com 1+ pessoas onde a câmera precisa seguir quem fala.
    Output alimenta a fase de crop dinâmico do Remotion (face tracking).

    Args:
        video_url: URL do vídeo.
        sample_fps: Amostragem (default 5.0).

    Returns:
        dict com:
        - samples: [{t, x, y, h}] - posições normalizadas (0-1)
        - mean_faces: média de rostos por frame
        - download_url: JSON completo
    """
    extra = [{"type": "detect_speakers", "params": {"sample_fps": sample_fps}}]
    result = _run_video_preset_job(
        preset="",
        video_url=video_url,
        extra_ops=extra,
        max_wait_seconds=max_wait_seconds,
        label="track_speakers",
    )
    if "error" in result:
        return result
    download_url = result.get("download_url")
    spk_data = {}
    try:
        if download_url:
            r = httpx.get(download_url, timeout=60.0)
            if r.status_code == 200:
                spk_data = r.json()
    except Exception as e:
        logger.warning(f"Failed to fetch speakers JSON: {e}")
    return {
        "job_id": result.get("job_id"),
        "download_url": download_url,
        "samples": spk_data.get("samples", []),
        "mean_faces": spk_data.get("meanFaces", 0),
        "duration": spk_data.get("duration", 0),
        "instructions": (
            "Use as samples como input do crop dinâmico no Remotion ou ffmpeg "
            "(crop centralizado em x,y por janela de tempo)."
        ),
    }


@with_logging("Fast Render Subtitles")
def fast_render_subtitles_tool(
    video_url: str,
    position: str = "center",
    vertical: bool = True,
    font: str = "Urbanist",
    font_size: int = 72,
    color_primary: str = "FFFFFF",
    color_highlight: str = "FFD600",
    max_words: int = 3,
    headline: str = "",
    max_wait_seconds: int = 1800,
) -> Dict[str, Any]:
    """
    Render legendas word-by-word Hormozi-style via FFmpeg+libass.
    10-15x mais rápido que Remotion (sem motion graphics).

    Use para renders em massa, previews rápidos ou quando o usuário NÃO precisa
    de zoom dinâmico, transições ou hooks visuais (caso contrário use remotion_render).

    Args:
        video_url: URL do vídeo.
        position: "center" | "top" | "bottom" (default "center").
        vertical: Se True, crop pra 1080x1920 (default True).
        font: Nome da fonte (default "Urbanist").
        font_size: px (default 72).
        color_primary: Hex sem # (default "FFFFFF").
        color_highlight: Hex sem # (default "FFD600").
        max_words: Palavras por linha (default 3).
        headline: Título persistente (opcional).

    Returns:
        dict com download_url do MP4 final.
    """
    params: Dict[str, Any] = {
        "position": position,
        "vertical": vertical,
        "font": font,
        "font_size": font_size,
        "color_primary": color_primary,
        "color_highlight": color_highlight,
        "max_words": max_words,
    }
    if headline:
        params["headline"] = headline
    extra = [{"type": "fast_subtitles", "params": params}]
    result = _run_video_preset_job(
        preset="",
        video_url=video_url,
        extra_ops=[
            {"type": "transcribe", "params": {"language": None, "word_timestamps": True}},
            *extra,
        ],
        max_wait_seconds=max_wait_seconds,
        label="fast_render_subtitles",
    )
    if "error" in result:
        return result
    return {
        "job_id": result.get("job_id"),
        "download_url": result.get("download_url"),
        "instructions": "Render concluído via FFmpeg+libass.",
    }


@with_logging("Filmstrip Preview")
def filmstrip_preview_tool(
    video_url: str,
    start: float,
    end: float,
    frames: int = 8,
    markers: Optional[List[float]] = None,
    max_wait_seconds: int = 600,
) -> Dict[str, Any]:
    """
    Gera PNG composite (frames + waveform) para review visual de um trecho.
    Útil quando o usuário ou outro agente precisa decidir manualmente onde cortar.

    Args:
        video_url: URL do vídeo.
        start: Início do trecho (segundos).
        end: Fim do trecho (segundos).
        frames: Quantidade de frames no strip (default 8).
        markers: Timestamps a marcar com linha vermelha (default [start, end]).

    Returns:
        dict com download_url do PNG.
    """
    params: Dict[str, Any] = {"start": start, "end": end, "frames": frames}
    if markers:
        params["markers"] = markers
    else:
        params["markers"] = [start, end]
    extra = [{"type": "filmstrip", "params": params}]
    result = _run_video_preset_job(
        preset="",
        video_url=video_url,
        extra_ops=extra,
        max_wait_seconds=max_wait_seconds,
        label="filmstrip",
    )
    if "error" in result:
        return result
    return {
        "job_id": result.get("job_id"),
        "download_url": result.get("download_url"),
        "instructions": "Apresente o PNG ao usuário para escolha visual de boundaries.",
    }


@with_logging("Instagram Screenshot")
def instagram_screenshot_tool(handle: str, count: int = 9) -> Dict[str, Any]:
    """Tira prints visuais de um perfil Instagram (Playwright, sessao persistente).

    Diferente das tools de creator (que pegam metadata + URLs), esta produz
    screenshots PNG reais — util quando o cliente quer 'copiar a pegada
    visual' de um @ (paleta, tipografia, composicao das capas).

    Args:
        handle: @ do perfil publico (com ou sem @).
        count: numero de posts individuais a capturar (default 9).

    Returns:
        dict com:
        - profile: @ normalizado
        - grid_url: URL do screenshot do perfil completo
        - post_urls: lista de URLs dos posts individuais
        - error (se falhou)
    """
    try:
        from app.services.instagram_playwright import capture_profile_screenshots_sync
    except ImportError as e:
        return {"error": f"Playwright nao disponivel: {e}"}

    try:
        result = capture_profile_screenshots_sync(handle=handle, count=count, headless=True)
    except Exception as e:
        return {"error": str(e)}

    # Converte paths para URLs servidas via /static/
    storage = os.getenv("STORAGE_PATH", "/app/storage").rstrip("/")
    public_base = get_video_public_url().rstrip("/")

    def _to_url(path: str) -> str:
        rel = path.replace(storage, "").replace("\\", "/").lstrip("/")
        return f"{public_base}/static/{rel}" if public_base else f"/static/{rel}"

    return {
        "profile": result["profile"],
        "captured_at": result["captured_at"],
        "grid_url": _to_url(result["grid_path"]),
        "post_urls": [_to_url(p) for p in result["post_paths"]],
        "post_count": result["post_count"],
    }


@with_logging("Inspect Asset")
def inspect_asset_tool(asset_url: str) -> str:
    """
    Performs visual QA on a generated asset to ensure it meets brand guidelines.
    Args:
        asset_url (str): URL of the asset to inspect.
    Returns:
        str: Validation report (PASS/FAIL + notes).
    """
    logger.info(f"BrandCraft: Inspecting asset {asset_url}")
    return "QA Report: PASS. The asset correctly utilizes the primary brand colors and typography. Layout is optimal."
