"""
ProspectPro - Processar Leads Existentes
Roda as fases de enriquecimento (Instagram, CNPJ, Sócios), análise profunda (stalker)
e geração de relatórios a partir de um arquivo de leads já existente.

Uso: python scripts/enrich_existing.py [caminho_do_arquivo_leads.json]
Se nenhum arquivo for passado, usará o mais recente da pasta data/leads/.
"""
import asyncio
import sys
import os
from pathlib import Path

# Forçar UTF-8 no Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Garantir que o squad está no path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.lead_enricher import run_enricher
from scripts.instagram_scraper import run_analyzer
from scripts.report_generator import run_report
from scripts.utils.csv_handler import get_latest_file


async def run_existing_pipeline(filepath: str | None = None) -> None:
    if filepath is None:
        filepath = get_latest_file("leads")
    
    if filepath is None or not Path(filepath).exists():
        print(f"[ERRO] Arquivo de leads não encontrado: {filepath}")
        return

    print(f"\n{'='*60}")
    print(f"  PROSPECTPRO - Processando Leads Existentes")
    print(f"  Arquivo original: {filepath}")
    print(f"{'='*60}\n")

    # --- FASE 1: Enriquecimento (Instagram + CNPJ + Sócios) ---
    print("[1/3] ENRICHER - Buscando Instagram, CNPJ e Sócios...")
    print("-" * 40)
    enrich_result = await run_enricher(filepath)
    enriched_path = enrich_result.get("json_path")
    if not enriched_path:
        print("[ERRO] Falha ao enriquecer os leads.")
        return

    # --- FASE 2: Análise Instagram ---
    print("\n[2/3] STALKER - Analisando perfis Instagram...")
    print("-" * 40)
    analyze_result = await run_analyzer(enriched_path)
    analyzed_path = analyze_result.get("json_path")
    if not analyzed_path:
        print("[ERRO] Falha ao analisar os leads.")
        return

    # --- FASE 3: Geração de Relatório ---
    print("\n[3/3] REPORTER - Gerando relatório final...")
    print("-" * 40)
    filename = Path(filepath).stem
    title = f"Relatório de Prospecção - {filename}"
    report_result = run_report(analyzed_path, title)
    
    print(f"\n{'='*60}")
    print(f"  CONCLUÍDO COM SUCESSO!")
    print(f"  MD:   {report_result.get('report_path')}")
    print(f"  JSON: {report_result.get('json_path')}")
    print(f"  CSV:  {report_result.get('csv_path')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_existing_pipeline(filepath))
