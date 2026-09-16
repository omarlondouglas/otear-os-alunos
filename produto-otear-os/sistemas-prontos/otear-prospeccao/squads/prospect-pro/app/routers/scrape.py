from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.lead import ScrapeRequest
from app.services.maps_service import scrape_maps

router = APIRouter(prefix="/api/scrape", tags=["scrape"])

# Armazena status dos jobs em memória
_jobs: dict[str, dict] = {}
_job_counter = 0


@router.post("/maps")
async def start_maps_scraping(request: ScrapeRequest, background_tasks: BackgroundTasks):
    global _job_counter
    _job_counter += 1
    job_id = f"job_{_job_counter}"

    _jobs[job_id] = {"status": "running", "result": None}

    async def run_job():
        try:
            result = await scrape_maps(request.query, request.location, request.limit)
            _jobs[job_id] = {"status": "completed", "result": result}
        except Exception as e:
            _jobs[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(run_job)

    return {"job_id": job_id, "status": "started", "query": request.query, "location": request.location}


@router.post("/maps/sync")
async def scrape_maps_sync(request: ScrapeRequest):
    try:
        result = await scrape_maps(request.query, request.location, request.limit)
        return {
            "status": "completed",
            "total": result["total"],
            "json_path": result["json_path"],
            "csv_path": result["csv_path"],
            "leads": result["leads"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) or repr(e))


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return _jobs[job_id]
