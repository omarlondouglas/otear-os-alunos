"""
User Memory Service
Le e atualiza USER.md / MEMORY.md do vault Obsidian. Esses textos sao injetados
no system prompt de todos os agentes (Hermes + Beast/Nolan/etc.).

Esquema dos arquivos: ver {OTEAR_VAULT_ROOT}/.system/README.md
- USER.md : 1500 chars, perfil do usuario
- MEMORY.md : 2200 chars, memoria do agente
- Secoes delimitadas por 'Â§ <nome>'
- Frontmatter YAML opcional

Uso:
    from app.services.user_memory import get_memory_prompt, add_memory_entry

    # No startup do agente:
    instructions = [get_memory_prompt(), *outras_instrucoes]

    # Quando agente decide persistir algo:
    add_memory_entry("workarounds aprendidos", "fix do bug X via Y")
"""
from __future__ import annotations

import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VAULT_PATH = Path(os.getenv("VAULT_PATH", "{OTEAR_VAULT_ROOT}"))
SYSTEM_DIR = VAULT_PATH / ".system"
USER_FILE = SYSTEM_DIR / "USER.md"
MEMORY_FILE = SYSTEM_DIR / "MEMORY.md"

USER_CHAR_LIMIT = 1500
MEMORY_CHAR_LIMIT = 2200
CONSOLIDATE_THRESHOLD = 0.80  # consolida quando passa de 80%

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_SECTION_RE = re.compile(r"^Â§\s+(.+?)$", re.MULTILINE)

# Cache simples com invalidacao por mtime
_cache_lock = threading.Lock()
_cache: Dict[Path, Tuple[float, "MemoryDoc"]] = {}


@dataclass
class MemoryDoc:
    """Documento parseado de USER.md ou MEMORY.md."""
    path: Path
    frontmatter: str  # YAML bruto
    sections: Dict[str, str]  # nome -> corpo da secao
    char_limit: int

    @property
    def body_chars(self) -> int:
        return sum(len(name) + len(body) + 4 for name, body in self.sections.items())

    @property
    def usage_pct(self) -> float:
        return self.body_chars / self.char_limit if self.char_limit else 0.0

    def needs_consolidation(self) -> bool:
        return self.usage_pct >= CONSOLIDATE_THRESHOLD

    def to_markdown(self) -> str:
        out = []
        if self.frontmatter:
            out.append(f"---\n{self.frontmatter}\n---\n")
        for name, body in self.sections.items():
            out.append(f"Â§ {name}\n{body.rstrip()}\n")
        return "\n".join(out).strip() + "\n"


def _parse(path: Path, char_limit: int) -> MemoryDoc:
    if not path.exists():
        return MemoryDoc(path=path, frontmatter="", sections={}, char_limit=char_limit)
    text = path.read_text(encoding="utf-8")

    frontmatter = ""
    m = _FRONTMATTER_RE.match(text)
    if m:
        frontmatter = m.group(1).strip()
        text = text[m.end():]

    sections: Dict[str, str] = {}
    matches = list(_SECTION_RE.finditer(text))
    for i, mt in enumerate(matches):
        name = mt.group(1).strip()
        start = mt.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections[name] = body

    return MemoryDoc(path=path, frontmatter=frontmatter, sections=sections, char_limit=char_limit)


def _load(path: Path, char_limit: int) -> MemoryDoc:
    """Carrega documento com cache por mtime."""
    with _cache_lock:
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            mtime = 0.0
        cached = _cache.get(path)
        if cached and cached[0] == mtime:
            return cached[1]
        doc = _parse(path, char_limit)
        _cache[path] = (mtime, doc)
        return doc


def _write(doc: MemoryDoc) -> None:
    doc.path.parent.mkdir(parents=True, exist_ok=True)
    doc.path.write_text(doc.to_markdown(), encoding="utf-8")
    with _cache_lock:
        _cache[doc.path] = (doc.path.stat().st_mtime, doc)


# â”€â”€â”€ API publica â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def get_user_profile() -> MemoryDoc:
    return _load(USER_FILE, USER_CHAR_LIMIT)


def get_agent_memory() -> MemoryDoc:
    return _load(MEMORY_FILE, MEMORY_CHAR_LIMIT)


def is_onboarding_pending() -> bool:
    """True se USER.md esta no estado inicial (pre-onboarding)."""
    doc = get_user_profile()
    if "pending_onboarding" in doc.frontmatter:
        return True
    # heuristica: todas as secoes ainda comecam com '[Aguardando onboarding'
    return all(body.startswith("[Aguardando onboarding") for body in doc.sections.values())


def get_memory_prompt() -> str:
    """Texto pronto pra prefixar ao system prompt dos agentes."""
    user = get_user_profile()
    memory = get_agent_memory()
    parts = []
    if user.sections:
        parts.append("## User Profile (USER.md)")
        for name, body in user.sections.items():
            parts.append(f"### {name}\n{body}")
    if memory.sections:
        parts.append("\n## Agent Memory (MEMORY.md)")
        for name, body in memory.sections.items():
            parts.append(f"### {name}\n{body}")
    return "\n".join(parts).strip()


def update_section(doc_kind: str, section: str, body: str) -> MemoryDoc:
    """Substitui o corpo de uma secao existente, ou cria nova se nao existir.

    doc_kind: 'user' | 'memory'
    """
    if doc_kind == "user":
        doc = get_user_profile()
    elif doc_kind == "memory":
        doc = get_agent_memory()
    else:
        raise ValueError(f"doc_kind must be 'user' or 'memory', got {doc_kind!r}")
    doc.sections[section] = body.strip()
    _write(doc)
    return doc


def add_memory_entry(section: str, entry: str) -> MemoryDoc:
    """Adiciona uma entrada em MEMORY.md. Cria a secao se nao existir."""
    doc = get_agent_memory()
    existing = doc.sections.get(section, "").strip()
    new_body = f"{existing}\n{entry.strip()}" if existing else entry.strip()
    doc.sections[section] = new_body
    _write(doc)
    return doc


def complete_onboarding(answers: Dict[str, str]) -> MemoryDoc:
    """Recebe as 5 respostas do onboarding e popula USER.md.

    answers keys esperadas:
      - identidade
      - estilo de comunicacao
      - preferencias tecnicas
      - workflow
      - objetivos
    """
    doc = get_user_profile()
    for section, body in answers.items():
        doc.sections[section] = body.strip()
    # remove flag de pending no frontmatter
    doc.frontmatter = re.sub(
        r"status:\s*pending_onboarding",
        f"status: active",
        doc.frontmatter,
    )
    _write(doc)
    return doc


def consolidation_needed() -> List[str]:
    """Retorna lista com 'user'/'memory' indicando quais arquivos passaram de 80%."""
    out = []
    if get_user_profile().needs_consolidation():
        out.append("user")
    if get_agent_memory().needs_consolidation():
        out.append("memory")
    return out


def vault_status() -> Dict[str, object]:
    """Resumo legivel pra dashboard / health check."""
    user = get_user_profile()
    memory = get_agent_memory()
    return {
        "vault_path": str(VAULT_PATH),
        "system_dir_exists": SYSTEM_DIR.exists(),
        "user": {
            "sections": list(user.sections.keys()),
            "chars": user.body_chars,
            "limit": user.char_limit,
            "usage_pct": round(user.usage_pct * 100, 1),
            "onboarding_pending": is_onboarding_pending(),
        },
        "memory": {
            "sections": list(memory.sections.keys()),
            "chars": memory.body_chars,
            "limit": memory.char_limit,
            "usage_pct": round(memory.usage_pct * 100, 1),
        },
    }
