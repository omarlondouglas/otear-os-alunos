"""Registry of stable product capabilities.

This is intentionally descriptive for now. Facades can be added per capability
without moving legacy tools out of app/agents/agno_tools.py immediately.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    description: str
    legacy_sources: tuple[str, ...]


CAPABILITIES: tuple[Capability, ...] = (
    Capability(
        id="research",
        name="Pesquisa",
        description="Busca contexto atual, noticias, dados, tendencias e exemplos.",
        legacy_sources=("web_search_tool", "get_news_tool", "app/services/news_digest"),
    ),
    Capability(
        id="references",
        name="Referencias",
        description="Importa e analisa perfis, links, imagens, videos e materiais de marca.",
        legacy_sources=("references-panel", "app/api/v1/endpoints/references.py", "instagram_screenshot_tool"),
    ),
    Capability(
        id="model_extraction",
        name="Extracao de modelo",
        description="Transforma referencias em modelos reutilizaveis de voz, visual, hooks e estrutura.",
        legacy_sources=("Erico", "InstaVisualRef", "app/knowledge"),
    ),
    Capability(
        id="writing",
        name="Roteiro e copy",
        description="Cria roteiros, copies, legendas, anuncios e reescritas em estilo.",
        legacy_sources=("Ogilvy", "Olivetto", "ClaraCopy", "save_script_tool"),
    ),
    Capability(
        id="creation",
        name="Criacao visual",
        description="Gera carrossel, imagem, thumbnail, capa e assets visuais.",
        legacy_sources=("GaryV", "Scher", "generate_carousel_tool", "generate_image_tool"),
    ),
    Capability(
        id="social_media",
        name="Social media",
        description="Planeja calendario editorial, pilares de conteudo, news radar, referencias sociais e distribuicao em formatos.",
        legacy_sources=("app/api/v1/endpoints/calendar.py", "app/api/v1/endpoints/news.py", "app/workers/social_tasks.py", "app/knowledge/social-media-calendar"),
    ),
    Capability(
        id="video",
        name="Video",
        description="Transcreve, detecta highlights, seleciona cortes, legenda e renderiza shorts.",
        legacy_sources=("Nolan", "Beast", "app/workers/operations", "app/knowledge/youtube-highlight-clipper"),
    ),
    Capability(
        id="memory",
        name="Memoria e biblioteca",
        description="Salva preferencias, contexto de marca, assets e aprendizados reutilizaveis.",
        legacy_sources=("app/orchestrator/memory.py", "app/services/user_memory.py", "library-panel"),
    ),
)


def list_capabilities() -> tuple[Capability, ...]:
    return CAPABILITIES


def get_capability(capability_id: str) -> Capability | None:
    return next((capability for capability in CAPABILITIES if capability.id == capability_id), None)
