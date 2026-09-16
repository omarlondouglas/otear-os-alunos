# Prospect Repo Reference

## Location
- Repo: `/root/prospect/` (cloned from `omarlondouglas/prospect`)
- Venv: `/root/prospect/.venv/`
- Python: 3.11

## Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `scraper_v2.py` | Playwright scraper with cookie injection | `python scraper_v2.py "termo" "cidade" [limite]` |
| `scraper_curl.py` | Curl-based scraper (API approach) | `python scraper_curl.py "termo" "cidade"` |
| `scraper_br.py` | Brazilian directories (Apontador + GuiaFacil) | `python scraper_br.py "termo" "cidade" [limite]` |
| `scraper_apontador.py` | Apontador-only scraper | `python scraper_apontador.py "termo" "cidade" [limite]` |
| `squads/prospect-pro/scripts/google_maps_scraper.py` | Original Playwright scraper (requires PYTHONPATH) | `PYTHONPATH=squads/prospect-pro python scripts/google_maps_scraper.py "termo" "cidade" [limite]` |

## Dependencies (installed in venv)

```
playwright
pyyaml
fastapi
uvicorn
beautifulsoup4
requests
```

## Output
- All scripts save to `/root/prospect/data/`
- Formats: JSON + CSV

## Setup Commands

```bash
cd /root/prospect
source .venv/bin/activate
pip install playwright pyyaml beautifulsoup4 requests
playwright install chromium
```

## IMPORTANT
- Google Maps scraping ONLY works on residential IPs
- This VPS (Hetzner, Germany) is blocked by Google
- For production use, run on local machine or use Google Places API
