import asyncio
import sys
from pathlib import Path

# Adicionar o diretório do squad ao path
SQUAD_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.google_maps_scraper import run_scraper
from scripts.utils.csv_handler import get_latest_file, load_leads_json


def _run_scraper_sync(query: str, location: str, limit: int) -> dict:
    """Run the scraper in a fresh ProactorEventLoop (called from a thread).
    Windows requires ProactorEventLoop for subprocess support (Playwright)."""
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_scraper(query, location, limit))
    finally:
        loop.close()


async def scrape_maps(query: str, location: str, limit: int = 20) -> dict:
    result = await asyncio.to_thread(_run_scraper_sync, query, location, limit)
    return {
        "total": len(result["leads"]),
        "total_found": result.get("total_found", len(result["leads"])),
        "duplicates_skipped": result.get("duplicates_skipped", 0),
        "json_path": result["json_path"],
        "csv_path": result["csv_path"],
        "leads": result["leads"],
    }


def get_raw_leads(filepath: str | None = None) -> list[dict]:
    if filepath is None:
        filepath = get_latest_file("leads")
    if filepath is None:
        return []
    return load_leads_json(filepath)
