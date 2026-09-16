"""Ingere noticias RSS na tabela legada `noticias`.

Exemplos:
  python scripts/ingest_rss_news.py --query "IA meteorologia" --limit 20
  python scripts/ingest_rss_news.py --query "agentes de IA OR automacao" --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.news_digest.rss_service import fetch_rss_news, rss_item_to_article_row  # noqa: E402


def _existing_urls(client: Any, urls: Iterable[str]) -> set[str]:
    found: set[str] = set()
    for url in [u for u in urls if u]:
        try:
            res = client.table("noticias").select("url").eq("url", url).limit(1).execute()
            if res.data:
                found.add(url)
        except Exception:
            # Se a consulta falhar, deixa a insercao tentar e reportar o erro real.
            continue
    return found


def ingest(query: str, *, limit: int, dry_run: bool = False) -> Dict[str, Any]:
    items = fetch_rss_news(query=query, limit=limit)
    rows = [rss_item_to_article_row(item) for item in items if item.get("url")]

    if dry_run:
        return {"query": query, "fetched": len(items), "inserted": 0, "skipped": 0, "items": items}

    from app.core.supabase import get_supabase

    client = get_supabase()
    existing = _existing_urls(client, [row.get("url") for row in rows])
    new_rows: List[Dict[str, Any]] = [row for row in rows if row.get("url") not in existing]

    inserted = 0
    if new_rows:
        res = client.table("noticias").insert(new_rows).execute()
        inserted = len(res.data or new_rows)

    return {
        "query": query,
        "fetched": len(items),
        "inserted": inserted,
        "skipped": len(rows) - len(new_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingere noticias RSS por nicho/palavra-chave.")
    parser.add_argument("--query", "-q", required=True, help="Nicho ou palavra-chave. Ex: 'IA meteorologia'")
    parser.add_argument("--limit", "-l", type=int, default=20, help="Quantidade maxima de noticias")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que buscaria, sem salvar")
    args = parser.parse_args()

    result = ingest(args.query, limit=max(1, min(args.limit, 100)), dry_run=args.dry_run)
    print(f"query={result['query']!r} fetched={result['fetched']} inserted={result['inserted']} skipped={result['skipped']}")

    if args.dry_run:
        for item in result["items"]:
            print(f"- {item['title']} | {item['source_label']} | {item.get('url')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
