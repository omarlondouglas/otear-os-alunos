"""
Google Maps Scraper - Standalone Playwright Script
Busca empresas no Google Maps via Playwright com cookie injection.
Funciona APENAS em IPs residenciais (não funciona em VPS/datacenter).

Uso:
    python scraper.py "termo de busca" "cidade" [limite]

Exemplo:
    python scraper.py "restaurantes" "São Paulo" 20
    python scraper.py "empresas de energia solar" "Rio das Ostras" 30

Requisitos:
    pip install playwright pyyaml
    playwright install chromium

Saída:
    /root/prospect/data/leads_{termo}_{timestamp}.json
    /root/prospect/data/leads_{termo}_{timestamp}.csv
"""
import asyncio
import json
import csv
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

LOCALE = "pt-BR"
TIMEZONE = "America/Sao_Paulo"
VIEWPORT = {"width": 1366, "height": 768}
HEADLESS = True
MAX_SCROLLS = 20
ACTION_DELAY_MIN = 2.0
ACTION_DELAY_MAX = 4.0
PAGE_DELAY_MIN = 3.0
PAGE_DELAY_MAX = 6.0
TIMEOUT = 30000

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

OUTPUT_DIR = Path("/root/prospect/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def random_delay(min_s, max_s):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def collect_listing_hrefs(page, limit):
    seen_hrefs = []
    scroll_attempts = 0
    stale_rounds = 0

    while len(seen_hrefs) < limit and scroll_attempts < MAX_SCROLLS:
        links = await page.locator("div[role='feed'] a[href*='/maps/place/']").all()
        for link in links:
            try:
                href = await link.get_attribute("href", timeout=5000)
                if href and "/maps/place/" in href and href not in seen_hrefs:
                    seen_hrefs.append(href)
            except Exception:
                continue

        if len(seen_hrefs) >= limit:
            break

        prev_count = len(seen_hrefs)
        feed = page.locator("div[role='feed']")
        if await feed.count() > 0:
            await feed.evaluate("el => el.scrollTop = el.scrollHeight")
        else:
            await page.mouse.wheel(0, 500)

        await asyncio.sleep(1.5)
        scroll_attempts += 1

        end_marker = await page.locator("span.HlvSq").count()
        if end_marker > 0:
            print(f"  [INFO] Fim da lista ({len(seen_hrefs)} resultados)")
            break

        if len(seen_hrefs) == prev_count:
            stale_rounds += 1
            if stale_rounds >= 3:
                print(f"  [INFO] Sem novos resultados após {stale_rounds} scrolls")
                break
            if await feed.count() > 0:
                await feed.evaluate("el => el.scrollBy({ top: 1000, behavior: 'smooth' })")
            await asyncio.sleep(2)
        else:
            stale_rounds = 0

    return seen_hrefs[:limit]


async def extract_listing_data(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT)
        await page.wait_for_selector("h1", timeout=10000)
        await random_delay(ACTION_DELAY_MIN, ACTION_DELAY_MAX)

        data = {}

        name_el = page.locator("h1").first
        if await name_el.count() > 0:
            data["nome"] = (await name_el.inner_text()).strip()

        cat_el = page.locator("button[jsaction*='category']").first
        if await cat_el.count() > 0:
            data["categoria"] = (await cat_el.inner_text()).strip()

        rating_el = page.locator("div.F7nice span[aria-hidden='true']").first
        if await rating_el.count() > 0:
            rating_text = (await rating_el.inner_text()).strip()
            try:
                data["rating"] = float(rating_text.replace(",", "."))
            except ValueError:
                pass

        reviews_el = page.locator("div.F7nice span[aria-label*='coment']").first
        if await reviews_el.count() == 0:
            reviews_el = page.locator("div.F7nice span[aria-label*='review']").first
        if await reviews_el.count() > 0:
            reviews_text = await reviews_el.get_attribute("aria-label") or ""
            numbers = re.findall(r"[\d.]+", reviews_text.replace(".", ""))
            if numbers:
                try:
                    data["reviews"] = int(numbers[0])
                except ValueError:
                    pass

        addr_el = page.locator("button[data-item-id='address']").first
        if await addr_el.count() > 0:
            data["endereco"] = (await addr_el.inner_text()).strip()

        phone_el = page.locator("button[data-item-id*='phone']").first
        if await phone_el.count() > 0:
            data["telefone"] = (await phone_el.inner_text()).strip()

        web_el = page.locator("a[data-item-id='authority']").first
        if await web_el.count() > 0:
            data["website"] = await web_el.get_attribute("href")

        data["maps_url"] = url

        if not data.get("nome"):
            return None
        return data

    except Exception as e:
        print(f"  [ERRO] Extraindo: {e}")
        return None


async def scrape(query, location, limit=20):
    search_term = f"{query} em {location}"
    search_url = f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}"

    print(f"\n[SCOUT] Buscando '{query}' em '{location}' (limite: {limit})...")
    print(f"  URL: {search_url}\n")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            viewport=VIEWPORT,
            user_agent=random.choice(USER_AGENTS),
            locale=LOCALE,
            timezone_id=TIMEZONE,
        )
        page = await context.new_page()
        leads = []

        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=TIMEOUT)
            await asyncio.sleep(3)

            if "consent.google.com" in page.url:
                print("  [ERRO] Redirecionado para consent.google.com")
                print("  [ERRO] IP datacenter detectado - o Google Maps bloqueia VPS/cloud")
                print("  [DICA] Rode este script na sua máquina local (IP residencial)")
                await browser.close()
                return []

            try:
                await page.wait_for_selector("div[role='feed']", timeout=15000)
                print("  [OK] Feed carregado!")
            except Exception:
                print("  [WARN] Feed não encontrado, tentando reload...")
                await page.reload(wait_until="domcontentloaded")
                await asyncio.sleep(5)
                try:
                    await page.wait_for_selector("div[role='feed']", timeout=15000)
                    print("  [OK] Feed carregado na 2ª tentativa!")
                except Exception:
                    print(f"  [ERRO] URL atual: {page.url}")
                    await page.screenshot(path=str(OUTPUT_DIR / "debug_screenshot.png"))
                    print("  [DEBUG] Screenshot salvo em data/debug_screenshot.png")
                    await browser.close()
                    return []

            await random_delay(ACTION_DELAY_MIN, ACTION_DELAY_MIN)

            print("  [SCROLL] Coletando links...")
            hrefs = await collect_listing_hrefs(page, limit)
            print(f"  [OK] {len(hrefs)} links coletados\n")

            if not hrefs:
                await browser.close()
                return []

            for i, href in enumerate(hrefs):
                try:
                    lead = await extract_listing_data(page, href)
                    if lead:
                        leads.append(lead)
                        print(f"  [{len(leads)}/{len(hrefs)}] {lead.get('nome', 'N/A')}")
                    await random_delay(PAGE_DELAY_MIN, PAGE_DELAY_MAX)
                except Exception as e:
                    print(f"  [ERRO] Listing {i+1}: {e}")
                    continue

        except Exception as e:
            print(f"  [ERRO] Scraping falhou: {e}")
        finally:
            await browser.close()

    return leads


def save_results(leads, query, location):
    if not leads:
        return None, None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_").lower()

    json_path = OUTPUT_DIR / f"leads_{safe_query}_{timestamp}.json"
    output = {
        "busca": f"{query} em {location}",
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(leads),
        "leads": leads,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    csv_path = OUTPUT_DIR / f"leads_{safe_query}_{timestamp}.csv"
    fieldnames = ["nome", "categoria", "rating", "reviews", "endereco", "telefone", "website", "maps_url"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    return str(json_path), str(csv_path)


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "restaurantes"
    location = sys.argv[2] if len(sys.argv) > 2 else "São Paulo"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    leads = asyncio.run(scrape(query, location, limit))

    if leads:
        json_path, csv_path = save_results(leads, query, location)
        print(f"\n[OK] {len(leads)} leads encontrados!")
        print(f"[JSON] {json_path}")
        print(f"[CSV] {csv_path}")
    else:
        print("\n[ERRO] Nenhum lead encontrado")
