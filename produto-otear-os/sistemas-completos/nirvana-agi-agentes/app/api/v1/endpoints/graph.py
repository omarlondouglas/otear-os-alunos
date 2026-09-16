"""
Graph API — devolve o "Mapa de Conexoes" do cliente.

Frontend (aba Conexoes) consome via GET /api/v1/graph/data e renderiza
com react-force-graph.
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/data")
async def graph_data(
    include_videos: bool = Query(True),
    include_content: bool = Query(True),
    include_memory: bool = Query(True),
    max_videos_per_creator: int = Query(5, ge=0, le=20),
) -> Dict[str, Any]:
    """Retorna {nodes, edges, stats, node_types_meta}.

    Filtros via query string para o frontend toggar tipos de no.
    """
    from app.services.graph_builder import build_graph
    return build_graph(
        include_videos=include_videos,
        include_content=include_content,
        include_memory=include_memory,
        max_videos_per_creator=max_videos_per_creator,
    )


@router.get("/stats")
async def graph_stats() -> Dict[str, Any]:
    """Versao lightweight — so o resumo (sem nodes/edges)."""
    from app.services.graph_builder import build_graph
    g = build_graph(include_videos=False, include_content=True, include_memory=True)
    return {"stats": g["stats"]}
