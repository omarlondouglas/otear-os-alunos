import asyncio
import re
import urllib.parse
import urllib.request
import json
from playwright.async_api import Page
from scripts.utils.browser import (
    load_config, create_browser, safe_goto, action_delay
)
from scripts.utils.csv_handler import (
    load_leads_json, save_leads_json, save_leads_csv, get_latest_file
)
from scripts.utils.scoring import score_lead, generate_approach_script
from scripts.utils.site_audit import audit_website


def clean_string(s: str) -> str:
    if not s:
        return ""
    # Remove characters like  and  and replace newlines with spaces
    cleaned = s.replace("\n", " ").strip()
    # Remove non-printable/icon characters (like private use area Unicode characters)
    cleaned = re.sub(r'[\ue000-\uf8ff]', '', cleaned)
    return cleaned.strip()


def extract_location_from_address(address: str) -> str:
    cleaned = clean_string(address)
    # Procurar por algo como "Rio das Ostras - RJ" ou "Rio de Janeiro - RJ"
    match = re.search(r"([^,]+ - [A-Z]{2})", cleaned)
    if match:
        return match.group(1).strip()
    return ""


def is_valid_cnpj(cnpj: str) -> bool:
    digits = re.sub(r"\D", "", cnpj or "")
    if len(digits) != 14 or digits == digits[0] * 14:
        return False

    def calc_digit(base: str, weights: list[int]) -> str:
        total = sum(int(digit) * weight for digit, weight in zip(base, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    first = calc_digit(digits[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = calc_digit(digits[:12] + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return digits[-2:] == first + second


def extract_cnpj_candidates(content: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    patterns = [
        r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b",
        r"(?i)cnpj\D{0,30}(\d{14})\b",
        r"\b\d{14}\b",
    ]

    for pattern in patterns:
        for match in re.findall(pattern, content or ""):
            raw = match if isinstance(match, str) else match[0]
            cnpj = re.sub(r"\D", "", raw)
            if cnpj not in seen and is_valid_cnpj(cnpj):
                seen.add(cnpj)
                candidates.append(cnpj)
    return candidates


async def find_cnpj_from_google(page: Page, name: str, location: str, config: dict) -> str | None:
    try:
        # Busca exata no Google
        query = f'"{name}" "{location}" cnpj'
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        if not await safe_goto(page, search_url, config):
            return None

        content = await page.content()
        cnpj_pattern = r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"
        matches = re.findall(cnpj_pattern, content)
        if matches:
            cnpj = re.sub(r"\D", "", matches[0])
            print(f"    CNPJ encontrado: {matches[0]} -> {cnpj}")
            return cnpj

        # Se não encontrar, tenta busca ampla (sem aspas)
        query_broad = f"{name} {location} cnpj"
        search_url_broad = f"https://www.google.com/search?q={urllib.parse.quote(query_broad)}"
        if not await safe_goto(page, search_url_broad, config):
            return None

        content_broad = await page.content()
        matches_broad = re.findall(cnpj_pattern, content_broad)
        if matches_broad:
            cnpj = re.sub(r"\D", "", matches_broad[0])
            print(f"    CNPJ encontrado (busca ampla): {matches_broad[0]} -> {cnpj}")
            return cnpj

    except Exception as e:
        print(f"    [WARN] Erro ao buscar CNPJ no Google: {e}")
    return None


async def find_cnpj_from_search(page: Page, name: str, location: str, config: dict) -> str | None:
    try:
        queries = [
            f'"{name}" "{location}" cnpj',
            f'"{name}" cnpj',
            f'{name} {location} cnpj',
            f'"{name}" site:cnpj.biz',
            f'"{name}" site:casadosdados.com.br',
            f'"{name}" site:cnpj.info',
        ]

        for query in queries:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            if not await safe_goto(page, search_url, config):
                continue

            candidates = extract_cnpj_candidates(await page.content())
            if candidates:
                print(f"    CNPJ encontrado: {candidates[0]} | query: {query}")
                return candidates[0]

            await action_delay(config)

    except Exception as e:
        print(f"    [WARN] Erro ao buscar CNPJ: {e}")
    return None


def get_owners_from_cnpj(cnpj: str) -> dict | None:
    # 1. Tenta BrasilAPI
    url_brasilapi = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        req = urllib.request.Request(url_brasilapi, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            owners = []
            for socio in data.get("qsa", []):
                owners.append({
                    "name": socio.get("nome_socio"),
                    "role": socio.get("qualificacao_socio")
                })
            return {
                "cnpj": cnpj,
                "razao_social": data.get("razao_social"),
                "nome_fantasia": data.get("nome_fantasia"),
                "owners": owners
            }
    except Exception as e:
        print(f"    [WARN] BrasilAPI falhou para CNPJ {cnpj}: {e}")

    # 2. Fallback para CNPJ.ws
    url_cnpjws = f"https://publica.cnpj.ws/cnpj/{cnpj}"
    try:
        req = urllib.request.Request(url_cnpjws, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            owners = []
            for socio in data.get("socios", []):
                owners.append({
                    "name": socio.get("nome"),
                    "role": socio.get("qualificacao_socio_descricao") or socio.get("funcao")
                })
            return {
                "cnpj": cnpj,
                "razao_social": data.get("razao_social"),
                "nome_fantasia": data.get("nome_fantasia"),
                "owners": owners
            }
    except Exception as e:
        print(f"    [WARN] CNPJ.ws falhou para CNPJ {cnpj}: {e}")

    # 3. Fallback para CNPJa Open API
    url_cnpja = f"https://open.cnpja.com/office/{cnpj}"
    try:
        req = urllib.request.Request(url_cnpja, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            company = data.get("company") or {}
            owners = []
            for member in company.get("members", []):
                person = member.get("person") or {}
                role = member.get("role") or {}
                owners.append({
                    "name": person.get("name"),
                    "role": role.get("text") or role.get("description")
                })
            return {
                "cnpj": cnpj,
                "razao_social": company.get("name"),
                "nome_fantasia": data.get("alias") or data.get("name"),
                "owners": owners
            }
    except Exception as e:
        print(f"    [WARN] CNPJa falhou para CNPJ {cnpj}: {e}")

    return None


async def find_cnpj_and_owners(page: Page, lead: dict, config: dict) -> dict | None:
    google = lead.get("google", {})
    name = google.get("name", "")
    address = google.get("address", "")
    
    if not name:
        return None
        
    location = extract_location_from_address(address)
    if not location:
        location = config.get("defaultLocation", "Brasil")

    print(f"  [CNPJ] Buscando CNPJ para '{name}' em '{location}'...")
    cnpj = await find_cnpj_from_search(page, name, location, config)
    if cnpj:
        # Pequeno delay antes de chamar API pública para evitar overload/rate limiting
        await asyncio.sleep(1.0)
        return get_owners_from_cnpj(cnpj)
    return None


async def find_instagram_handle(page: Page, lead: dict, config: dict) -> str | None:
    google = lead.get("google", {})
    name = google.get("name", "")
    website = google.get("website")

    # 1. Tentar extrair do website
    if website:
        handle = await find_instagram_from_website(page, website, config)
        if handle:
            return handle

    # 2. Buscar no Google
    handle = await find_instagram_from_google(page, name, config)
    if handle:
        return handle

    return None


async def find_instagram_from_website(page: Page, website: str, config: dict) -> str | None:
    try:
        if not await safe_goto(page, website, config):
            return None

        # Buscar links do Instagram na página
        instagram_links = await page.locator("a[href*='instagram.com']").all()
        for link in instagram_links:
            href = await link.get_attribute("href")
            if href:
                handle = extract_handle_from_url(href)
                if handle:
                    return handle

        # Buscar no texto da página
        content = await page.content()
        patterns = [
            r'instagram\.com/([a-zA-Z0-9_.]+)',
            r'@([a-zA-Z0-9_.]+)\s*(?:no\s+)?(?:instagram|insta)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match not in ("p", "reel", "stories", "explore", "accounts"):
                    return match

    except Exception:
        pass
    return None


async def find_instagram_from_google(page: Page, business_name: str, config: dict) -> str | None:
    try:
        search_query = f"{business_name} instagram"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

        if not await safe_goto(page, search_url, config):
            return None

        await page.wait_for_selector("#search", timeout=10000)

        # Procurar links do Instagram nos resultados
        results = await page.locator("a[href*='instagram.com']").all()
        for result in results[:3]:
            href = await result.get_attribute("href")
            if href:
                handle = extract_handle_from_url(href)
                if handle:
                    return handle

    except Exception:
        pass
    return None


def extract_handle_from_url(url: str) -> str | None:
    patterns = [
        r'instagram\.com/([a-zA-Z0-9_.]+)/?(?:\?|$)',
        r'instagram\.com/([a-zA-Z0-9_.]+)',
    ]
    excluded = {"p", "reel", "reels", "stories", "explore", "accounts", "about", "legal", "developer"}

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            handle = match.group(1).lower()
            if handle not in excluded and len(handle) > 1:
                return handle
    return None


async def enrich_leads(leads: list[dict]) -> list[dict]:
    config = load_config()
    batch_size = 10  # Reiniciar browser a cada N leads para evitar OOM

    enriched = []
    browser = None
    page = None

    try:
        for i, lead in enumerate(leads):
            # Criar/reiniciar browser a cada batch_size leads
            if i % batch_size == 0:
                if browser:
                    try:
                        await browser.close()
                    except Exception:
                        pass
                browser, context = await create_browser(config)
                page = await context.new_page()

            print(f"\n[{i+1}/{len(leads)}] Enriquecendo: {lead.get('google', {}).get('name', 'N/A')}")

            # Buscar Instagram
            handle = await find_instagram_handle(page, lead, config)
            if handle:
                lead["instagram"] = {"handle": handle, "profile_url": f"https://www.instagram.com/{handle}/"}
                print(f"  [OK] Instagram encontrado: @{handle}")
            else:
                lead["instagram"] = None
                print(f"  [X] Instagram nao encontrado")

            # Buscar CNPJ e Sócios (Donos)
            cnpj_info = await find_cnpj_and_owners(page, lead, config)
            if cnpj_info:
                lead["cnpj_info"] = cnpj_info
                owners_names = [o["name"] for o in cnpj_info.get("owners", [])]
                print(f"  [OK] CNPJ encontrado: {cnpj_info.get('cnpj')} | Sócios: {', '.join(owners_names) if owners_names else 'Nenhum'}")
            else:
                lead["cnpj_info"] = None
                print(f"  [X] CNPJ/Sócios nao encontrados")

            website = lead.get("google", {}).get("website")
            print("  [SITE] Auditando website...")
            lead["website_audit"] = audit_website(website, lead.get("google", {}).get("name"))
            audit = lead["website_audit"]
            if audit.get("status") == "bad":
                print(f"  [SITE] Problemas: {', '.join(audit.get('problems', [])[:3])}")
            elif audit.get("status") == "ok":
                print("  [SITE] Nenhum problema critico encontrado")
            else:
                print("  [SITE] Sem website cadastrado")

            # Scoring inicial (sem dados do Instagram ainda)
            lead["score"] = score_lead(lead)
            lead["status"] = "enriched"

            enriched.append(lead)

    except Exception as e:
        print(f"Erro no enriquecimento: {e}")
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass

    return enriched


async def run_enricher(filepath: str | None = None) -> dict:
    if filepath is None:
        filepath = get_latest_file("leads")
    if filepath is None:
        print("Nenhum arquivo de leads encontrado.")
        return {"leads": [], "json_path": None}

    leads = load_leads_json(filepath)
    print(f"\n[LOAD] Carregados {len(leads)} leads de {filepath}")

    enriched = await enrich_leads(leads)

    json_path = save_leads_json(enriched, "enriched")
    csv_rows = []
    for l in enriched:
        cnpj_info = l.get("cnpj_info") or {}
        owners = cnpj_info.get("owners") or []
        csv_rows.append({
            "name": l.get("google", {}).get("name"),
            "instagram": l.get("instagram", {}).get("handle") if l.get("instagram") else None,
            "cnpj": cnpj_info.get("cnpj"),
            "razao_social": cnpj_info.get("razao_social"),
            "socios": "; ".join(
                f"{o.get('name')} ({o.get('role')})" for o in owners if o.get("name")
            ),
            "score": l.get("score", {}).get("total", 0),
            "classification": l.get("score", {}).get("classification", "cold"),
        })
    csv_path = save_leads_csv(csv_rows, "enriched")

    print(f"\n[OK] {len(enriched)} leads enriquecidos!")
    print(f"[JSON] {json_path}")
    print(f"[CSV] {csv_path}")

    return {"leads": enriched, "json_path": json_path, "csv_path": csv_path}


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_enricher(filepath))
