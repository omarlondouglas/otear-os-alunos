import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Ensure squad is in path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.utils.browser import load_config, random_user_agent

async def main():
    config = load_config()
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True)
    
    # Test context WITH ignore_https_errors=True and WITHOUT google cookies
    context_args = {
        "viewport": {"width": 1280, "height": 800},
        "user_agent": random_user_agent(config),
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
        "ignore_https_errors": True,  # Ignore SSL cert issues
    }
    
    context = await browser.new_context(**context_args)
    page = await context.new_page()

    url1 = "http://www.viaenergiasolar.com.br/"
    print(f"Navigating directly to website with ignore_https_errors=True: {url1}...")
    try:
        await page.goto(url1, wait_until="domcontentloaded", timeout=15000)
        print("Success for website!")
        # Let's see if we find instagram links
        links = await page.locator("a[href*='instagram.com']").all()
        print(f"Found {len(links)} instagram links.")
        for link in links:
            print(f"Href: {await link.get_attribute('href')}")
    except Exception as e:
        print(f"Website failed with exception: {e}")

    url2 = "https://www.google.com/search?q=VIA+SOLAR+-+Energia+Solar+instagram"
    print(f"Navigating directly to Google Search without Google cookies: {url2}...")
    try:
        await page.goto(url2, wait_until="domcontentloaded", timeout=15000)
        print("Success for Google Search!")
        # Let's search for instagram links
        results = await page.locator("a[href*='instagram.com']").all()
        print(f"Found {len(results)} instagram links in Google results.")
        for r in results:
            print(f"Result: {await r.get_attribute('href')}")
    except Exception as e:
        print(f"Google Search failed with exception: {e}")

    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
