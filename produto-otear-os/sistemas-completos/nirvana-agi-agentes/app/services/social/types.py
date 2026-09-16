"""Tipos compartilhados pelo pipeline de extracao de perfis sociais."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SocialPost:
    """Post individual retornado por um lister (TikTok/Instagram).

    Campos opcionais ficam None quando a fonte nao expoe.
    """
    post_id: str                       # id unico no plataforma
    platform: str                      # "tiktok" | "instagram"
    handle: str                        # @do criador
    url: str                           # URL do post no app
    play_url: Optional[str] = None     # URL direta do .mp4 (quando disponivel)
    cover_url: Optional[str] = None    # thumbnail
    title: str = ""                    # caption/description
    duration: float = 0.0              # segundos
    posted_at: Optional[str] = None    # ISO date
    play_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None


@dataclass
class CreatorAnalysis:
    """Resultado da analise LLM agregada de N posts de um criador."""
    handle: str
    platform: str
    posts_analyzed: int
    hook_patterns: List[str] = field(default_factory=list)
    narrative_arc: str = ""
    vocabulary: List[str] = field(default_factory=list)
    emotional_triggers: List[str] = field(default_factory=list)
    cta_style: str = ""
    tone: str = ""
    pacing: str = ""
    visual_format: str = ""
    summary: str = ""  # 2-3 linhas livres


@dataclass
class PostScriptAnalysis:
    """Analise detalhada de roteiro de um post individual."""
    hook_literal: str = ""
    hook_type: str = ""
    script_breakdown_markdown: str = ""
    reusable_patterns: List[str] = field(default_factory=list)


@dataclass
class ExtractionMeta:
    """Metadata salvo em _meta.json para o frontend mostrar progresso."""
    handle: str
    platform: str
    kind: str  # "self" | "inspiration"
    status: str  # "pending" | "extracting" | "done" | "failed"
    posts_total: int = 0
    posts_done: int = 0
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    last_error: Optional[str] = None
    job_id: Optional[str] = None
