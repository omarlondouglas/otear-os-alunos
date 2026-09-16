"""
Parser de identificadores de rede social.

Aceita varios formatos que o cliente pode digitar e normaliza para (platform, handle).

Exemplos:
    parse_social_handle("@marlon")
        -> ("unknown", "@marlon")
    parse_social_handle("instagram.com/marlon")
        -> ("instagram", "@marlon")
    parse_social_handle("https://www.tiktok.com/@hormozi")
        -> ("tiktok", "@hormozi")
    parse_social_handle("https://tiktok.com/@x/video/12345")
        -> ("tiktok", "@x")

    parse_inspirations("@a, https://instagram.com/b\n@c")
        -> [("unknown","@a"), ("instagram","@b"), ("unknown","@c")]
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from urllib.parse import urlparse


@dataclass(frozen=True)
class SocialHandle:
    platform: str   # "instagram" | "tiktok" | "youtube" | "unknown"
    handle: str     # ex: "@marlon"

    def to_url(self) -> Optional[str]:
        if self.platform == "instagram":
            return f"https://www.instagram.com/{self.handle.lstrip('@')}/"
        if self.platform == "tiktok":
            return f"https://www.tiktok.com/{self.handle}"
        if self.platform == "youtube":
            return f"https://www.youtube.com/{self.handle}"
        return None


def _normalize_handle(raw: str) -> str:
    raw = raw.strip().strip("/").lstrip("@")
    return f"@{raw}" if raw else ""


def parse_social_handle(text: str) -> Optional[SocialHandle]:
    """Detecta plataforma e normaliza handle. Retorna None se nao reconhecer."""
    if not text or not text.strip():
        return None

    t = text.strip()

    # URL completa
    if t.startswith("http://") or t.startswith("https://") or "://" in t:
        try:
            url = urlparse(t)
            host = url.netloc.lower().replace("www.", "")
            path_parts = [p for p in url.path.split("/") if p]
            if "instagram.com" in host:
                if path_parts:
                    return SocialHandle("instagram", _normalize_handle(path_parts[0]))
            if "tiktok.com" in host:
                # vt.tiktok.com/abc -> shortlink, nao da pra extrair handle
                if host.startswith("vt.") or host.startswith("vm."):
                    return SocialHandle("tiktok", "@unknown_shortlink")
                if path_parts:
                    h = path_parts[0]
                    if h.startswith("@"):
                        return SocialHandle("tiktok", _normalize_handle(h))
            if "youtube.com" in host:
                if path_parts and path_parts[0].startswith("@"):
                    return SocialHandle("youtube", _normalize_handle(path_parts[0]))
                if "channel" in path_parts or "c" in path_parts:
                    return SocialHandle("youtube", path_parts[-1])
        except Exception:
            pass

    # Sem URL — string solta
    # "instagram.com/marlon"
    m = re.match(r"^(?:www\.)?(instagram|tiktok|youtube)\.com/(.+)$", t, re.IGNORECASE)
    if m:
        platform = m.group(1).lower()
        rest = m.group(2).strip("/").split("/")[0]
        return SocialHandle(platform, _normalize_handle(rest))

    # "@marlon" ou "marlon" — plataforma desconhecida
    if t.startswith("@") or re.match(r"^[\w.-]+$", t):
        return SocialHandle("unknown", _normalize_handle(t))

    return None


def parse_inspirations(text: str, max_items: int = 3) -> List[SocialHandle]:
    """Quebra texto livre em ate `max_items` SocialHandle.

    Aceita virgulas, ponto-e-virgulas ou linhas como separadores.
    """
    if not text:
        return []
    parts = re.split(r"[,;\n]+", text)
    out: List[SocialHandle] = []
    seen = set()
    for p in parts:
        p = p.strip()
        if not p:
            continue
        h = parse_social_handle(p)
        if h is None:
            continue
        key = (h.platform, h.handle.lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
        if len(out) >= max_items:
            break
    return out


def serialize_handles(handles: List[SocialHandle]) -> str:
    import json
    return json.dumps(
        [{"platform": h.platform, "handle": h.handle} for h in handles],
        ensure_ascii=False,
    )


def deserialize_handles(json_str: str) -> List[SocialHandle]:
    import json
    if not json_str:
        return []
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return []
    return [SocialHandle(d["platform"], d["handle"]) for d in data if "handle" in d]
