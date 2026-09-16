import re
import random


GREETING_VARIATIONS = [
    "Olá", "Oi", "E aí", "Bom dia", "Boa tarde",
    "Olá!", "Oi!", "Hey", "Fala",
]

INTRO_VARIATIONS = [
    "Tudo bem?", "Tudo certo?", "Como vai?",
    "Tudo joia?", "Como está?",
]


def resolve_template(template: str, lead: dict) -> str:
    """Substitui variáveis no template com dados do lead."""
    name = lead.get("name", "")
    first_name = name.split()[0] if name else ""

    # Detect main problem from score breakdown
    problems = []
    if lead.get("score_no_website", 0) > 0:
        problems.append("não tem um site profissional")
    if lead.get("score_no_instagram", 0) > 0:
        problems.append("não está presente no Instagram")
    if lead.get("score_low_engagement", 0) > 0:
        problems.append("o engajamento nas redes está abaixo do ideal")
    if lead.get("score_irregular_posting", 0) > 0:
        problems.append("não tem uma estratégia de conteúdo regular")
    if lead.get("score_no_bio_link", 0) > 0:
        problems.append("o perfil do Instagram não tem link para conversão")

    main_problem = problems[0] if problems else "pode melhorar sua presença digital"

    # Extract city from address
    address = lead.get("address", "") or ""
    city_parts = address.split(",")
    city = city_parts[-2].strip() if len(city_parts) >= 2 else "sua região"

    variables = {
        "{{nome}}": name,
        "{{primeiro_nome}}": first_name,
        "{{categoria}}": lead.get("category", "seu segmento") or "seu segmento",
        "{{cidade}}": city,
        "{{instagram}}": lead.get("instagram_handle", "") or "",
        "{{problema}}": main_problem,
        "{{website}}": lead.get("website", "sem website") or "sem website",
        "{{saudacao}}": random.choice(GREETING_VARIATIONS),
        "{{intro}}": random.choice(INTRO_VARIATIONS),
    }

    result = template
    for var, value in variables.items():
        result = result.replace(var, str(value))

    return result


def apply_micro_variations(text: str) -> str:
    """Aplica micro-variações para evitar fingerprint de mensagem idêntica."""
    # Randomly add/remove emoji variations
    emoji_pairs = [
        ("👋", "✋"),
        ("📊", "📈"),
        ("✅", "☑️"),
        ("🔥", "⚡"),
    ]
    for a, b in emoji_pairs:
        if a in text and random.random() > 0.5:
            text = text.replace(a, b)

    # Random punctuation variation
    if random.random() > 0.7:
        text = text.replace("!", ".")
    if random.random() > 0.8:
        text = text.replace("?", "? 🤔")

    return text
