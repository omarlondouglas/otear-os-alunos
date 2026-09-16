import json
import csv
import io
import re
import uuid
from datetime import datetime
from app.core.database import get_supabase


def normalize_phone_br(raw: str | None) -> str | None:
    """Normaliza telefone brasileiro para formato 55XXXXXXXXXXX."""
    if not raw:
        return None
    cleaned = re.sub(r"[^\d]", "", raw.strip())
    if not cleaned:
        return None
    if len(cleaned) == 11:
        cleaned = "55" + cleaned
    elif len(cleaned) == 10:
        cleaned = "55" + cleaned
    elif len(cleaned) == 13 and cleaned.startswith("55"):
        pass
    elif len(cleaned) == 12 and cleaned.startswith("55"):
        pass
    else:
        cleaned = "55" + cleaned
    return cleaned


def parse_prospect_pro_json(content: str) -> list[dict]:
    """Parse JSON exportado pelo ProspectPro."""
    data = json.loads(content)
    if isinstance(data, dict) and "leads" in data:
        leads_raw = data["leads"]
    elif isinstance(data, list):
        leads_raw = data
    else:
        leads_raw = [data]

    results = []
    for lead in leads_raw:
        google = lead.get("google", {})
        instagram = lead.get("instagram") or {}
        score = lead.get("score") or {}
        cnpj_info = lead.get("cnpj_info") or {}
        site_audit = lead.get("website_audit") or {}
        site_checklist = site_audit.get("checklist") or {}
        owners = cnpj_info.get("owners") or []
        decision_maker = next(
            (
                owner for owner in owners
                if re.search(r"administrador|titular|diretor|presidente|empres", owner.get("role") or "", re.I)
            ),
            owners[0] if owners else {},
        )

        row = {
            "prospect_pro_id": lead.get("id"),
            "name": google.get("name", ""),
            "category": google.get("category"),
            "phone": google.get("phone"),
            "website": google.get("website"),
            "address": google.get("address"),
            "rating": google.get("rating"),
            "reviews_count": google.get("reviews_count"),
            "maps_url": google.get("maps_url"),
            "latitude": google.get("latitude"),
            "longitude": google.get("longitude"),
            "instagram_handle": instagram.get("handle"),
            "instagram_url": instagram.get("profile_url"),
            "instagram_bio": instagram.get("bio"),
            "instagram_bio_link": instagram.get("bio_link"),
            "instagram_followers": instagram.get("followers"),
            "instagram_following": instagram.get("following"),
            "instagram_posts": instagram.get("posts_count"),
            "instagram_is_business": instagram.get("is_business", False),
            "instagram_is_verified": instagram.get("is_verified", False),
            "engagement_rate": instagram.get("engagement_rate"),
            "avg_likes": instagram.get("avg_likes"),
            "avg_comments": instagram.get("avg_comments"),
            "posting_frequency_days": instagram.get("posting_frequency_days"),
            "last_post_date": instagram.get("last_post_date"),
            "cnpj": cnpj_info.get("cnpj"),
            "razao_social": cnpj_info.get("razao_social"),
            "nome_fantasia": cnpj_info.get("nome_fantasia"),
            "decision_maker_name": decision_maker.get("name"),
            "decision_maker_role": decision_maker.get("role"),
            "cnpj_owners": owners,
            "score_total": score.get("total", 0),
            "score_classification": score.get("classification", "cold"),
            "score_no_website": score.get("no_website", 0),
            "score_bad_website": score.get("bad_website", 0),
            "score_no_instagram": score.get("no_instagram", 0),
            "score_low_engagement": score.get("low_engagement", 0),
            "score_irregular_posting": score.get("irregular_posting", 0),
            "score_few_reviews": score.get("few_reviews", 0),
            "score_low_rating": score.get("low_rating", 0),
            "score_no_professional_bio": score.get("no_professional_bio", 0),
            "score_no_bio_link": score.get("no_bio_link", 0),
            "approach_script": lead.get("approach_script"),
            "site_status": site_audit.get("status"),
            "site_score": site_audit.get("score"),
            "site_final_url": site_audit.get("final_url"),
            "site_problems": site_audit.get("problems", []),
            "site_missing_items": site_checklist.get("missing", []),
            "site_present_items": site_checklist.get("present", []),
            "site_response_time_seconds": site_audit.get("response_time_seconds"),
            "site_http_status": site_audit.get("http_status"),
            "site_audit": site_audit,
            "tags": lead.get("tags", []),
            "notes": lead.get("notes"),
        }
        row["whatsapp_number"] = normalize_phone_br(row["phone"])
        results.append(row)
    return results


def parse_csv_import(content: str) -> list[dict]:
    """Parse CSV exportado pelo ProspectPro."""
    reader = csv.DictReader(io.StringIO(content))
    results = []
    for row in reader:
        mapped = {
            "name": row.get("name", row.get("nome", "")),
            "category": row.get("category", row.get("categoria")),
            "phone": row.get("phone", row.get("telefone")),
            "website": row.get("website"),
            "address": row.get("address", row.get("endereco")),
            "rating": float(row["rating"]) if row.get("rating") else None,
            "reviews_count": int(row["reviews_count"]) if row.get("reviews_count") else None,
            "instagram_handle": row.get("instagram_handle", row.get("instagram")),
            "instagram_followers": int(row["instagram_followers"]) if row.get("instagram_followers") else None,
            "engagement_rate": float(row["engagement_rate"]) if row.get("engagement_rate") else None,
            "score_total": int(row.get("score_total", row.get("score", 0)) or 0),
            "score_classification": row.get("score_classification", row.get("classification", "cold")),
            "site_status": row.get("site_status"),
            "site_score": int(row["site_score"]) if row.get("site_score") else None,
            "approach_script": row.get("approach_script"),
            "tags": [],
        }
        mapped["whatsapp_number"] = normalize_phone_br(mapped["phone"])
        results.append(mapped)
    return results


async def import_leads(content: str, file_type: str = "json") -> dict:
    """Importa leads para o Supabase. Retorna resumo da importação."""
    db = get_supabase()
    batch_id = str(uuid.uuid4())

    if file_type == "json":
        leads = parse_prospect_pro_json(content)
    else:
        leads = parse_csv_import(content)

    imported = 0
    duplicates = 0
    updated_existing = 0
    errors = 0
    error_details = []

    for lead in leads:
        if not lead.get("name"):
            errors += 1
            error_details.append("Lead sem nome encontrado, pulando")
            continue

        # Check duplicate by phone or name+address
        existing = None
        if lead.get("whatsapp_number"):
            result = db.table("leads").select("id").eq(
                "whatsapp_number", lead["whatsapp_number"]
            ).execute()
            if result.data:
                existing = result.data[0]

        if not existing and lead.get("name") and lead.get("address"):
            result = db.table("leads").select("id").eq(
                "name", lead["name"]
            ).eq("address", lead["address"]).execute()
            if result.data:
                existing = result.data[0]

        if existing:
            update_data = {
                k: v for k, v in lead.items()
                if v is not None and k not in {"outreach_status", "import_batch_id", "imported_at", "created_at"}
            }
            update_data["updated_at"] = datetime.utcnow().isoformat()

            try:
                db.table("leads").update(update_data).eq("id", existing["id"]).execute()
                updated_existing += 1
            except Exception as e:
                errors += 1
                error_details.append(f"Erro ao atualizar {lead.get('name', '?')}: {str(e)[:100]}")
            continue

        lead["import_batch_id"] = batch_id
        lead["outreach_status"] = "imported"

        # Remove None values to let DB defaults work
        clean = {k: v for k, v in lead.items() if v is not None}

        try:
            db.table("leads").insert(clean).execute()
            imported += 1
        except Exception as e:
            errors += 1
            error_details.append(f"Erro ao inserir {lead.get('name', '?')}: {str(e)[:100]}")

    return {
        "batch_id": batch_id,
        "total_imported": imported,
        "duplicates_skipped": duplicates,
        "updated_existing": updated_existing,
        "errors": errors,
        "error_details": error_details[:20],
    }
