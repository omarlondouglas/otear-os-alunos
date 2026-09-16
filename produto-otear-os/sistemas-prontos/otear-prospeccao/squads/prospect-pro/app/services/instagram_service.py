import asyncio
import sys
from pathlib import Path

SQUAD_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.instagram_scraper import run_analyzer
from scripts.lead_enricher import run_enricher
from scripts.utils.csv_handler import get_latest_file, load_leads_json


def _new_loop():
    """Create a fresh event loop with subprocess support on Windows."""
    if sys.platform == "win32":
        return asyncio.ProactorEventLoop()
    return asyncio.new_event_loop()


def _run_enricher_sync(filepath: str | None) -> dict:
    """Run the enricher in a fresh event loop (called from a thread)."""
    loop = _new_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_enricher(filepath))
    finally:
        loop.close()


def _run_analyzer_sync(filepath: str | None, posts_to_analyze: int = 12) -> dict:
    """Run the analyzer in a fresh event loop (called from a thread)."""
    loop = _new_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_analyzer(filepath, posts_to_analyze))
    finally:
        loop.close()


async def enrich_leads(filepath: str | None = None) -> dict:
    return await asyncio.to_thread(_run_enricher_sync, filepath)


async def analyze_instagram(filepath: str | None = None, posts_to_analyze: int = 12) -> dict:
    return await asyncio.to_thread(_run_analyzer_sync, filepath, posts_to_analyze)


def get_enriched_leads(filepath: str | None = None) -> list[dict]:
    if filepath is None:
        filepath = get_latest_file("enriched")
    if filepath is None:
        return []
    return load_leads_json(filepath)
