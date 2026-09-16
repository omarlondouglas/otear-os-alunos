from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.lead import ReportRequest
from app.services.report_service import create_report, list_reports, get_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("/generate")
async def generate_report_endpoint(request: ReportRequest):
    try:
        result = await create_report(request.leads_file, request.title)
        if not result:
            raise HTTPException(status_code=404, detail="Nenhum lead encontrado para gerar relatório")
        return {
            "status": "completed",
            "report_path": result.get("report_path"),
            "csv_path": result.get("csv_path"),
            "summary": result.get("summary"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_reports_endpoint():
    reports = list_reports()
    return {"total": len(reports), "reports": reports}


@router.get("/{report_id}")
async def get_report_endpoint(report_id: str):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return report


@router.get("/{report_id}/download")
async def download_report(report_id: str, format: str = "md"):
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")

    if format == "md":
        path = report.get("report_path") or report.get("path", "").replace(".json", ".md")
    elif format == "json":
        path = report.get("path")
    else:
        raise HTTPException(status_code=400, detail="Formato inválido. Use: md, json")

    if not path:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(path, filename=f"report_{report_id}.{format}")
