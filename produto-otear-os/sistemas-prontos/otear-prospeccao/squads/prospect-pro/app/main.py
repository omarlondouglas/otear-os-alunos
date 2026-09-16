import sys
import os
from pathlib import Path

# Forcar UTF-8 no Windows para evitar erros de encoding com caracteres especiais
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Adicionar squad ao path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.routers import scrape, prospects, reports

app = FastAPI(
    title="ProspectPro API",
    description="API de prospeccao ativa para Marketing Digital. "
                "Busca leads no Google Maps, enriquece com Instagram, gera relatorios.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router)
app.include_router(prospects.router)
app.include_router(reports.router)


@app.middleware("http")
async def force_utf8_response(request: Request, call_next):
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


STATIC_DIR = Path(__file__).parent / "static"


@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return {
        "name": "ProspectPro API",
        "version": "1.0.0",
        "description": "Prospeccao ativa para Marketing Digital",
        "docs": "/docs",
    }


@app.get("/api")
async def api_info():
    return {
        "name": "ProspectPro API",
        "version": "1.0.0",
        "endpoints": {
            "scrape": "POST /api/scrape/maps - Buscar leads no Google Maps",
            "leads": "GET /api/leads - Listar leads",
            "enrich": "POST /api/enrich - Enriquecer leads com Instagram",
            "analyze": "POST /api/analyze - Analisar perfis Instagram",
            "reports": "POST /api/reports/generate - Gerar relatorio",
            "list_reports": "GET /api/reports/ - Listar relatorios",
        },
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
