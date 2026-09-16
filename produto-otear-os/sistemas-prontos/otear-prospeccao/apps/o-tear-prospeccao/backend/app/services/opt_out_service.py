from app.core.database import get_supabase


DEFAULT_KEYWORDS = ["parar", "sair", "cancelar", "stop", "remover", "nao quero", "nao desejo"]


async def get_opt_out_keywords() -> list[str]:
    db = get_supabase()
    result = db.table("app_settings").select("value").eq("key", "opt_out_keywords").single().execute()
    if result.data:
        return result.data["value"]
    return DEFAULT_KEYWORDS


async def check_opt_out(message: str) -> bool:
    """Verifica se a mensagem contém keywords de opt-out."""
    keywords = await get_opt_out_keywords()
    message_lower = message.lower().strip()
    return any(kw in message_lower for kw in keywords)


async def register_opt_out(phone_number: str, lead_id: str | None = None, reason: str | None = None):
    """Registra opt-out e atualiza status do lead."""
    db = get_supabase()

    # Inserir opt-out (ignora se já existe)
    try:
        db.table("opt_outs").insert({
            "phone_number": phone_number,
            "lead_id": lead_id,
            "reason": reason or "Solicitou parada via mensagem",
        }).execute()
    except Exception:
        pass  # already exists

    # Atualizar lead
    if lead_id:
        db.table("leads").update({"outreach_status": "opted_out"}).eq("id", lead_id).execute()

    # Cancelar mensagens pendentes
    db.table("message_queue").update({
        "status": "cancelled",
    }).eq("whatsapp_to", phone_number).eq("status", "pending").execute()
