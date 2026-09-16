import asyncio
import sys
import traceback
from pathlib import Path

# Ensure squad is in path
SQUAD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SQUAD_DIR))

from scripts.utils.browser import load_config, create_browser, safe_goto
from scripts.lead_enricher import find_instagram_from_google, find_instagram_from_website, extract_handle_from_url

async def main():
    config = load_config()
    browser, context = await create_browser(config)
    page = await context.new_page()

    lead_name = "VIA SOLAR - Energia Solar"
    lead_website = "http://www.viaenergiasolar.com.br/"

    print(f"--- Debugging Instagram enrichment for '{lead_name}' ---")

    # 1. Test website enrichment
    print("\n[DEBUG] Testing Website Enrichment...")
    try:
        if lead_website:
            print(f"Navigating to website: {lead_website}")
            if await safe_goto(page, lead_website, config):
                print("Successfully loaded website.")
                # Print all instagram links found
                links = await page.locator("a[href*='instagram.com']").all()
                print(f"Found {len(links)} links matching 'instagram.com'.")
                for link in links:
                    href = await link.get_attribute("href")
                    print(f"Link href: {href}")
                    handle = extract_handle_from_url(href)
                    print(f"Extracted handle: {handle}")
                
                content = await page.content()
                print(f"Content length: {len(content)}")
            else:
                print("Failed to load website.")
    except Exception as e:
        print("Exception during website search:")
        traceback.print_exc()

    # 2. Test Google enrichment
    print("\n[DEBUG] Testing Google Enrichment...")
    try:
        search_query = f"{lead_name} instagram"
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        print(f"Navigating to Google Search: {search_url}")
        
        if await safe_goto(page, search_url, config):
            print("Successfully loaded Google Search page.")
            # Wait for search container
            try:
                await page.wait_for_selector("#search", timeout=5000)
                print("Selector '#search' found.")
            except Exception as e:
                print(f"Selector '#search' NOT found: {e}")
                # Save screenshot of what google search actually looks like
                ss_path = "debug_google_search.png"
                await page.screenshot(path=ss_path)
                print(f"Saved debug screenshot to {ss_path}")
            
            # Print all instagram.com hrefs found on page
            results = await page.locator("a[href*='instagram.com']").all()
            print(f"Found {len(results)} instagram links in Google results.")
            for r in results:
                href = await r.get_attribute("href")
                print(f"Result href: {href}")
                handle = extract_handle_from_url(href)
                print(f"Extracted handle: {handle}")
        else:
            print("Failed to load Google Search.")
    except Exception as e:
        print("Exception during Google Search:")
        traceback.print_exc()

    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
