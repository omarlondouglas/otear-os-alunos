import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "scoring_rules.yaml"


def load_scoring_rules() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["scoring"]


def score_lead(lead: dict) -> dict:
    rules = load_scoring_rules()
    criteria = rules["criteria"]
    breakdown = {}

    google = lead.get("google", {})
    insta = lead.get("instagram")

    # Sem website
    has_website = bool(google.get("website"))
    breakdown["no_website"] = criteria["no_website"]["points"] if not has_website else 0
    audit = lead.get("website_audit") or {}
    bad_website_rule = criteria.get("bad_website", {})
    audit_score = audit.get("score", 0) or 0
    breakdown["bad_website"] = (
        bad_website_rule.get("points", 0)
        if has_website
        and audit.get("status") == "bad"
        and audit_score >= bad_website_rule.get("threshold", 30)
        else 0
    )

    # Sem Instagram
    has_instagram = insta and insta.get("handle")
    breakdown["no_instagram"] = criteria["no_instagram"]["points"] if not has_instagram else 0

    if has_instagram and insta:
        # Engagement baixo
        engagement = insta.get("engagement_rate", 0) or 0
        threshold = criteria["low_engagement"]["threshold"]
        breakdown["low_engagement"] = criteria["low_engagement"]["points"] if engagement < threshold else 0

        # Posting irregular
        freq = insta.get("posting_frequency_days", 0) or 0
        max_gap = criteria["irregular_posting"]["maxGapDays"]
        breakdown["irregular_posting"] = criteria["irregular_posting"]["points"] if freq > max_gap else 0

        # Bio não profissional
        bio = insta.get("bio", "") or ""
        breakdown["no_professional_bio"] = criteria["no_professional_bio"]["points"] if len(bio) < 20 else 0

        # Sem link na bio
        has_link = bool(insta.get("bio_link"))
        breakdown["no_bio_link"] = criteria["no_bio_link"]["points"] if not has_link else 0
    else:
        breakdown["low_engagement"] = 0
        breakdown["irregular_posting"] = 0
        breakdown["no_professional_bio"] = 0
        breakdown["no_bio_link"] = 0

    # Poucos reviews
    reviews = google.get("reviews_count", 0) or 0
    threshold = criteria["few_reviews"]["threshold"]
    breakdown["few_reviews"] = criteria["few_reviews"]["points"] if reviews < threshold else 0

    # Rating baixo
    rating = google.get("rating", 0) or 0
    threshold = criteria["low_rating"]["threshold"]
    breakdown["low_rating"] = criteria["low_rating"]["points"] if 0 < rating < threshold else 0

    total = sum(breakdown.values())
    breakdown["total"] = total

    classification_rules = rules["classification"]
    if total >= classification_rules["hot"]["minScore"]:
        breakdown["classification"] = "hot"
    elif total >= classification_rules["warm"]["minScore"]:
        breakdown["classification"] = "warm"
    else:
        breakdown["classification"] = "cold"

    return breakdown


def generate_approach_script(lead: dict, score: dict) -> str:
    google = lead.get("google", {})
    name = google.get("name", "sua empresa")
    category = google.get("category", "seu negócio")
    weaknesses = []

    if score.get("no_website"):
        weaknesses.append("não tem um site profissional")
    if score.get("bad_website"):
        audit = lead.get("website_audit") or {}
        problems = audit.get("problems") or []
        if problems:
            weaknesses.append(f"tem um site com problema de {problems[0]}")
        else:
            weaknesses.append("tem um site que pode estar perdendo conversões")
    if score.get("no_instagram"):
        weaknesses.append("não está presente no Instagram")
    if score.get("low_engagement"):
        weaknesses.append("o engajamento nas redes está abaixo do ideal")
    if score.get("irregular_posting"):
        weaknesses.append("a frequência de posts está irregular")
    if score.get("no_bio_link"):
        weaknesses.append("o perfil do Instagram não tem link para conversão")

    if not weaknesses:
        insight = f"vi que o {name} tem potencial para crescer muito nas redes sociais"
    elif len(weaknesses) == 1:
        insight = f"notei que o {name} {weaknesses[0]}"
    else:
        insight = f"notei que o {name} {weaknesses[0]} e {weaknesses[1]}"

    classification = score.get("classification", "cold")

    if classification == "hot":
        urgency = "Tenho algumas ideias rápidas que podem trazer resultados já no primeiro mês."
    elif classification == "warm":
        urgency = "Tenho um diagnóstico gratuito que pode ajudar a identificar oportunidades."
    else:
        urgency = "Se tiver interesse, posso compartilhar algumas dicas sem compromisso."

    # Tentar obter o nome do primeiro sócio/dono
    owner_name = None
    cnpj_info = lead.get("cnpj_info")
    if cnpj_info and cnpj_info.get("owners"):
        first_owner = cnpj_info["owners"][0].get("name", "")
        if first_owner:
            parts = first_owner.split()
            if parts:
                first_name = parts[0].strip().title()
                if len(first_name) >= 3 and first_name.isalpha():
                    owner_name = first_name

    greeting = f"Ola, {owner_name}! Tudo bem?" if owner_name else "Ola! Tudo bem?"

    script = (
        f"{greeting}\n\n"
        f"Sou especialista em marketing digital para {category} e "
        f"{insight}.\n\n"
        f"{urgency}\n\n"
        f"Posso te enviar mais detalhes?"
    )

    return script
