from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Intent(str, Enum):
    CAROUSEL = "carousel"
    VIDEO_EDIT = "video_edit"
    VIDEO_STATUS = "video_status"
    IMAGE = "image"
    LINKEDIN_POST = "linkedin_post"
    SCRIPT = "script"
    STRATEGY = "strategy"
    MEMORY = "memory"
    GENERAL = "general"


@dataclass
class ClientContext:
    user_id: Optional[str] = None
    org_id: Optional[str] = None
    brand_id: Optional[str] = None
    user_context: str = ""
    brand_context: str = ""
    vault_context: str = ""

    def as_prompt(self) -> str:
        parts = []
        if self.brand_context:
            parts.append(f"## Marca ativa\n{self.brand_context}")
        if self.user_context:
            parts.append(f"## Perfil do usuario\n{self.user_context}")
        if self.vault_context:
            parts.append(f"## Memoria operacional\n{self.vault_context}")
        return "\n\n".join(parts).strip()


@dataclass
class OrchestratorResult:
    response: str
    data: Dict[str, Any] = field(default_factory=dict)
