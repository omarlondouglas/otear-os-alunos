import asyncio
import os
import sys
import re
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure squad is in path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.google_maps_scraper import scrape_google_maps
from scripts.lead_enricher import enrich_leads
from scripts.instagram_scraper import analyze_leads
from scripts.report_generator import generate_report
from scripts.utils.csv_handler import save_leads_json, save_leads_csv


def normalize(s: str) -> str:
    if not s:
        return ""
    # Remove emojis, special chars, and whitespace
    return re.sub(r'[^a-z0-9]', '', s.lower())


async def main():
    print("=" * 60)
    print("PROSPECTPRO - RIO DE JANEIRO & REGION SOLAR ENERGY SCRAPER")
    print("Alvo: 100 empresas únicas de energia solar")
    print("=" * 60)

    unique_leads = []
    seen_names = set()
    seen_phones = set()
    seen_urls = set()

    search_queries = [
        ("energia solar", "Rio de Janeiro, RJ"),
        ("empresa de energia solar", "Rio de Janeiro, RJ"),
        ("energia solar", "Niterói, RJ"),
        ("energia solar", "Duque de Caxias, RJ"),
        ("energia solar", "Nova Iguaçu, RJ"),
        ("energia solar", "São Gonçalo, RJ"),
        ("energia solar", "Barra da Tijuca, Rio de Janeiro"),
        ("energia solar", "Centro, Rio de Janeiro"),
        ("energia solar", "Jacarepaguá, Rio de Janeiro"),
        ("energia solar", "Campo Grande, Rio de Janeiro"),
        ("energia solar", "Belford Roxo, RJ"),
        ("energia solar", "São João de Meriti, RJ"),
        ("energia solar", "Petrópolis, RJ"),
    ]

    for idx, (query, location) in enumerate(search_queries, 1):
        if len(unique_leads) >= 100:
            print(f"\n[INFO] Meta de 100 leads atingida! (Total: {len(unique_leads)})")
            break

        print(f"\n[CONTRATO {idx}/{len(search_queries)}] Buscando '{query}' em '{location}'...")
        print("-" * 50)
        
        # Busca no Maps (limite de 30 por localidade/query para diversificar e ser rápido)
        leads = await scrape_google_maps(query, location, limit=30)
        print(f"[OK] Encontrados {len(leads)} resultados no Google Maps para esta busca.")

        added_in_round = 0
        for lead in leads:
            name = lead.get("name", "")
            phone = lead.get("phone", "")
            maps_url = lead.get("maps_url", "")

            norm_name = normalize(name)
            norm_phone = normalize(phone) if phone else ""

            # Verificar duplicidade
            is_dup = False
            if norm_name and norm_name in seen_names:
                is_dup = True
            if norm_phone and norm_phone in seen_phones:
                is_dup = True
            if maps_url and maps_url in seen_urls:
                is_dup = True

            if not is_dup:
                if norm_name:
                    seen_names.add(norm_name)
                if norm_phone:
                    seen_phones.add(norm_phone)
                if maps_url:
                    seen_urls.add(maps_url)
                
                unique_leads.append(lead)
                added_in_round += 1

                if len(unique_leads) >= 100:
                    break

        print(f"[STATUS] Adicionados {added_in_round} novos leads únicos nesta rodada.")
        print(f"[STATUS] Total acumulado de leads únicos: {len(unique_leads)}/100")

    # Limitar aos primeiros 100 leads
    final_leads = unique_leads[:100]
    print(f"\n[FIM SCOUT] Coleta finalizada com {len(final_leads)} leads únicos!")

    if not final_leads:
        print("[ERRO] Nenhum lead coletado. Abortando.")
        return

    # Formatar leads como "raw"
    formatted = [{"google": lead, "status": "raw"} for lead in final_leads]

    # Salvar arquivo de leads brutos (com timestamp)
    leads_json_path = save_leads_json(formatted, "leads")
    leads_csv_path = save_leads_csv(final_leads, "leads")
    print(f"[SALVO] Leads brutos salvos em:\n  JSON: {leads_json_path}\n  CSV: {leads_csv_path}")

    # --- FASE 2: Enriquecimento (Instagram) ---
    print("\n" + "="*50)
    print("[2/4] ENRICHER - Buscando perfis do Instagram...")
    print("="*50)
    enrich_result = await enrich_leads(formatted)
    
    # --- FASE 3: Análise do Instagram ---
    print("\n" + "="*50)
    print("[3/4] STALKER - Analisando perfis do Instagram...")
    print("="*50)
    analyze_result = await analyze_leads(enrich_result)

    # --- FASE 4: Relatório Final ---
    print("\n" + "="*50)
    print("[4/4] REPORTER - Gerando relatório de prospecção...")
    print("="*50)
    title = "Prospecção: 100 Empresas de Energia Solar - Rio de Janeiro e Região"
    report_result = generate_report(analyze_result, title)

    print("\n" + "="*60)
    print("PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"Total de leads processados: {len(final_leads)}")
    print(f"Relatório gerado em: {report_result['report_path']}")
    print(f"Planilha gerada em: {report_result['csv_path']}")
    print(f"JSON gerado em: {report_result['json_path']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
