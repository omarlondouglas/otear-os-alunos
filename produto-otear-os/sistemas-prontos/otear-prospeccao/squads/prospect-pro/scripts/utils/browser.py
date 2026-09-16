import asyncio
import os
import random
import yaml
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Carregar .env se existir
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "scraper_config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["scraper"]


def random_user_agent(config: dict) -> str:
    return random.choice(config["user_agents"])


async def random_delay(min_s: float, max_s: float):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def action_delay(config: dict):
    delays = config["delays"]
    await random_delay(delays["between_actions_min"], delays["between_actions_max"])


async def page_delay(config: dict):
    delays = config["delays"]
    await random_delay(delays["between_pages_min"], delays["between_pages_max"])


async def human_scroll(page: Page, config: dict, scrolls: int = 3):
    delays = config["delays"]
    for _ in range(scrolls):
        distance = random.randint(300, 700)
        await page.mouse.wheel(0, distance)
        await random_delay(delays["scroll_delay_min"], delays["scroll_delay_max"])


def parse_netscape_cookies(file_path: str) -> list[dict]:
    cookies = []
    if not os.path.exists(file_path):
        return cookies
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 7:
                    domain = parts[0]
                    # flag = parts[1] (not needed by playwright)
                    path = parts[2]
                    secure = parts[3].upper() == "TRUE"
                    expires = int(parts[4])
                    name = parts[5]
                    value = parts[6]
                    
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": domain,
                        "path": path,
                        "secure": secure,
                        "expires": expires
                    })
    except Exception as e:
        print(f"  [WARN] Erro ao ler cookies Netscape ({file_path}): {e}")
    return cookies


async def create_browser(config: dict) -> tuple[Browser, BrowserContext]:
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=config["browser"]["headless"],
    )
    
    instagram_session_path = Path(__file__).parent.parent.parent / "data" / "instagram_session.json"
    
    context_args = {
        "viewport": {
            "width": config["browser"]["viewport"]["width"],
            "height": config["browser"]["viewport"]["height"],
        },
        "user_agent": random_user_agent(config),
        "locale": config["browser"]["locale"],
        "timezone_id": config["browser"]["timezone"],
    }
    
    # Se existir sessao do Instagram em JSON (formato Playwright), carregar
    if instagram_session_path.exists():
        context_args["storage_state"] = str(instagram_session_path)
        print(f"  [INFO] Carregando sessao do Instagram via storage_state: {instagram_session_path.name}")
        
    context = await browser.new_context(**context_args)
    
    # Se existirem cookies do Google em formato Netscape, carregar
    google_cookies_path = Path(__file__).parent.parent.parent / "data" / "google_cookies.txt"
    if google_cookies_path.exists():
        cookies = parse_netscape_cookies(str(google_cookies_path))
        if cookies:
            await context.add_cookies(cookies)
            print(f"  [INFO] {len(cookies)} cookies do Google carregados de {google_cookies_path.name}")
            
    # Se existirem cookies do Instagram em formato Netscape, carregar também como fallback
    instagram_cookies_path = Path(__file__).parent.parent.parent / "data" / "instagram_cookies.txt"
    if instagram_cookies_path.exists():
        cookies = parse_netscape_cookies(str(instagram_cookies_path))
        if cookies:
            await context.add_cookies(cookies)
            print(f"  [INFO] {len(cookies)} cookies do Instagram carregados de {instagram_cookies_path.name}")
            
    return browser, context


async def safe_goto(page: Page, url: str, config: dict) -> bool:
    try:
        timeout = config["limits"]["timeout_seconds"] * 1000
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        await action_delay(config)
        return True
    except Exception:
        return False


async def type_like_human(page: Page, selector: str, text: str, config: dict):
    delays = config["delays"]
    await page.click(selector)
    for char in text:
        await page.keyboard.type(char, delay=random.randint(
            delays["typing_delay_min"], delays["typing_delay_max"]
        ))
    await action_delay(config)


async def instagram_login(page: Page, config: dict) -> bool:
    """Faz login no Instagram. Retorna True se logou com sucesso ou ja esta autenticado."""
    ig_config = config.get("instagram", {})
    base_url = ig_config.get("base_url", "https://www.instagram.com")
    
    # 1. Verificar se já está autenticado via cookies/session state
    try:
        if not await safe_goto(page, base_url, config):
            return False
        
        await asyncio.sleep(2)
        if "login" not in page.url.lower():
            print("  [OK] Usuário já autenticado via cookies/sessão.")
            return True
    except Exception:
        pass

    username_env = ig_config.get("username_env", "INSTAGRAM_USERNAME")
    password_env = ig_config.get("password_env", "INSTAGRAM_PASSWORD")

    username = os.environ.get(username_env)
    password = os.environ.get(password_env)

    if not username or not password:
        print(f"  [WARN] Credenciais Instagram nao encontradas ({username_env}/{password_env})")
        return False

    try:
        login_url = f"{base_url}/accounts/login/"
        if not await safe_goto(page, login_url, config):
            return False

        # Aceitar cookies se aparecer
        try:
            cookie_btn = page.locator(
                "button:has-text('Permitir'), "
                "button:has-text('Allow'), "
                "button:has-text('Aceitar')"
            ).first
            if await cookie_btn.count() > 0:
                await cookie_btn.click(timeout=3000)
                await asyncio.sleep(1)
        except Exception:
            pass

        # Aguardar form de login
        await page.wait_for_selector("input[name='username']", timeout=10000)

        # Preencher usuario
        await type_like_human(page, "input[name='username']", username, config)

        # Preencher senha
        await type_like_human(page, "input[name='password']", password, config)

        # Clicar em Login
        await page.click("button[type='submit']")
        await asyncio.sleep(5)

        # Verificar se logou (feed ou desafio de seguranca)
        current_url = page.url
        if "challenge" in current_url or "two_factor" in current_url:
            print("  [WARN] Instagram pede verificacao 2FA - login parcial")
            return False

        # Fechar dialogs "Salvar informacoes de login" / "Ativar notificacoes"
        for _ in range(2):
            try:
                not_now = page.locator(
                    "button:has-text('Agora não'), "
                    "button:has-text('Not Now'), "
                    "button:has-text('Ahora no'), "
                    "div[role='button']:has-text('Agora não')"
                ).first
                if await not_now.count() > 0:
                    await not_now.click(timeout=3000)
                    await asyncio.sleep(2)
            except Exception:
                break

        # Verificar se estamos no feed
        if "login" not in page.url.lower():
            print(f"  [OK] Login Instagram bem-sucedido como @{username}")
            # Salvar cookies/sessão para reutilização futura
            try:
                session_path = Path(__file__).parent.parent.parent / "data" / "instagram_session.json"
                session_path.parent.mkdir(parents=True, exist_ok=True)
                await page.context.storage_state(path=str(session_path))
                print(f"  [OK] Sessao do Instagram salva em: {session_path.name}")
            except Exception as se:
                print(f"  [WARN] Nao foi possivel salvar a sessao: {se}")
            return True
        else:
            print("  [ERRO] Falha no login Instagram")
            return False

    except Exception as e:
        print(f"  [ERRO] Login Instagram falhou: {e}")
        return False
