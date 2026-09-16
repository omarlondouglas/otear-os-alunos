"""
Instagram Playwright Scraper — captura prints visuais de perfis publicos.

Diferente do `instagram_lister` (instaloader) que pega METADATA + URLs,
este servico usa Chromium headless com sessao persistente para tirar
SCREENSHOTS reais do perfil — util pra dar referencia visual ao cliente
("quero copiar a pegada visual desse perfil").

Sessao persistente em /app/storage/.playwright_profile/ — primeiro acesso ao
Instagram pode pedir login manual via VNC ou logando na maquina host e
copiando o perfil.

Uso:
    from app.services.instagram_playwright import capture_profile_screenshots

    result = await capture_profile_screenshots("@hormozi", count=9)
    # result = {"profile": "@hormozi", "grid_path": "/app/storage/.../grid.png",
    #          "post_paths": [...], "captured_at": "..."}
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "/app/storage"))
PLAYWRIGHT_BROWSERS_PATH = Path(
    os.getenv("PLAYWRIGHT_BROWSERS_PATH", str(STORAGE_PATH / ".playwright_browsers"))
)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS_PATH))
PROFILE_DIR = Path(
    os.getenv("INSTAGRAM_PLAYWRIGHT_PROFILE_DIR", str(STORAGE_PATH / ".playwright_profile"))
)
PLAYWRIGHT_CHANNEL = os.getenv("INSTAGRAM_PLAYWRIGHT_CHANNEL", "").strip() or None
SCREENSHOTS_DIR = STORAGE_PATH / "instagram_screenshots"

DEFAULT_VIEWPORT = {"width": 1280, "height": 1024}
NAVIGATION_TIMEOUT_MS = 30_000


def _normalize(handle: str) -> str:
    h = handle.strip().lstrip("@")
    return re.sub(r"[^\w.\-]", "", h).lower()


async def _dismiss_instagram_modals(page) -> None:
    """Fecha modais leves de signup/login que aparecem sobre perfis publicos."""
    try:
        clicked = await page.evaluate(
            """
            () => {
                const closeIcon = document.querySelector("[aria-label='Fechar'], [aria-label='Close']");
                const target = closeIcon && (closeIcon.closest('button') || closeIcon);
                if (!target) return false;
                target.click();
                return true;
            }
            """
        )
        if clicked:
            await page.wait_for_timeout(500)
            return
    except Exception:
        pass

    try:
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(300)
    except Exception:
        pass

    candidates = [
        page.locator("[aria-label='Fechar'], [aria-label='Close']").first,
        page.get_by_role("button", name=re.compile(r"^(Fechar|Close)$", re.I)),
        page.get_by_role("button", name=re.compile(r"(Agora não|Not Now)", re.I)),
        page.locator("div[role='dialog'] button").first,
    ]

    for _ in range(2):
        dismissed = False
        for locator in candidates:
            try:
                if await locator.first.is_visible(timeout=1500):
                    await locator.first.click(timeout=3000)
                    dismissed = True
                    await page.wait_for_timeout(500)
                    break
            except Exception:
                continue
        if not dismissed:
            return


async def capture_profile_screenshots(
    handle: str,
    count: int = 9,
    headless: bool = True,
) -> Dict[str, Any]:
    """Captura: 1 screenshot do grid do perfil + opcional N posts individuais.

    Args:
        handle: @ do perfil Instagram (publico).
        count: numero de posts individuais a capturar (default 9).
        headless: rodar sem janela (default True; False util pra debug local).

    Returns:
        dict com paths salvos. Levanta RuntimeError se Playwright indisponivel
        ou perfil privado.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as e:
        raise RuntimeError(
            "playwright nao instalado. Rode: pip install playwright && "
            "playwright install chromium"
        ) from e

    handle_clean = _normalize(handle)
    if not handle_clean:
        raise ValueError(f"handle invalido: {handle!r}")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = SCREENSHOTS_DIR / handle_clean / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    profile_url = f"https://www.instagram.com/{handle_clean}/"
    grid_path = out_dir / "grid.png"
    post_paths: List[str] = []

    async with async_playwright() as p:
        # Persistent context = browser + cookies + localStorage entre execucoes.
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            channel=PLAYWRIGHT_CHANNEL,
            viewport=DEFAULT_VIEWPORT,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
        )
        try:
            page = await context.new_page()
            await page.goto(profile_url, wait_until="domcontentloaded",
                            timeout=NAVIGATION_TIMEOUT_MS)

            # Detecta tela de login -> precisa autenticar manualmente
            try:
                login_marker = await page.locator(
                    "input[name='username'], input[name='emailOrPhone']"
                ).first.is_visible(timeout=3000)
                if login_marker:
                    raise RuntimeError(
                        "Instagram pede login. Rode 1x com headless=False "
                        "via container exposto (ou docker exec -it) para "
                        "logar, depois sessao fica persistida em /app/storage/.playwright_profile/"
                    )
            except Exception:
                pass  # ok — tela de perfil

            # O Instagram costuma exibir o modal de signup alguns segundos apos
            # carregar o perfil publico. Aguarde brevemente antes de tentar
            # fechar, senao o screenshot fica escurecido pelo overlay.
            await page.wait_for_timeout(3000)
            await _dismiss_instagram_modals(page)

            # Detecta perfil privado / nao encontrado
            try:
                is_private = await page.locator(
                    "text=This Account is Private"
                ).first.is_visible(timeout=2000)
                if is_private:
                    raise RuntimeError(f"@{handle_clean} eh privado")
            except RuntimeError:
                raise
            except Exception:
                pass

            # Aguarda a primeira linha do grid carregar
            try:
                await page.wait_for_selector("main a[href*='/p/'], main a[href*='/reel/']", timeout=15_000)
            except Exception:
                logger.warning(f"Grid nao carregou em tempo para @{handle_clean}, prosseguindo")
            await _dismiss_instagram_modals(page)

            # Screenshot do perfil inteiro (header + grid)
            await page.screenshot(path=str(grid_path), full_page=False)
            logger.info(f"[insta_playwright] grid salvo: {grid_path}")

            # Captura primeiros N posts individuais
            try:
                post_links = await page.locator(
                    "main a[href*='/p/'], main a[href*='/reel/']"
                ).evaluate_all("els => els.slice(0, " + str(count) + ").map(e => e.href)")
            except Exception as e:
                logger.warning(f"Falha listando posts: {e}")
                post_links = []

            for i, url in enumerate(post_links, 1):
                try:
                    pop = await context.new_page()
                    await pop.goto(url, wait_until="domcontentloaded",
                                   timeout=NAVIGATION_TIMEOUT_MS)
                    await pop.wait_for_timeout(2000)
                    await _dismiss_instagram_modals(pop)
                    # Aguarda a imagem do post aparecer
                    try:
                        await pop.wait_for_selector(
                            "article img[srcset], article video",
                            timeout=8000,
                        )
                    except Exception:
                        pass
                    target = out_dir / f"post_{i:02d}.png"
                    await pop.screenshot(path=str(target), full_page=False)
                    post_paths.append(str(target))
                    await pop.close()
                except Exception as e:
                    logger.warning(f"Post {i} falhou ({url}): {e}")
                    continue
        finally:
            await context.close()

    return {
        "profile": f"@{handle_clean}",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "grid_path": str(grid_path),
        "post_paths": post_paths,
        "post_count": len(post_paths),
        "out_dir": str(out_dir),
    }


def capture_profile_screenshots_sync(
    handle: str,
    count: int = 9,
    headless: bool = True,
) -> Dict[str, Any]:
    """Wrapper sincrono pra uso em contextos non-async (Celery, scripts)."""
    return asyncio.run(capture_profile_screenshots(handle, count=count, headless=headless))
