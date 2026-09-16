import asyncio
import re
from playwright.async_api import Page
from scripts.utils.browser import (
    load_config, create_browser, safe_goto, human_scroll,
    action_delay, type_like_human, page_delay
)
from scripts.utils.csv_handler import DATA_DIR, load_leads_json, save_leads_json, save_leads_csv


# Seletor robusto: busca links que apontam para /maps/place/ dentro do feed
LISTING_SELECTOR = "div[role='feed'] a[href*='/maps/place/']"


def _clean_text(value: str | None) -> str:
    cleaned = re.sub(r"[\ue000-\uf8ff]", "", value or "")
    return re.sub(r"\s+", " ", cleaned).strip().lower()


def _phone_digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def _lead_keys(lead: dict) -> set[str]:
    google = lead.get("google") or lead
    keys: set[str] = set()

    maps_url = google.get("maps_url")
    if maps_url:
        keys.add(f"maps:{maps_url}")

    phone = _phone_digits(google.get("phone"))
    if phone:
        keys.add(f"phone:{phone}")

    name = _clean_text(google.get("name"))
    address = _clean_text(google.get("address"))
    if name and address:
        keys.add(f"name_address:{name}|{address}")

    return keys


def _load_existing_lead_keys() -> set[str]:
    keys: set[str] = set()
    leads_dir = DATA_DIR / "leads"
    if not leads_dir.exists():
        return keys

    for filepath in leads_dir.glob("*.json"):
        try:
            for lead in load_leads_json(str(filepath)):
                keys.update(_lead_keys(lead))
        except Exception as e:
            print(f"  [WARN] Nao foi possivel ler historico {filepath.name}: {e}")

    return keys


def dedupe_against_history(leads: list[dict]) -> tuple[list[dict], int]:
    existing_keys = _load_existing_lead_keys()
    batch_keys: set[str] = set()
    unique_leads: list[dict] = []
    duplicates = 0

    for lead in leads:
        keys = _lead_keys(lead)
        if keys and (keys & existing_keys or keys & batch_keys):
            duplicates += 1
            print(f"  [DUP] Ignorando lead repetido: {lead.get('name', 'N/A')}")
            continue

        batch_keys.update(keys)
        unique_leads.append(lead)

    return unique_leads, duplicates


async def _dismiss_consent(page: Page):
    """Fecha banners de consentimento/cookies do Google se aparecerem."""
    try:
        consent_btn = page.locator(
            "button:has-text('Aceitar'), "
            "button:has-text('Accept'), "
            "form[action*='consent'] button"
        ).first
        if await consent_btn.count() > 0:
            await consent_btn.click(timeout=3000)
            await asyncio.sleep(1)
    except Exception:
        pass


async def _collect_listing_hrefs(page: Page, limit: int, config: dict) -> list[str]:
    """Scroll no feed e coleta hrefs unicos de listings ate atingir o limite."""
    feed = page.locator("div[role='feed']")
    max_scrolls = config["limits"]["max_scroll_attempts"]
    seen_hrefs: list[str] = []
    scroll_attempts = 0
    stale_rounds = 0

    while len(seen_hrefs) < limit and scroll_attempts < max_scrolls:
        # Coletar todos os links visiveis no feed
        links = await page.locator(LISTING_SELECTOR).all()

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

        # Scroll dentro do feed
        await feed.evaluate("el => el.scrollTop = el.scrollHeight")
        await asyncio.sleep(1.5)
        scroll_attempts += 1

        # Verificar se chegou ao fim da lista
        end_marker = await page.locator("span.HlvSq").count()
        if end_marker > 0:
            print(f"  [INFO] Fim da lista atingido ({len(seen_hrefs)} resultados)")
            break

        # Se nao carregou novos resultados, tenta mais algumas vezes
        if len(seen_hrefs) == prev_count:
            stale_rounds += 1
            if stale_rounds >= 3:
                print(f"  [INFO] Sem novos resultados apos {stale_rounds} scrolls")
                break
            # Scroll mais agressivo
            await feed.evaluate(
                "el => el.scrollBy({ top: 1000, behavior: 'smooth' })"
            )
            await asyncio.sleep(2)
        else:
            stale_rounds = 0

    return seen_hrefs[:limit]


async def scrape_google_maps(query: str, location: str, limit: int = 20) -> list[dict]:
    config = load_config()
    browser, context = await create_browser(config)
    page = await context.new_page()

    leads = []

    try:
        search_term = f"{query} em {location}"
        search_url = f"{config['google_maps']['search_url']}{search_term.replace(' ', '+')}"

        if not await safe_goto(page, search_url, config):
            return leads

        # Fechar banners de consentimento
        await _dismiss_consent(page)

        # Aguardar resultados carregarem
        try:
            await page.wait_for_selector("div[role='feed']", timeout=15000)
        except Exception:
            print("[ERRO] Feed de resultados nao encontrado")
            return leads

        await action_delay(config)

        # Fase 1: Coletar todos os hrefs via scroll
        print(f"  [SCROLL] Coletando links dos resultados...")
        hrefs = await _collect_listing_hrefs(page, limit, config)
        print(f"  [OK] {len(hrefs)} links coletados\n")

        if not hrefs:
            return leads

        # Fase 2: Navegar em cada link e extrair dados
        for i, href in enumerate(hrefs):
            try:
                lead = await extract_listing_data(page, href, config)
                if lead:
                    lead["maps_url"] = href
                    leads.append(lead)
                    print(f"[{len(leads)}/{len(hrefs)}] {lead.get('name', 'N/A')}")

                await page_delay(config)

            except Exception as e:
                print(f"Erro no listing {i+1}: {e}")
                continue

    except Exception as e:
        print(f"Erro geral no scraping: {e}")
    finally:
        await browser.close()

    return leads


async def extract_listing_data(page: Page, url: str, config: dict) -> dict | None:
    try:
        if not await safe_goto(page, url, config):
            return None

        await page.wait_for_selector("h1", timeout=10000)
        await action_delay(config)

        data = {}

        # Nome
        name_el = page.locator("h1").first
        if await name_el.count() > 0:
            data["name"] = await name_el.inner_text()

        # Categoria
        category_el = page.locator("button[jsaction*='category']").first
        if await category_el.count() > 0:
            data["category"] = await category_el.inner_text()

        # Rating e reviews
        rating_el = page.locator("div.F7nice span[aria-hidden='true']").first
        if await rating_el.count() > 0:
            rating_text = await rating_el.inner_text()
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
                    data["reviews_count"] = int(numbers[0])
                except ValueError:
                    pass

        # Endereço
        address_el = page.locator("button[data-item-id='address']").first
        if await address_el.count() > 0:
            data["address"] = (await address_el.inner_text()).strip()

        # Telefone
        phone_el = page.locator("button[data-item-id*='phone']").first
        if await phone_el.count() > 0:
            data["phone"] = (await phone_el.inner_text()).strip()

        # Website
        website_el = page.locator("a[data-item-id='authority']").first
        if await website_el.count() > 0:
            data["website"] = await website_el.get_attribute("href")

        # Horario de funcionamento
        hours_el = page.locator("div[aria-label*='horario'], div[aria-label*='horário'], div[aria-label*='hours']").first
        if await hours_el.count() > 0:
            data["opening_hours"] = await hours_el.get_attribute("aria-label")

        if not data.get("name"):
            return None

        return data

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return None


async def run_scraper(query: str, location: str, limit: int = 20) -> dict:
    print(f"\n[SCOUT] Buscando '{query}' em '{location}' (limite: {limit})...\n")

    leads = await scrape_google_maps(query, location, limit)
    total_found = len(leads)
    leads, duplicates_skipped = dedupe_against_history(leads)

    if not leads:
        if duplicates_skipped:
            print(f"Nenhum lead novo encontrado. {duplicates_skipped} repetidos ignorados.")
        else:
            print("Nenhum lead encontrado.")
        return {
            "leads": [],
            "json_path": None,
            "csv_path": None,
            "total_found": total_found,
            "duplicates_skipped": duplicates_skipped,
        }

    # Formatar para salvar
    formatted = [{"google": lead, "status": "raw"} for lead in leads]

    json_path = save_leads_json(formatted, "leads")
    csv_path = save_leads_csv([lead for lead in leads], "leads")

    print(f"\n[OK] {len(leads)} leads novos encontrados!")
    if duplicates_skipped:
        print(f"[DUP] {duplicates_skipped} leads repetidos ignorados")
    print(f"[JSON] {json_path}")
    print(f"[CSV] {csv_path}")

    return {
        "leads": formatted,
        "json_path": json_path,
        "csv_path": csv_path,
        "total_found": total_found,
        "duplicates_skipped": duplicates_skipped,
    }


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "restaurantes"
    location = sys.argv[2] if len(sys.argv) > 2 else "São Paulo"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    asyncio.run(run_scraper(query, location, limit))
