import json
from datetime import datetime
from pathlib import Path
from scripts.utils.csv_handler import (
    load_leads_json, save_leads_csv, get_latest_file
)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
REPORTS_DIR = Path(__file__).parent.parent / "data" / "reports"


def generate_report(leads: list[dict], title: str = "Relatório de Prospecção") -> dict:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Classificar leads
    hot = [l for l in leads if l.get("score", {}).get("classification") == "hot"]
    warm = [l for l in leads if l.get("score", {}).get("classification") == "warm"]
    cold = [l for l in leads if l.get("score", {}).get("classification") == "cold"]

    # Ordenar por score (maior primeiro)
    hot.sort(key=lambda x: x.get("score", {}).get("total", 0), reverse=True)
    warm.sort(key=lambda x: x.get("score", {}).get("total", 0), reverse=True)

    # Gerar Markdown
    md = f"# {title}\n\n"
    md += f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    md += f"**Total de leads:** {len(leads)}\n\n"
    md += f"## Resumo\n\n"
    md += f"| Classificação | Quantidade | % |\n"
    md += f"|---------------|-----------|---|\n"
    pct = lambda n: f"{(n/len(leads)*100):.0f}%" if leads else "0%"
    md += f"| [HOT] Hot | {len(hot)} | {pct(len(hot))} |\n"
    md += f"| [WARM] Warm | {len(warm)} | {pct(len(warm))} |\n"
    md += f"| [COLD] Cold | {len(cold)} | {pct(len(cold))} |\n\n"

    # Leads Hot (detalhados)
    if hot:
        md += "## [HOT] Leads Hot — Abordar Imediatamente\n\n"
        for i, lead in enumerate(hot, 1):
            md += format_lead_detail(lead, i)

    # Leads Warm
    if warm:
        md += "## [WARM] Leads Warm — Abordar em 1-3 dias\n\n"
        for i, lead in enumerate(warm, 1):
            md += format_lead_detail(lead, i)

    # Leads Cold (resumo)
    if cold:
        md += "## [COLD] Leads Cold — Monitorar\n\n"
        md += "| # | Nome | Score | Instagram |\n"
        md += "|---|------|-------|----------|\n"
        for i, lead in enumerate(cold, 1):
            g = lead.get("google", {})
            ig = lead.get("instagram", {})
            handle = ig.get("handle", "N/A") if ig else "N/A"
            score = lead.get("score", {}).get("total", 0)
            md += f"| {i} | {g.get('name', 'N/A')} | {score} | @{handle} |\n"
        md += "\n"

    # Salvar relatório
    report_path = REPORTS_DIR / f"{timestamp}_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    # Salvar JSON do relatório
    report_json_path = REPORTS_DIR / f"{timestamp}_report.json"
    report_data = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "summary": {"total": len(leads), "hot": len(hot), "warm": len(warm), "cold": len(cold)},
        "leads": leads,
    }
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

    # Salvar CSV final
    csv_rows = []
    for lead in leads:
        g = lead.get("google", {})
        ig = lead.get("instagram") or {}
        s = lead.get("score", {})
        site = lead.get("website_audit") or {}
        checklist = site.get("checklist") or {}
        cnpj_info = lead.get("cnpj_info") or {}
        owners = cnpj_info.get("owners", [])
        owners_str = ", ".join(f"{o['name']} ({o['role']})" for o in owners) if owners else ""
        csv_rows.append({
            "nome": g.get("name"),
            "categoria": g.get("category"),
            "telefone": g.get("phone"),
            "website": g.get("website"),
            "endereco": g.get("address"),
            "cnpj": cnpj_info.get("cnpj"),
            "razao_social": cnpj_info.get("razao_social"),
            "socios": owners_str,
            "rating_google": g.get("rating"),
            "reviews_google": g.get("reviews_count"),
            "instagram": ig.get("handle"),
            "followers": ig.get("followers"),
            "engagement_rate": ig.get("engagement_rate"),
            "site_status": site.get("status"),
            "site_score": site.get("score"),
            "site_problemas": " | ".join(site.get("problems", [])),
            "site_itens_faltando": " | ".join(checklist.get("missing", [])),
            "score": s.get("total"),
            "classificacao": s.get("classification"),
            "script_abordagem": lead.get("approach_script", "").replace("\n", " | "),
        })

    csv_path = save_leads_csv(csv_rows, "reports")

    print(f"\n[REPORT] Relatorio gerado: {report_path}")
    print(f"[JSON] {report_json_path}")
    print(f"[CSV] {csv_path}")

    return {
        "report_path": str(report_path),
        "json_path": str(report_json_path),
        "csv_path": csv_path,
        "summary": {"total": len(leads), "hot": len(hot), "warm": len(warm), "cold": len(cold)},
        "markdown": md,
    }


def format_lead_detail(lead: dict, index: int) -> str:
    g = lead.get("google", {})
    ig = lead.get("instagram") or {}
    s = lead.get("score", {})
    site = lead.get("website_audit") or {}
    checklist = site.get("checklist") or {}

    md = f"### {index}. {g.get('name', 'N/A')}\n\n"
    md += f"**Score:** {s.get('total', 0)}/20\n\n"

    md += "| Dado | Valor |\n"
    md += "|------|-------|\n"
    md += f"| Categoria | {g.get('category', 'N/A')} |\n"
    md += f"| Telefone | {g.get('phone', 'N/A')} |\n"
    md += f"| Website | {g.get('website', 'Sem website')} |\n"
    md += f"| Endereço | {g.get('address', 'N/A')} |\n"

    cnpj_info = lead.get("cnpj_info")
    if cnpj_info:
        md += f"| CNPJ | {cnpj_info.get('cnpj', 'N/A')} |\n"
        md += f"| Razão Social | {cnpj_info.get('razao_social', 'N/A')} |\n"
        owners = cnpj_info.get("owners", [])
        if owners:
            owners_str = ", ".join(f"{o['name']} ({o['role']})" for o in owners)
            md += f"| Sócios/Donos | {owners_str} |\n"
    md += f"| Rating Google | {g.get('rating', 'N/A')} estrelas ({g.get('reviews_count', 0)} reviews) |\n"

    if ig.get("handle"):
        md += f"| Instagram | @{ig['handle']} |\n"
        md += f"| Followers | {ig.get('followers', 'N/A')} |\n"
        md += f"| Engagement | {ig.get('engagement_rate', 'N/A')}% |\n"
        md += f"| Posts | {ig.get('posts_count', 'N/A')} |\n"
    else:
        md += "| Instagram | Sem Instagram |\n"

    md += "\n"

    if site:
        md += "**Diagnostico do Site:**\n\n"
        md += "| Item | Valor |\n"
        md += "|------|-------|\n"
        md += f"| Status | {site.get('status', 'N/A')} |\n"
        md += f"| Score do site | {site.get('score', 0)}/100 |\n"
        if site.get("final_url"):
            md += f"| URL final | {site.get('final_url')} |\n"
        if site.get("response_time_seconds") is not None:
            md += f"| Tempo de resposta | {site.get('response_time_seconds')}s |\n"
        problems = site.get("problems") or []
        if problems:
            md += f"| Problemas | {', '.join(problems)} |\n"
        missing = checklist.get("missing") or []
        if missing:
            md += f"| Itens faltando | {', '.join(missing)} |\n"
        md += "\n"

    # Analise de Conteudo (se disponivel)
    content_metrics = ig.get("content_metrics")
    if content_metrics:
        md += "**Analise de Conteudo:**\n\n"
        md += "| Metrica | Valor |\n"
        md += "|---------|-------|\n"
        md += f"| Videos/Reels | {content_metrics.get('video_count', 0)} |\n"
        md += f"| Fotos | {content_metrics.get('photo_count', 0)} |\n"
        md += f"| Carrosseis | {content_metrics.get('carousel_count', 0)} |\n"
        md += f"| % Video | {content_metrics.get('video_ratio', 0)}% |\n"
        md += f"| Posts com CTA | {content_metrics.get('posts_with_cta', 0)} ({content_metrics.get('cta_ratio', 0)}%) |\n"
        md += f"| Tamanho medio caption | {content_metrics.get('avg_caption_length', 0)} chars |\n"

        top_hashtags = content_metrics.get("top_hashtags", [])
        if top_hashtags:
            md += f"| Top Hashtags | {', '.join('#' + h for h in top_hashtags[:5])} |\n"
        md += "\n"

    # Posts recentes com detalhes (se disponivel)
    recent_posts = ig.get("recent_posts", [])
    if recent_posts and any(p.get("caption") or p.get("video_url") for p in recent_posts):
        md += "**Posts Recentes:**\n\n"
        md += "| # | Tipo | Curtidas | Coment. | Hashtags | Video |\n"
        md += "|---|------|----------|---------|----------|-------|\n"
        for pi, post in enumerate(recent_posts[:6], 1):
            post_type = post.get("type", "?")
            likes = post.get("likes", 0)
            comments = post.get("comments", 0)
            hashtag_count = len(post.get("hashtags", []))
            has_video = "Sim" if post.get("video_url") else "Nao"
            md += f"| {pi} | {post_type} | {likes} | {comments} | {hashtag_count} | {has_video} |\n"
        md += "\n"

    # Screenshot do grid
    grid_ss = ig.get("grid_screenshot")
    if grid_ss:
        md += f"**Grid Screenshot:** `{grid_ss}`\n\n"

    # Pontos de fraqueza
    weaknesses = []
    if s.get("no_website"): weaknesses.append("Sem website")
    if s.get("bad_website"): weaknesses.append("Site com problemas")
    if s.get("no_instagram"): weaknesses.append("Sem Instagram")
    if s.get("low_engagement"): weaknesses.append("Engagement baixo")
    if s.get("irregular_posting"): weaknesses.append("Posts irregulares")
    if s.get("few_reviews"): weaknesses.append("Poucos reviews")
    if s.get("low_rating"): weaknesses.append("Rating baixo")
    if s.get("no_professional_bio"): weaknesses.append("Bio nao profissional")
    if s.get("no_bio_link"): weaknesses.append("Sem link na bio")

    if weaknesses:
        md += f"**Oportunidades:** {', '.join(weaknesses)}\n\n"

    # Script de abordagem
    script = lead.get("approach_script")
    if script:
        md += f"**Script de Abordagem:**\n\n> {script.replace(chr(10), chr(10) + '> ')}\n\n"

    md += "---\n\n"
    return md


def run_report(filepath: str | None = None, title: str = "Relatório de Prospecção") -> dict:
    if filepath is None:
        filepath = get_latest_file("enriched")
    if filepath is None:
        print("Nenhum arquivo de leads encontrado.")
        return {}

    leads = load_leads_json(filepath)
    print(f"\n[LOAD] Carregados {len(leads)} leads de {filepath}")

    return generate_report(leads, title)


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    title = sys.argv[2] if len(sys.argv) > 2 else "Relatório de Prospecção"
    run_report(filepath, title)
