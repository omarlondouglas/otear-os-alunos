from fastapi import APIRouter, HTTPException, Query
from app.models.lead import EnrichRequest, AnalyzeRequest, LeadListResponse
from app.services.maps_service import get_raw_leads
from app.services.instagram_service import enrich_leads, analyze_instagram, get_enriched_leads

router = APIRouter(prefix="/api", tags=["prospects"])


@router.get("/leads")
async def list_leads(
    status: str | None = Query(None, description="Filtrar por status: raw, enriched, analyzed"),
    classification: str | None = Query(None, description="Filtrar: hot, warm, cold"),
    min_score: int | None = Query(None, ge=0, le=20),
    file: str | None = Query(None, description="Caminho do arquivo de leads"),
):
    if status == "raw" or (not status and not file):
        leads = get_raw_leads(file)
    else:
        leads = get_enriched_leads(file)

    # Filtrar por classificação
    if classification:
        leads = [l for l in leads if l.get("score", {}).get("classification") == classification]

    # Filtrar por score mínimo
    if min_score is not None:
        leads = [l for l in leads if l.get("score", {}).get("total", 0) >= min_score]

    hot = sum(1 for l in leads if l.get("score", {}).get("classification") == "hot")
    warm = sum(1 for l in leads if l.get("score", {}).get("classification") == "warm")
    cold = sum(1 for l in leads if l.get("score", {}).get("classification") == "cold")

    return {"total": len(leads), "hot": hot, "warm": warm, "cold": cold, "leads": leads}


@router.post("/enrich")
async def enrich_leads_endpoint(request: EnrichRequest):
    try:
        result = await enrich_leads(request.leads_file)
        return {
            "status": "completed",
            "total": len(result["leads"]),
            "json_path": result["json_path"],
            "leads": result["leads"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) or repr(e))


@router.post("/analyze")
async def analyze_instagram_endpoint(request: AnalyzeRequest):
    try:
        result = await analyze_instagram(request.leads_file, request.posts_to_analyze)
        return {
            "status": "completed",
            "total": len(result["leads"]),
            "hot": result.get("hot", 0),
            "warm": result.get("warm", 0),
            "cold": result.get("cold", 0),
            "json_path": result["json_path"],
            "leads": result["leads"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) or repr(e))
