#!/usr/bin/env python3
"""
query_supabase.py — Query O Tear Supabase tables safely.

Usage:
    python3 query_supabase.py <table> [limit] [--order <column>]

Examples:
    python3 query_supabase.py noticias 10
    python3 query_supabase.py noticias 5 --order publicado_em
    python3 query_supabase.py videos_do_youtube 20
    python3 query_supabase.py ideias_de_conteudo 5

Tables and their sort columns:
    noticias           → publicado_em (or created_at)
    noticias_perplexity → data_criacao
    posts_do_reddit    → date (string, limited sort)
    videos_do_youtube  → created_at
    ideias_de_conteudo → id (no timestamp column)
"""

import sys
import json
import urllib.request

SUPABASE_URL = "https://jrkuuusrjzzpdjkulvmf.supabase.co"

# ── Load key from memory or env ──────────────────────────────────────
import os

def get_key():
    # Try environment variable first
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if key:
        return key
    # Try reading from a local file
    key_file = os.path.expanduser("~/.hermes/.supabase_key")
    if os.path.exists(key_file):
        return open(key_file).read().strip()
    print("ERROR: No Supabase key found.", file=sys.stderr)
    print("Set SUPABASE_SERVICE_ROLE_KEY env var or save key to ~/.hermes/.supabase_key", file=sys.stderr)
    sys.exit(1)

# → When running, replace this with the actual key from Hermes memory
SUPABASE_KEY = get_key()

# ── Column mappings per table (actual schema) ────────────────────────
TABLE_COLUMNS = {
    "noticias": {
        "sort": "publicado_em",
        "columns": ["id", "titulo", "resumo", "conteudo", "url", "categoria", "tags", "fonte", "publicado_em", "created_at"],
    },
    "noticias_perplexity": {
        "sort": "data_criacao",
        "columns": ["id", "headline", "resumo", "fonte", "data_criacao", "data_atualizacao"],
    },
    "posts_do_reddit": {
        "sort": "date",
        "columns": ["id", "titulo", "url", "resumo", "updates_engagement", "date"],
    },
    "videos_do_youtube": {
        "sort": "created_at",
        "columns": ["id", "titulo", "descricao", "canal", "url", "created_at"],
    },
    "ideias_de_conteudo": {
        "sort": "id",
        "columns": ["id", "idea_title", "description", "porque"],
    },
}


def query_table(table: str, limit: int = 10, order_col: str = None) -> list:
    if table not in TABLE_COLUMNS:
        print(f"WARNING: Unknown table '{table}'. Querying without column filter.", file=sys.stderr)
        cols = "*"
        sort_col = order_col or "created_at"
    else:
        info = TABLE_COLUMNS[table]
        cols = ",".join(info["columns"])
        sort_col = order_col or info["sort"]

    url = f"{SUPABASE_URL}/rest/v1/{table}?select={cols}&order={sort_col}.desc&limit={limit}"
    req = urllib.request.Request(url, headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    table = args[0]
    limit = 10
    order_col = None

    i = 1
    while i < len(args):
        if args[i] == "--order" and i + 1 < len(args):
            order_col = args[i + 1]
            i += 2
        elif args[i].isdigit():
            limit = int(args[i])
            i += 1
        else:
            i += 1

    data = query_table(table, limit, order_col)
    if not data:
        print(f"No data returned from '{table}'.")
        return

    print(f"=== {table} ({len(data)} results) ===\n")
    for i, row in enumerate(data, 1):
        # Print a summary line
        title = (
            row.get("titulo")
            or row.get("headline")
            or row.get("idea_title")
            or row.get("titulo")
            or "—"
        )
        date = (
            row.get("publicado_em")
            or row.get("data_criacao")
            or row.get("created_at")
            or row.get("date")
            or ""
        )[:10]
        print(f"{i}. [{date}] {title}")

        # Print all fields
        for k, v in row.items():
            if v and k not in ("titulo", "headline", "idea_title"):
                val = str(v)[:120]
                print(f"   {k}: {val}")
        print()


if __name__ == "__main__":
    main()
