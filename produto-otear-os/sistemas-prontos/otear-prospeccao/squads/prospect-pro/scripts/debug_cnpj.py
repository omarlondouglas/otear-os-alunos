import asyncio
import sys
import traceback
from pathlib import Path

# Ensure squad is in path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.utils.browser import load_config, create_browser
from scripts.lead_enricher import find_cnpj_and_owners, clean_string, extract_location_from_address

async def main():
    config = load_config()
    browser, context = await create_browser(config)
    page = await context.new_page()

    # Test cases
    test_leads = [
        {
            "google": {
                "name": "Star Solar Energia Renovável",
                "address": "R. E - Palmital, Rio das Ostras - RJ, 28891-070"
            }
        },
        {
            "google": {
                "name": "VIA SOLAR - Energia Solar",
                "address": "Estr. dos Bandeirantes, 3748 - Taquara, Rio de Janeiro - RJ, 22775-114"
            }
        }
    ]

    print("--- Debugging CNPJ and Owners Enrichment ---")

    for lead in test_leads:
        name = lead["google"]["name"]
        address = lead["google"]["address"]
        print(f"\n[TEST] Lead: {name}")
        print(f"Address: {address}")
        
        try:
            info = await find_cnpj_and_owners(page, lead, config)
            print(f"Result: {info}")
        except Exception as e:
            print(f"Exception during test for {name}:")
            traceback.print_exc()

    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
