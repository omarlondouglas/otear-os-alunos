"""Utilitarios de media: screenshots e downloads de video."""
import asyncio
from pathlib import Path
from playwright.async_api import Page

SQUAD_DIR = Path(__file__).parent.parent.parent
SCREENSHOT_DIR = SQUAD_DIR / "data" / "screenshots"


def ensure_screenshot_dir(handle: str) -> Path:
    """Cria diretorio de screenshots para um handle."""
    dir_path = SCREENSHOT_DIR / handle.replace("@", "").replace("/", "_")
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


async def take_grid_screenshot(page: Page, handle: str) -> str | None:
    """Captura screenshot do grid de posts do perfil Instagram."""
    try:
        dir_path = ensure_screenshot_dir(handle)
        screenshot_path = dir_path / "grid.png"

        # Scroll suave pra mostrar o grid
        await page.evaluate("window.scrollTo(0, 300)")
        await asyncio.sleep(1)

        await page.screenshot(path=str(screenshot_path), full_page=False)
        return str(screenshot_path)
    except Exception as e:
        print(f"  [WARN] Erro ao capturar grid screenshot: {e}")
        return None


async def take_post_screenshot(page: Page, handle: str, post_index: int) -> str | None:
    """Captura screenshot de um post aberto (modal)."""
    try:
        dir_path = ensure_screenshot_dir(handle)
        screenshot_path = dir_path / f"post_{post_index}.png"

        await page.screenshot(path=str(screenshot_path), full_page=False)
        return str(screenshot_path)
    except Exception as e:
        print(f"  [WARN] Erro ao capturar post screenshot: {e}")
        return None


async def extract_video_url(page: Page) -> str | None:
    """Extrai URL do video de um post aberto."""
    try:
        # Tentar tag <video> direta
        video_el = page.locator("video").first
        if await video_el.count() > 0:
            src = await video_el.get_attribute("src")
            if src and src.startswith("http"):
                return src

        # Tentar source dentro de video
        source_el = page.locator("video source").first
        if await source_el.count() > 0:
            src = await source_el.get_attribute("src")
            if src and src.startswith("http"):
                return src

        # Tentar extrair do blob via JS
        video_src = await page.evaluate("""
            () => {
                const video = document.querySelector('video');
                if (video && video.src && video.src.startsWith('http')) return video.src;
                if (video && video.currentSrc && video.currentSrc.startsWith('http')) return video.currentSrc;
                return null;
            }
        """)
        return video_src

    except Exception:
        return None


async def extract_thumbnail_url(page: Page) -> str | None:
    """Extrai URL da thumbnail/capa do post."""
    try:
        # Imagem principal do post (dentro do modal ou artigo)
        selectors = [
            "article img[style*='object-fit']",
            "div[role='dialog'] img[srcset]",
            "article img[srcset]",
            "div[role='dialog'] img[src*='instagram']",
        ]
        for selector in selectors:
            img = page.locator(selector).first
            if await img.count() > 0:
                src = await img.get_attribute("src")
                if src and "instagram" in src:
                    return src
        return None
    except Exception:
        return None
