"""
Graph Builder â€” monta o "Mapa de Conexoes" do cliente.

Coleta dados de:
  - USER.md (vault) â€” perfil do cliente
  - MEMORY.md (vault) â€” decisoes/ambiente do agente
  - references/<handle>/_profile.md â€” criadores que inspiram + estilo extraido
  - references/<handle>/<post>.md â€” videos analisados de cada criador
  - VideoJob (PostgreSQL) â€” conteudos gerados pelo cliente

Retorna estrutura `{nodes, edges}` consumivel por libs de visualizacao
(react-force-graph, vis.js, cytoscape).

Apelo do feature: cliente ve TUDO conectado â€” quem inspira ele, quais
hooks aparecem em multiplos creators, quais ideias ja viraram conteudo.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "{OTEAR_VAULT_ROOT}"))
REFERENCES_DIR = Path(os.environ.get("REFERENCES_PATH", str(VAULT_PATH / "references")))
SYSTEM_DIR = VAULT_PATH / ".system"


# â”€â”€â”€ Tipos de no â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

NODE_TYPES = {
    "you":         {"color": "#A3F12E", "size": 24, "label": "Voce"},
    "inspiration": {"color": "#FF8C00", "size": 18, "label": "Inspiracao"},
    "video":       {"color": "#4FC3F7", "size": 8,  "label": "Video"},
    "hook":        {"color": "#AB47BC", "size": 10, "label": "Hook"},
    "trigger":     {"color": "#FF69B4", "size": 8,  "label": "Gatilho"},
    "vocab":       {"color": "#FFD700", "size": 6,  "label": "Vocab"},
    "content":     {"color": "#00FFFF", "size": 14, "label": "Conteudo"},
    "strategy":    {"color": "#7CFFB2", "size": 20, "label": "Estrategia"},
    "pillar":      {"color": "#FDE047", "size": 15, "label": "Pilar"},
    "news":        {"color": "#38BDF8", "size": 10, "label": "Noticia"},
    "planned":     {"color": "#FB7185", "size": 12, "label": "Planejado"},
    "memory":      {"color": "#888888", "size": 10, "label": "Memoria"},
    "section":     {"color": "#555555", "size": 6,  "label": "Secao"},
}

CONTENT_PILLARS = {
    "noticias": {
        "label": "Noticias",
        "role": "Tendencias, mudancas de mercado, novas ferramentas, IA, plataformas e sinais oportunos.",
        "keywords": [
            "noticia", "lanc", "anuncia", "atualiza", "novo", "nova", "mercado",
            "tendencia", "alerta", "mudanca", "openai", "google", "meta", "ia",
            "inteligencia artificial", "modelo", "regulacao", "pesquisa", "estudo",
        ],
    },
    "tutorial": {
        "label": "Tutorial",
        "role": "Educacao pratica, passo a passo, processos, templates, checklists e demonstracoes.",
        "keywords": [
            "como", "passo", "guia", "tutorial", "checklist", "template", "ferramenta",
            "automatizar", "processo", "workflow", "aprenda", "dica", "exemplo",
        ],
    },
    "vlog": {
        "label": "Vlog",
        "role": "Bastidores, rotina, experimentos, ponto de vista de operador e prova de trabalho.",
        "keywords": [
            "bastidor", "rotina", "diario", "experimento", "testei", "aprendi",
            "processo", "cliente", "prova", "making of", "dia", "decisao",
        ],
    },
    "review_sincero": {
        "label": "Review sincero",
        "role": "Avaliacao honesta de ferramentas, tendencias, campanhas, produtos e metodos.",
        "keywords": [
            "review", "analise", "vale a pena", "veredito", "comparativo", "melhor",
            "pior", "falha", "funciona", "testamos", "avaliacao", "benchmark",
        ],
    },
}


# â”€â”€â”€ Parsers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
_SECTION_RE = re.compile(r"^Â§\s+(.+?)$", re.MULTILINE)


def _parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    fm: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, text[m.end():]


def _parse_user_md() -> Dict[str, Any]:
    path = SYSTEM_DIR / "USER.md"
    if not path.exists():
        return {"identidade": "Voce", "sections": {}}
    text = path.read_text(encoding="utf-8")
    sections: Dict[str, str] = {}
    for m in _SECTION_RE.finditer(text):
        name = m.group(1).strip()
        start = m.end()
        next_match = _SECTION_RE.search(text, start)
        end = next_match.start() if next_match else len(text)
        sections[name] = text[start:end].strip()[:500]
    return {
        "identidade": sections.get("identidade", "Voce") or "Voce",
        "sections": sections,
    }


def _parse_memory_md() -> Dict[str, str]:
    path = SYSTEM_DIR / "MEMORY.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    sections: Dict[str, str] = {}
    for m in _SECTION_RE.finditer(text):
        name = m.group(1).strip()
        start = m.end()
        next_match = _SECTION_RE.search(text, start)
        end = next_match.start() if next_match else len(text)
        sections[name] = text[start:end].strip()[:300]
    return sections


def _parse_creator_profile(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(text)

    sections: Dict[str, str] = {}
    matches = list(_HEADING_RE.finditer(body))
    for i, m in enumerate(matches):
        title = m.group(2).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()

    def _bullets(s: str) -> List[str]:
        return [
            ln.lstrip("- ").strip()
            for ln in s.splitlines()
            if ln.strip().startswith("-")
        ][:8]

    def _csv(s: str) -> List[str]:
        clean = s.strip().strip("_")
        if not clean or clean.startswith("(nao"):
            return []
        return [t.strip() for t in clean.split(",") if t.strip()][:6]

    return {
        "handle": fm.get("handle", path.parent.name),
        "platform": fm.get("platform", "unknown"),
        "kind": fm.get("kind", "inspiration"),
        "posts_analyzed": int(fm.get("posts_analyzed", "0") or 0),
        "hook_patterns": _bullets(sections.get("hook patterns", "")),
        "vocabulary": _csv(sections.get("vocabulario-chave", "")),
        "emotional_triggers": _csv(sections.get("gatilhos emocionais", "")),
        "tone": (sections.get("tom", "") or "")[:120],
        "summary": (sections.get("resumo", "") or "")[:200],
    }


def _list_creator_videos(creator_dir: Path, limit: int = 5) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in sorted(creator_dir.glob("*.md"))[:50]:
        if p.name.startswith("_"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
            fm, _ = _parse_frontmatter(text)
            out.append({
                "post_id": fm.get("post_id", p.stem),
                "url": fm.get("url", ""),
                "duration": fm.get("duration", ""),
            })
            if len(out) >= limit:
                break
        except Exception:
            continue
    return out


def _list_user_content_jobs(limit: int = 30) -> List[Dict[str, Any]]:
    """Le os ultimos jobs do PostgreSQL (conteudo gerado pelo cliente)."""
    try:
        from app.core.database import SessionLocal
        from app.models.job import VideoJob, JobStatus
        db = SessionLocal()
        try:
            rows = (
                db.query(VideoJob)
                .filter(VideoJob.status == JobStatus.COMPLETED)
                .order_by(VideoJob.completed_at.desc())
                .limit(limit)
                .all()
            )
            out = []
            for r in rows:
                op_types = []
                try:
                    if r.operations:
                        op_types = [o.get("type") for o in r.operations if isinstance(o, dict)]
                except Exception:
                    pass
                preset_name = None
                for o in (r.operations or []):
                    if isinstance(o, dict) and o.get("type") == "preset":
                        preset_name = (o.get("params") or {}).get("name")
                        break
                out.append({
                    "id": str(r.id),
                    "preset": preset_name or (op_types[0] if op_types else "edit"),
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                })
            return out
        finally:
            db.close()
    except Exception:
        return []


def _classify_content_pillar(*parts: Any) -> str:
    text = " ".join(str(part or "") for part in parts).casefold()
    scores = {
        slug: sum(1 for keyword in meta["keywords"] if keyword in text)
        for slug, meta in CONTENT_PILLARS.items()
    }
    best_slug, best_score = max(scores.items(), key=lambda item: item[1])
    return best_slug if best_score > 0 else "noticias"


def _list_news_signals(limit: int = 24) -> List[Dict[str, Any]]:
    """Le o feed consolidado salvo no Supabase para conectar noticias aos pilares."""
    try:
        from app.core.supabase import get_supabase
        from app.services.news_digest.feed_service import build_news_feed

        feed = build_news_feed(
            get_supabase(),
            limit=limit,
            include_rss_fallback=False,
        )
        return list(feed.get("items") or [])[:limit]
    except Exception:
        return []


def _list_planned_calendar(limit: int = 20) -> List[Dict[str, Any]]:
    """Le entradas recentes do calendario editorial para conectar planejamento aos pilares."""
    try:
        from app.core.supabase import get_supabase

        response = (
            get_supabase()
            .table("content_calendar")
            .select("id,title,content_type,platform,scheduled_at,status,notes")
            .order("scheduled_at", desc=False)
            .limit(limit)
            .execute()
        )
        return list(response.data or [])
    except Exception:
        return []


# â”€â”€â”€ Builder principal â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_graph(
    include_videos: bool = True,
    include_content: bool = True,
    include_memory: bool = True,
    max_videos_per_creator: int = 5,
) -> Dict[str, Any]:
    """Monta o grafo completo {nodes, edges, stats}."""
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # 1. No central â€” Voce
    user = _parse_user_md()
    you_id = "you"
    nodes.append({
        "id": you_id,
        "type": "you",
        "label": user["identidade"][:50],
        "data": {"sections": user["sections"]},
    })

    # 1.5 Estrategia macro de conteudo e pilares editoriais.
    strategy_id = "strategy:content"
    nodes.append({
        "id": strategy_id,
        "type": "strategy",
        "label": "Estrategia de Conteudo",
        "data": {
            "publico": user["sections"].get("publico", "")[:300],
            "niche": user["sections"].get("news_radar", "")[:300],
            "mix": {
                "noticias": "30%",
                "tutorial": "25%",
                "vlog": "25%",
                "review_sincero": "20%",
            },
        },
    })
    edges.append({"source": you_id, "target": strategy_id, "kind": "owns_strategy"})

    pillar_ids: Dict[str, str] = {}
    for slug, meta in CONTENT_PILLARS.items():
        pillar_id = f"pillar:{slug}"
        pillar_ids[slug] = pillar_id
        nodes.append({
            "id": pillar_id,
            "type": "pillar",
            "label": meta["label"],
            "data": {"role": meta["role"], "keywords": meta["keywords"][:8]},
        })
        edges.append({"source": strategy_id, "target": pillar_id, "kind": "defines_pillar"})

    # 2. Memorias (cards conectados a Voce)
    if include_memory:
        for sec_name, content in _parse_memory_md().items():
            mem_id = f"memory:{sec_name}"
            nodes.append({
                "id": mem_id,
                "type": "memory",
                "label": sec_name,
                "data": {"content": content},
            })
            edges.append({"source": you_id, "target": mem_id, "kind": "remembers"})

    # 3. Criadores (inspirations + self) com hooks/triggers/vocab
    if REFERENCES_DIR.exists():
        for creator_dir in sorted(REFERENCES_DIR.iterdir()):
            if not creator_dir.is_dir() or creator_dir.name.startswith("."):
                continue
            handle = creator_dir.name
            profile = _parse_creator_profile(creator_dir / "_profile.md")
            kind = profile.get("kind", "inspiration")
            creator_node_type = "you" if kind == "self" else "inspiration"
            creator_id = f"creator:{handle}"

            # Se kind=self, nao duplica â€” usa o no Voce
            if kind == "self":
                # Conecta o no Voce ao perfil extraido
                edges.append({
                    "source": you_id,
                    "target": creator_id,
                    "kind": "is_extracted_as",
                })

            nodes.append({
                "id": creator_id,
                "type": creator_node_type if kind != "self" else "inspiration",  # cor laranja pra distinguir do central
                "label": handle,
                "data": {
                    "platform": profile.get("platform", "unknown"),
                    "summary": profile.get("summary", ""),
                    "tone": profile.get("tone", ""),
                    "posts_analyzed": profile.get("posts_analyzed", 0),
                },
            })

            if kind != "self":
                edges.append({
                    "source": you_id,
                    "target": creator_id,
                    "kind": "inspires",
                })

            # Hooks
            for i, hook in enumerate(profile.get("hook_patterns", [])):
                hook_id = f"hook:{handle}:{i}"
                nodes.append({
                    "id": hook_id,
                    "type": "hook",
                    "label": hook[:60],
                    "data": {"full": hook, "creator": handle},
                })
                edges.append({"source": creator_id, "target": hook_id, "kind": "uses_hook"})

            # Gatilhos emocionais
            for trig in profile.get("emotional_triggers", []):
                trig_id = f"trigger:{trig.lower()}"
                # Reusa nos de gatilho cross-creators (mesmo trigger conecta multiplos)
                if not any(n["id"] == trig_id for n in nodes):
                    nodes.append({
                        "id": trig_id,
                        "type": "trigger",
                        "label": trig,
                        "data": {},
                    })
                edges.append({"source": creator_id, "target": trig_id, "kind": "activates"})

            # Vocabulario chave (so 3 mais fortes pra nao poluir)
            for word in profile.get("vocabulary", [])[:3]:
                word_id = f"vocab:{word.lower()}"
                if not any(n["id"] == word_id for n in nodes):
                    nodes.append({
                        "id": word_id,
                        "type": "vocab",
                        "label": word,
                        "data": {},
                    })
                edges.append({"source": creator_id, "target": word_id, "kind": "uses_word"})

            # Videos (limitado)
            if include_videos:
                for v in _list_creator_videos(creator_dir, limit=max_videos_per_creator):
                    vid_id = f"video:{handle}:{v['post_id']}"
                    nodes.append({
                        "id": vid_id,
                        "type": "video",
                        "label": v["post_id"][:20],
                        "data": {"url": v["url"], "creator": handle},
                    })
                    edges.append({"source": creator_id, "target": vid_id, "kind": "posted"})

    # 4. Conteudos gerados pelo cliente
    if include_content:
        for job in _list_user_content_jobs(limit=20):
            pillar_slug = _classify_content_pillar(job.get("preset"))
            job_id = f"content:{job['id']}"
            nodes.append({
                "id": job_id,
                "type": "content",
                "label": job["preset"] or "edit",
                "data": {
                    "completed_at": job.get("completed_at"),
                    "pillar": pillar_slug,
                },
            })
            edges.append({"source": pillar_ids[pillar_slug], "target": job_id, "kind": "produces"})
            edges.append({"source": you_id, "target": job_id, "kind": "created"})

        for entry in _list_planned_calendar(limit=20):
            pillar_slug = _classify_content_pillar(
                entry.get("content_type"),
                entry.get("title"),
                entry.get("notes"),
            )
            planned_id = f"planned:{entry.get('id')}"
            nodes.append({
                "id": planned_id,
                "type": "planned",
                "label": (entry.get("title") or "Planejado")[:60],
                "data": {
                    "content_type": entry.get("content_type"),
                    "platform": entry.get("platform"),
                    "scheduled_at": entry.get("scheduled_at"),
                    "status": entry.get("status"),
                    "pillar": pillar_slug,
                    "notes": (entry.get("notes") or "")[:300],
                },
            })
            edges.append({"source": pillar_ids[pillar_slug], "target": planned_id, "kind": "plans"})

        for news in _list_news_signals(limit=24):
            pillar_slug = _classify_content_pillar(
                news.get("title"),
                news.get("summary"),
                news.get("category"),
                " ".join(news.get("tags") or []),
            )
            raw_id = str(news.get("id") or news.get("url") or news.get("title"))
            news_id = f"news:{raw_id[:90]}"
            nodes.append({
                "id": news_id,
                "type": "news",
                "label": (news.get("title") or "Noticia")[:70],
                "data": {
                    "source": news.get("source"),
                    "source_label": news.get("source_label"),
                    "url": news.get("url"),
                    "published_at": news.get("published_at"),
                    "summary": (news.get("summary") or "")[:300],
                    "pillar": pillar_slug,
                    "why_connected": CONTENT_PILLARS[pillar_slug]["role"],
                },
            })
            edges.append({"source": news_id, "target": pillar_ids[pillar_slug], "kind": "feeds_pillar"})

    # Stats
    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_type": {},
    }
    for n in nodes:
        t = n["type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": stats,
        "node_types_meta": NODE_TYPES,
    }
