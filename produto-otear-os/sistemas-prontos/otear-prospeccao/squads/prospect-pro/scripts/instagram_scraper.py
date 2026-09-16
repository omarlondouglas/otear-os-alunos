import asyncio
import re
from collections import Counter
from datetime import datetime
from playwright.async_api import Page
from scripts.utils.browser import (
    load_config, create_browser, safe_goto, human_scroll,
    action_delay, instagram_login
)
from scripts.utils.csv_handler import (
    load_leads_json, save_leads_json, get_latest_file
)
from scripts.utils.scoring import score_lead, generate_approach_script
from scripts.utils.media import (
    take_grid_screenshot, take_post_screenshot,
    extract_video_url, extract_thumbnail_url
)


async def scrape_instagram_profile(page: Page, handle: str, config: dict) -> dict | None:
    try:
        profile_url = f"https://www.instagram.com/{handle}/"
        if not await safe_goto(page, profile_url, config):
            return None

        current_url = page.url
        if "login" in current_url or "accounts/login" in current_url:
            print(f"  [WARN] Instagram requer login para @{handle}")
            return {"handle": handle, "profile_url": profile_url}

        # Aguardar perfil carregar
        try:
            await page.wait_for_selector("header", timeout=10000)
        except Exception:
            print(f"  [WARN] Timeout ao carregar perfil @{handle}")
            return {"handle": handle, "profile_url": profile_url}

        await action_delay(config)

        data = {"handle": handle, "profile_url": profile_url}

        # Extrair meta dados
        try:
            meta_el = page.locator("meta[name='description']").first
            if await meta_el.count() > 0:
                meta_content = await meta_el.get_attribute("content")
                if meta_content:
                    parsed = parse_meta_description(meta_content)
                    data.update(parsed)
        except Exception:
            pass

        # Bio
        try:
            bio_el = page.locator("header section > div > span, header section div.-vDIg span").first
            if await bio_el.count() > 0:
                data["bio"] = await bio_el.inner_text()
        except Exception:
            pass

        # Bio link
        try:
            bio_link_el = page.locator("header a[rel*='nofollow'], header a[href*='l.instagram.com']").first
            if await bio_link_el.count() > 0:
                data["bio_link"] = await bio_link_el.get_attribute("href")
        except Exception:
            pass

        # Conta business
        try:
            category_el = page.locator("header div[class*='category'], header a[class*='category']").first
            if await category_el.count() > 0:
                data["is_business"] = True
        except Exception:
            pass

        # Verificado
        try:
            verified_el = page.locator("header svg[aria-label*='Verified'], header span[title='Verified']").first
            data["is_verified"] = await verified_el.count() > 0
        except Exception:
            data["is_verified"] = False

        # Screenshot do grid
        if config.get("instagram", {}).get("save_screenshots", False):
            grid_ss = await take_grid_screenshot(page, handle)
            if grid_ss:
                data["grid_screenshot"] = grid_ss

        # Scraping profundo dos posts
        posts_to_analyze = config.get("instagram", {}).get("posts_to_analyze", 12)
        posts_data = await scrape_recent_posts_deep(page, handle, posts_to_analyze, config)
        if posts_data:
            data["recent_posts"] = posts_data
            data.update(calculate_engagement(data, posts_data))
            data["content_metrics"] = calculate_content_metrics(posts_data)

        return data

    except Exception as e:
        print(f"  Erro ao scraper @{handle}: {e}")
        return None


async def scrape_recent_posts_deep(
    page: Page, handle: str, max_posts: int, config: dict
) -> list[dict]:
    """Scraping profundo: abre cada post e extrai dados completos."""
    posts = []
    save_screenshots = config.get("instagram", {}).get("save_screenshots", False)

    try:
        # Coletar links dos posts no grid
        post_links = await page.locator(
            "article a[href*='/p/'], "
            "article a[href*='/reel/'], "
            "main a[href*='/p/'], "
            "main a[href*='/reel/']"
        ).all()

        posts_count = min(len(post_links), max_posts)
        if posts_count == 0:
            return posts

        # Coletar hrefs primeiro (evitar stale elements)
        hrefs = []
        for link in post_links[:posts_count]:
            try:
                href = await link.get_attribute("href")
                if href:
                    hrefs.append(href)
            except Exception:
                continue

        # Agora clicar no primeiro post para abrir o modal
        try:
            await post_links[0].click(timeout=5000)
            await asyncio.sleep(2)
        except Exception:
            # Fallback: navegar direto para o primeiro post
            if hrefs:
                full_url = hrefs[0] if hrefs[0].startswith("http") else f"https://www.instagram.com{hrefs[0]}"
                await safe_goto(page, full_url, config)

        # Extrair dados de cada post navegando com seta direita
        for i in range(posts_count):
            try:
                post_data = await extract_post_data(page, i, handle, save_screenshots, config)
                if post_data:
                    # Adicionar href se temos
                    if i < len(hrefs):
                        href = hrefs[i]
                        if not href.startswith("http"):
                            href = f"https://www.instagram.com{href}"
                        post_data["url"] = href
                    posts.append(post_data)

                # Navegar para proximo post (seta direita)
                if i < posts_count - 1:
                    next_btn = page.locator(
                        "button[aria-label='Next'], "
                        "button[aria-label='Avançar'], "
                        "button[aria-label='Próximo'], "
                        "div[role='dialog'] button svg[aria-label='Next']"
                    ).first

                    if await next_btn.count() > 0:
                        await next_btn.click(timeout=3000)
                        await asyncio.sleep(1.5)
                    else:
                        # Tentar keyboard
                        await page.keyboard.press("ArrowRight")
                        await asyncio.sleep(1.5)

            except Exception as e:
                print(f"    [WARN] Erro no post {i+1}: {e}")
                continue

        # Fechar modal
        try:
            await page.keyboard.press("Escape")
            await asyncio.sleep(1)
        except Exception:
            pass

    except Exception as e:
        print(f"  [WARN] Erro ao scraper posts: {e}")

    return posts


async def extract_post_data(
    page: Page, index: int, handle: str, save_screenshots: bool, config: dict
) -> dict | None:
    """Extrai dados completos de um post aberto (modal ou pagina)."""
    try:
        data = {}

        # Detectar tipo de post
        has_video = await page.locator("video").count() > 0
        has_carousel = await page.locator(
            "button[aria-label*='carousel'], "
            "button[aria-label*='Go to slide'], "
            "div[class*='carousel'] button"
        ).count() > 0

        is_reel = "/reel/" in page.url if hasattr(page, 'url') else False

        if has_video or is_reel:
            data["type"] = "reel" if is_reel else "video"
            data["video_url"] = await extract_video_url(page)
        elif has_carousel:
            data["type"] = "carousel"
        else:
            data["type"] = "photo"

        # Thumbnail
        data["thumbnail_url"] = await extract_thumbnail_url(page)

        # Curtidas
        likes = await _extract_likes(page)
        data["likes"] = likes

        # Comentarios
        comments = await _extract_comments_count(page)
        data["comments"] = comments

        # Caption
        caption = await _extract_caption(page)
        data["caption"] = caption

        # Hashtags (extrair da caption)
        if caption:
            data["hashtags"] = re.findall(r"#(\w+)", caption)
        else:
            data["hashtags"] = []

        # Screenshot do post
        if save_screenshots:
            ss_path = await take_post_screenshot(page, handle, index + 1)
            if ss_path:
                data["screenshot_path"] = ss_path

        return data

    except Exception as e:
        print(f"    [WARN] Erro ao extrair dados do post: {e}")
        return None


async def _extract_likes(page: Page) -> int:
    """Extrai numero de curtidas do post."""
    try:
        # Seletor para "X curtidas" ou "X likes"
        selectors = [
            "section span a span",  # "123 likes" link
            "section button span",  # "123 curtidas" button
            "span a[href*='liked_by']",
            "div[role='dialog'] section span",
        ]
        for selector in selectors:
            el = page.locator(selector).first
            if await el.count() > 0:
                text = await el.inner_text()
                num = parse_number(text)
                if num > 0:
                    return num

        # Tentar aria-label "X likes"
        like_section = page.locator("section[class*=''], div[class*='']").first
        all_spans = await page.locator("section span").all()
        for span in all_spans[:10]:
            try:
                text = await span.inner_text()
                if any(w in text.lower() for w in ["curtida", "like", "gostaram"]):
                    num = parse_number(text)
                    if num > 0:
                        return num
            except Exception:
                continue

    except Exception:
        pass
    return 0


async def _extract_comments_count(page: Page) -> int:
    """Extrai numero de comentarios."""
    try:
        # Link "Ver todos os X comentarios"
        comments_link = page.locator(
            "a[href*='comments'], "
            "span:has-text('comentário'), "
            "span:has-text('comment')"
        ).first
        if await comments_link.count() > 0:
            text = await comments_link.inner_text()
            numbers = re.findall(r"[\d,.]+", text.replace(".", ""))
            if numbers:
                return int(numbers[0].replace(",", ""))
    except Exception:
        pass
    return 0


async def _extract_caption(page: Page) -> str | None:
    """Extrai a legenda/caption do post."""
    try:
        # Caption geralmente esta em um span dentro de h1 ou div apos o username
        caption_selectors = [
            "div[role='dialog'] h1",
            "div[role='dialog'] span[dir='auto']",
            "article span[dir='auto']",
            "ul li span[dir='auto']",
        ]
        for selector in caption_selectors:
            el = page.locator(selector).first
            if await el.count() > 0:
                text = await el.inner_text()
                if text and len(text) > 5:
                    return text.strip()
    except Exception:
        pass
    return None


def parse_meta_description(meta: str) -> dict:
    data = {}
    patterns = {
        "followers": r"([\d,.]+[KMkm]?)\s*(?:Followers|Seguidores)",
        "following": r"([\d,.]+[KMkm]?)\s*(?:Following|Seguindo)",
        "posts_count": r"([\d,.]+[KMkm]?)\s*(?:Posts|Publicações|Publicacoes)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, meta, re.IGNORECASE)
        if match:
            data[key] = parse_number(match.group(1))

    bio_match = re.search(r"Posts?\s*[-\u2013\u2014]\s*(.+?)(?:\s*$)", meta)
    if bio_match:
        data["bio"] = bio_match.group(1).strip()

    return data


def parse_number(text: str) -> int:
    text = text.strip().replace(",", "").replace(".", "")
    multiplier = 1
    if text.lower().endswith("k"):
        multiplier = 1000
        text = text[:-1]
    elif text.lower().endswith("m"):
        multiplier = 1000000
        text = text[:-1]
    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def calculate_engagement(profile: dict, posts: list[dict]) -> dict:
    followers = profile.get("followers", 0)
    if not followers or not posts:
        return {}

    total_likes = sum(p.get("likes", 0) for p in posts)
    total_comments = sum(p.get("comments", 0) for p in posts)
    post_count = len(posts)

    avg_likes = total_likes / post_count if post_count else 0
    avg_comments = total_comments / post_count if post_count else 0
    engagement_rate = ((avg_likes + avg_comments) / followers * 100) if followers > 0 else 0

    return {
        "engagement_rate": round(engagement_rate, 2),
        "avg_likes": round(avg_likes, 1),
        "avg_comments": round(avg_comments, 1),
    }


def calculate_content_metrics(posts: list[dict]) -> dict:
    """Calcula metricas de conteudo a partir dos posts."""
    if not posts:
        return {}

    types = Counter(p.get("type", "unknown") for p in posts)
    all_hashtags = []
    total_caption_len = 0
    captions_with_cta = 0

    cta_keywords = [
        "link", "bio", "clique", "acesse", "confira", "agende",
        "marque", "envie", "chame", "whatsapp", "dm", "saiba mais",
        "compre", "garanta", "reserve",
    ]

    for post in posts:
        hashtags = post.get("hashtags", [])
        all_hashtags.extend(hashtags)

        caption = post.get("caption", "") or ""
        total_caption_len += len(caption)

        if any(kw in caption.lower() for kw in cta_keywords):
            captions_with_cta += 1

    hashtag_counts = Counter(all_hashtags)
    top_hashtags = [tag for tag, _ in hashtag_counts.most_common(10)]

    total = len(posts)
    return {
        "video_count": types.get("video", 0) + types.get("reel", 0),
        "photo_count": types.get("photo", 0),
        "carousel_count": types.get("carousel", 0),
        "video_ratio": round((types.get("video", 0) + types.get("reel", 0)) / total * 100, 1),
        "top_hashtags": top_hashtags,
        "avg_caption_length": round(total_caption_len / total) if total else 0,
        "posts_with_cta": captions_with_cta,
        "cta_ratio": round(captions_with_cta / total * 100, 1) if total else 0,
    }


async def analyze_leads(leads: list[dict], posts_to_analyze: int = 12) -> list[dict]:
    config = load_config()
    config["instagram"]["posts_to_analyze"] = posts_to_analyze
    batch_size = 10

    analyzed = []
    browser = None
    page = None
    insta_index = 0
    logged_in = False

    try:
        for i, lead in enumerate(leads):
            insta = lead.get("instagram")
            if not insta or not insta.get("handle"):
                lead["status"] = "analyzed"
                lead["score"] = score_lead(lead)
                lead["approach_script"] = generate_approach_script(lead, lead["score"])
                analyzed.append(lead)
                continue

            # Criar/reiniciar browser a cada batch_size perfis
            if insta_index % batch_size == 0:
                if browser:
                    try:
                        await browser.close()
                    except Exception:
                        pass
                browser, context = await create_browser(config)
                page = await context.new_page()
                logged_in = False

            # Login no Instagram (uma vez por sessao de browser)
            if not logged_in and config.get("instagram", {}).get("login_required", False):
                logged_in = await instagram_login(page, config)

            handle = insta["handle"]
            print(f"\n[{i+1}/{len(leads)}] Analisando Instagram: @{handle}")

            profile = await scrape_instagram_profile(page, handle, config)
            if profile:
                lead["instagram"] = profile

                followers = profile.get("followers", 'N/A')
                engagement = profile.get("engagement_rate", 'N/A')
                post_count = len(profile.get("recent_posts", []))
                content = profile.get("content_metrics", {})
                video_ratio = content.get("video_ratio", 0)

                print(f"  [DATA] Followers: {followers} | "
                      f"Engagement: {engagement}% | "
                      f"Posts analisados: {post_count} | "
                      f"Video ratio: {video_ratio}%")

            lead["score"] = score_lead(lead)
            lead["approach_script"] = generate_approach_script(lead, lead["score"])
            lead["status"] = "analyzed"

            analyzed.append(lead)
            insta_index += 1

    except Exception as e:
        print(f"Erro na analise: {e}")
    finally:
        if browser:
            try:
                await browser.close()
            except Exception:
                pass

    return analyzed


async def run_analyzer(filepath: str | None = None, posts_to_analyze: int = 12) -> dict:
    if filepath is None:
        filepath = get_latest_file("enriched")
    if filepath is None:
        print("Nenhum arquivo de leads enriquecidos encontrado.")
        return {"leads": [], "json_path": None}

    leads = load_leads_json(filepath)
    print(f"\n[LOAD] Carregados {len(leads)} leads de {filepath}")

    analyzed = await analyze_leads(leads, posts_to_analyze)

    json_path = save_leads_json(analyzed, "enriched")

    hot = sum(1 for l in analyzed if l.get("score", {}).get("classification") == "hot")
    warm = sum(1 for l in analyzed if l.get("score", {}).get("classification") == "warm")
    cold = sum(1 for l in analyzed if l.get("score", {}).get("classification") == "cold")

    print(f"\n[OK] {len(analyzed)} leads analisados!")
    print(f"Hot: {hot} | Warm: {warm} | Cold: {cold}")
    print(f"[JSON] {json_path}")

    return {"leads": analyzed, "json_path": json_path, "hot": hot, "warm": warm, "cold": cold}


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_analyzer(filepath))
