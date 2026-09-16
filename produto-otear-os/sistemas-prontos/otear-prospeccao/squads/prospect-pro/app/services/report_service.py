import sys
from pathlib import Path

SQUAD_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.report_generator import generate_report, run_report
from scripts.utils.csv_handler import get_latest_file, load_leads_json

REPORTS_DIR = SQUAD_DIR / "data" / "reports"


async def create_report(filepath: str | None = None, title: str = "Relatório de Prospecção") -> dict:
    return run_report(filepath, title)


def list_reports() -> list[dict]:
    if not REPORTS_DIR.exists():
        return []
    reports = []
    for f in sorted(REPORTS_DIR.glob("*_report.json"), reverse=True):
        data = load_leads_json(str(f))
        reports.append({
            "id": f.stem,
            "title": data.get("title"),
            "generated_at": data.get("generated_at"),
            "summary": data.get("summary"),
            "path": str(f),
        })
    return reports


def get_report(report_id: str) -> dict | None:
    json_path = REPORTS_DIR / f"{report_id}.json"
    md_path = REPORTS_DIR / f"{report_id.replace('_report', '_report')}.md"

    if not json_path.exists():
        # Tentar buscar pelo ID parcial
        matches = list(REPORTS_DIR.glob(f"*{report_id}*.json"))
        if matches:
            json_path = matches[0]
            md_path = json_path.with_suffix(".md")
        else:
            return None

    data = load_leads_json(str(json_path))
    markdown = ""
    if md_path.exists():
        with open(md_path, "r", encoding="utf-8") as f:
            markdown = f.read()

    return {**data, "markdown": markdown}
