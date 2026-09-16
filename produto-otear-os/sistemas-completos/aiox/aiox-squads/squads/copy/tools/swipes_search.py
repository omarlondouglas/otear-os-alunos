"""
Swipes DB Search CLI — para uso dos agentes de copy.

Uso:
    python swipes_search.py "lead saude masculina" --author clayton_makepeace --count 5
    python swipes_search.py "headline curiosidade" --language pt --count 8
    python swipes_search.py --list-authors

Retorna JSON com os chunks mais relevantes.
"""
import os, sys, json, argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Load env from aiox-core
ROOT = Path(__file__).resolve().parents[4]  # d:/AIOX/
ENV_PATH = ROOT / "aiox-core" / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except ImportError:
    # fallback manual
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not all([OPENAI_KEY, SUPA_URL, SUPA_KEY]):
    print(json.dumps({"error": "Missing env vars (OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY)"}))
    sys.exit(1)

from openai import OpenAI
from supabase import create_client

oai = OpenAI(api_key=OPENAI_KEY)
sb = create_client(SUPA_URL, SUPA_KEY)
EMBED_MODEL = "text-embedding-3-small"


def embed(text: str) -> list[float]:
    r = oai.embeddings.create(model=EMBED_MODEL, input=text)
    return r.data[0].embedding


def search(query: str, author: str | None = None, language: str | None = None,
           count: int = 10, threshold: float = 0.3) -> list[dict]:
    qv = embed(query)
    r = sb.rpc("match_swipes", {
        "query_embedding": qv,
        "match_count": count,
        "filter_author": author,
        "filter_language": language,
        "similarity_threshold": threshold,
    }).execute()
    return r.data or []


def list_authors() -> list[dict]:
    r = sb.rpc("list_swipe_authors").execute()
    return r.data or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="Query semantica")
    ap.add_argument("--author", default=None, help="Filtrar por autor (ex: clayton_makepeace)")
    ap.add_argument("--language", choices=["en", "pt", "mixed"], default=None)
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--list-authors", action="store_true")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    args = ap.parse_args()

    if args.list_authors:
        data = list_authors()
        if args.format == "json":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"{'CHUNKS':>7}  AUTHOR")
            for row in data:
                print(f"{row['chunks']:>7}  {row['author']}")
        return

    if not args.query:
        ap.error("query obrigatoria (ou use --list-authors)")

    results = search(args.query, args.author, args.language, args.count, args.threshold)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f"\nQuery: {args.query}")
    if args.author: print(f"Author: {args.author}")
    if args.language: print(f"Language: {args.language}")
    print(f"Results: {len(results)}\n" + "=" * 60)

    for i, r in enumerate(results, 1):
        sim = r.get("similarity", 0)
        author = r.get("author", "?")
        source = r.get("source_file", "?")
        page = r.get("page")
        page_str = f" | p{page}" if page else ""
        content = r.get("content", "").strip()
        print(f"\n[{i}] sim={sim:.3f} | {author} | {source}{page_str}")
        print("-" * 60)
        # Truncate content pra preview
        if len(content) > 800:
            print(content[:800] + "\n... [truncated]")
        else:
            print(content)


if __name__ == "__main__":
    main()
