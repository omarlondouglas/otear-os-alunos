from fastapi import APIRouter, UploadFile, File, Query, Depends, HTTPException
from hashlib import sha1
from pathlib import Path
from typing import Optional
from app.core.database import get_supabase
from app.core.auth import verify_api_key
from app.schemas.lead import LeadResponse, LeadListResponse, BulkActionRequest, ImportResponse
from app.services.lead_import import import_leads, parse_prospect_pro_json

router = APIRouter(prefix="/api/leads", tags=["leads"])


def prospect_data_dir(stage: str) -> Path:
    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "agents" / "prospect-pro" / "data" / stage


def latest_prospect_file() -> Path | None:
    candidates = []
    for stage in ("enriched", "leads"):
        data_dir = prospect_data_dir(stage)
        candidates.extend(data_dir.glob("*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def stable_local_lead_id(lead: dict) -> str:
    source = "|".join(
        str(lead.get(key) or "")
        for key in ("prospect_pro_id", "name", "address", "whatsapp_number", "website")
    )
    return "local-" + sha1(source.encode("utf-8")).hexdigest()[:16]


def list_local_prospect_leads(
    classification: Optional[str],
    outreach_status: Optional[str],
    min_score: Optional[int],
    search: Optional[str],
    page: int,
    per_page: int,
) -> dict:
    latest_file = latest_prospect_file()
    if not latest_file:
        return {"total": 0, "hot": 0, "warm": 0, "cold": 0, "leads": []}

    leads = parse_prospect_pro_json(latest_file.read_text(encoding="utf-8-sig"))
    for lead in leads:
        lead.setdefault("id", stable_local_lead_id(lead))
        lead.setdefault("outreach_status", "imported")

    if classification:
        leads = [lead for lead in leads if lead.get("score_classification") == classification]
    if outreach_status:
        leads = [lead for lead in leads if lead.get("outreach_status") == outreach_status]
    if min_score is not None:
        leads = [lead for lead in leads if (lead.get("score_total") or 0) >= min_score]
    if search:
        needle = search.lower()
        leads = [
            lead for lead in leads
            if needle in (lead.get("name") or "").lower()
            or needle in (lead.get("category") or "").lower()
            or needle in (lead.get("address") or "").lower()
        ]

    leads.sort(key=lambda lead: lead.get("score_total") or 0, reverse=True)
    total = len(leads)
    hot = sum(1 for lead in leads if lead.get("score_classification") == "hot")
    warm = sum(1 for lead in leads if lead.get("score_classification") == "warm")
    cold = sum(1 for lead in leads if lead.get("score_classification") == "cold")

    offset = (page - 1) * per_page
    return {
        "total": total,
        "hot": hot,
        "warm": warm,
        "cold": cold,
        "leads": leads[offset:offset + per_page],
    }


@router.post("/import", response_model=ImportResponse)
async def import_leads_endpoint(file: UploadFile = File(...), _=Depends(verify_api_key)):
    content = (await file.read()).decode("utf-8")
    file_type = "csv" if file.filename and file.filename.endswith(".csv") else "json"
    result = await import_leads(content, file_type)
    return result


@router.post("/import-latest-prospect", response_model=ImportResponse)
async def import_latest_prospect_endpoint(
    stage: str = Query("leads", pattern="^(leads|enriched)$"),
    _=Depends(verify_api_key),
):
    data_dir = prospect_data_dir(stage)
    files = sorted(data_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail=f"Nenhum arquivo encontrado em {data_dir}")

    content = files[0].read_text(encoding="utf-8-sig")
    return await import_leads(content, "json")


@router.get("", response_model=LeadListResponse)
async def list_leads(
    classification: Optional[str] = None,
    outreach_status: Optional[str] = None,
    min_score: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    _=Depends(verify_api_key),
):
    try:
        db = get_supabase()
        query = db.table("leads").select("*", count="exact")

        if classification:
            query = query.eq("score_classification", classification)
        if outreach_status:
            query = query.eq("outreach_status", outreach_status)
        if min_score is not None:
            query = query.gte("score_total", min_score)
        if search:
            query = query.ilike("name", f"%{search}%")

        offset = (page - 1) * per_page
        query = query.order("score_total", desc=True).range(offset, offset + per_page - 1)
        result = query.execute()
    except Exception:
        return list_local_prospect_leads(
            classification=classification,
            outreach_status=outreach_status,
            min_score=min_score,
            search=search,
            page=page,
            per_page=per_page,
        )

    leads = result.data or []
    total = result.count or 0

    hot = sum(1 for l in leads if l.get("score_classification") == "hot")
    warm = sum(1 for l in leads if l.get("score_classification") == "warm")
    cold = sum(1 for l in leads if l.get("score_classification") == "cold")

    return {
        "total": total,
        "hot": hot,
        "warm": warm,
        "cold": cold,
        "leads": leads,
    }


@router.get("/{lead_id}")
async def get_lead(lead_id: str, _=Depends(verify_api_key)):
    db = get_supabase()
    result = db.table("leads").select("*").eq("id", lead_id).single().execute()
    return result.data


@router.patch("/{lead_id}")
async def update_lead(lead_id: str, updates: dict, _=Depends(verify_api_key)):
    db = get_supabase()
    allowed = {"notes", "tags", "outreach_status", "whatsapp_number"}
    clean = {k: v for k, v in updates.items() if k in allowed}
    result = db.table("leads").update(clean).eq("id", lead_id).execute()
    return result.data[0] if result.data else {"error": "Lead não encontrado"}


@router.post("/bulk")
async def bulk_action(request: BulkActionRequest, _=Depends(verify_api_key)):
    db = get_supabase()
    updated = 0

    for lead_id in request.lead_ids:
        if request.action == "tag" and request.value:
            lead = db.table("leads").select("tags").eq("id", lead_id).single().execute()
            if lead.data:
                tags = lead.data.get("tags", [])
                if request.value not in tags:
                    tags.append(request.value)
                    db.table("leads").update({"tags": tags}).eq("id", lead_id).execute()
                    updated += 1
        elif request.action == "archive":
            db.table("leads").update({"outreach_status": "archived"}).eq("id", lead_id).execute()
            updated += 1
        elif request.action == "assign_campaign":
            db.table("leads").update({"outreach_status": "queued"}).eq("id", lead_id).execute()
            updated += 1

    return {"updated": updated, "total": len(request.lead_ids)}
