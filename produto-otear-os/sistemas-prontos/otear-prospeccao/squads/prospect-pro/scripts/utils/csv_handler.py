import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Any


DATA_DIR = Path(__file__).parent.parent.parent / "data"


def ensure_dirs():
    for subdir in ["leads", "enriched", "reports"]:
        (DATA_DIR / subdir).mkdir(parents=True, exist_ok=True)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_leads_json(leads: list[dict], stage: str = "leads") -> str:
    ensure_dirs()
    filename = f"{timestamp()}_{stage}.json"
    filepath = DATA_DIR / stage / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2, default=str)
    return str(filepath)


def save_leads_csv(leads: list[dict], stage: str = "leads") -> str:
    ensure_dirs()
    filename = f"{timestamp()}_{stage}.csv"
    filepath = DATA_DIR / stage / filename
    if not leads:
        return str(filepath)

    flat = [flatten_dict(lead) for lead in leads]
    fieldnames: list[str] = []
    seen_fields: set[str] = set()
    for row in flat:
        for key in row.keys():
            if key not in seen_fields:
                seen_fields.add(key)
                fieldnames.append(key)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    return str(filepath)


def load_leads_json(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        leads = data.get("leads")
        if isinstance(leads, list):
            return leads
        return [data]
    return []


def get_latest_file(stage: str, extension: str = ".json") -> str | None:
    dir_path = DATA_DIR / stage
    if not dir_path.exists():
        return None
    files = sorted(dir_path.glob(f"*{extension}"), reverse=True)
    return str(files[0]) if files else None


def flatten_dict(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v, ensure_ascii=False, default=str)))
        else:
            items.append((new_key, v))
    return dict(items)
