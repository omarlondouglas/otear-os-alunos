"""
ProspectPro Pipeline Completo
Roda todo o fluxo: Scrape -> Enrich -> Analyze -> Report
Com um unico comando.
"""
import asyncio
import sys
import os
from pathlib import Path

# Forcar UTF-8 no Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Garantir que o squad esta no path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.google_maps_scraper import run_scraper
from scripts.lead_enricher import run_enricher
from scripts.instagram_scraper import run_analyzer
from scripts.report_generator import run_report


async def run_pipeline(query: str, location: str, limit: int = 20) -> dict:
    """
    Executa o pipeline completo de prospeccao.

    Args:
        query: Nicho/categoria (ex: "restaurantes", "barbearias")
        location: Local (ex: "Sao Paulo", "Curitiba centro")
        limit: Numero maximo de leads

    Returns:
        Dict com summary, report_path, markdown do relatorio
    """
    print(f"\n{'='*60}")
    print(f"  PROSPECTPRO - Pipeline Completo")
    print(f"  Nicho: {query}")
    print(f"  Local: {location}")
    print(f"  Limite: {limit} leads")
    print(f"{'='*60}\n")

    # --- FASE 1: Scraping Google Maps ---
    print("[1/4] SCOUT - Buscando leads no Google Maps...")
    print("-" * 40)
    scrape_result = await run_scraper(query, location, limit)
    leads_count = len(scrape_result.get("leads", []))
    print(f"[OK] {leads_count} leads encontrados")
    print(f"     Arquivo: {scrape_result.get('json_path')}\n")

    if leads_count == 0:
        print("[FIM] Nenhum lead encontrado. Pipeline encerrado.")
        return {
            "success": False,
            "message": "Nenhum lead encontrado no Google Maps",
            "summary": {"total": 0, "hot": 0, "warm": 0, "cold": 0},
        }

    # --- FASE 2: Enriquecimento (busca Instagram) ---
    print("[2/4] ENRICHER - Buscando Instagram dos leads...")
    print("-" * 40)
    enrich_result = await run_enricher(scrape_result["json_path"])
    enriched = enrich_result.get("leads", [])
    with_insta = sum(1 for l in enriched if l.get("instagram") and l["instagram"].get("handle"))
    print(f"[OK] {with_insta}/{leads_count} leads com Instagram encontrado")
    print(f"     Arquivo: {enrich_result.get('json_path')}\n")

    # --- FASE 3: Analise Instagram ---
    print("[3/4] STALKER - Analisando perfis Instagram...")
    print("-" * 40)
    analyze_result = await run_analyzer(enrich_result["json_path"])
    hot = analyze_result.get("hot", 0)
    warm = analyze_result.get("warm", 0)
    cold = analyze_result.get("cold", 0)
    print(f"[OK] Analise completa: {hot} HOT | {warm} WARM | {cold} COLD")
    print(f"     Arquivo: {analyze_result.get('json_path')}\n")

    # --- FASE 4: Geracao de Relatorio ---
    print("[4/4] REPORTER - Gerando relatorio final...")
    print("-" * 40)
    title = f"Prospeccao: {query} em {location}"
    report_result = run_report(analyze_result["json_path"], title)
    print(f"[OK] Relatorio gerado!")
    print(f"     MD:   {report_result.get('report_path')}")
    print(f"     JSON: {report_result.get('json_path')}")
    print(f"     CSV:  {report_result.get('csv_path')}\n")

    # --- RESUMO FINAL ---
    summary = report_result.get("summary", {})
    print(f"{'='*60}")
    print(f"  PIPELINE COMPLETO!")
    print(f"  Total: {summary.get('total', 0)} leads")
    print(f"  HOT:  {summary.get('hot', 0)}")
    print(f"  WARM: {summary.get('warm', 0)}")
    print(f"  COLD: {summary.get('cold', 0)}")
    print(f"{'='*60}\n")

    # Imprime o relatorio no terminal
    print("\n" + report_result.get("markdown", ""))

    return {
        "success": True,
        "summary": summary,
        "report_path": report_result.get("report_path"),
        "json_path": report_result.get("json_path"),
        "csv_path": report_result.get("csv_path"),
        "markdown": report_result.get("markdown"),
    }


def main():
    """Entry point CLI."""
    if len(sys.argv) < 3:
        print("Uso: python prospect_pipeline.py <nicho> <local> [limite]")
        print("Exemplo: python prospect_pipeline.py restaurantes \"Sao Paulo\" 10")
        sys.exit(1)

    query = sys.argv[1]
    location = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    result = asyncio.run(run_pipeline(query, location, limit))

    if result["success"]:
        print(f"\nRelatorio salvo em: {result['report_path']}")
    else:
        print(f"\n{result['message']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
