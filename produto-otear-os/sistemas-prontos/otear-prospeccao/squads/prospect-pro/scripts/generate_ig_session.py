import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import yaml
import os

CONFIG_PATH = Path(__file__).parent.parent / "config" / "scraper_config.yaml"

def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["scraper"]

async def main():
    config = load_config()
    print("Iniciando navegador para geracao de cookies do Instagram...")
    print("O navegador abrira no modo visivel (headless: False).")
    print("Por favor, faca o login manualmente e resolva qualquer desafio/2FA.")
    
    pw = await async_playwright().start()
    # Forcar headless: False para o usuario interagir
    browser = await pw.chromium.launch(headless=False)
    
    context = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="pt-BR"
    )
    
    page = await context.new_page()
    await page.goto("https://www.instagram.com/accounts/login/")
    
    # Aguardar ate o usuario confirmar no terminal
    print("\n" + "="*60)
    print("INSTRUCOES:")
    print("1. Na janela do navegador que se abriu, insira seus dados de login.")
    print("2. Caso o Instagram envie um codigo de verificacao (2FA), insira-o.")
    print("3. Quando estiver na pagina inicial (Feed) do Instagram, volte aqui no terminal.")
    print("4. Pressione ENTER neste terminal para salvar a sessao e fechar o navegador.")
    print("="*60 + "\n")
    
    # Input sincrono em thread para nao bloquear o loop de eventos
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, input, "Pressione [ENTER] quando o login estiver concluido para salvar os cookies... ")
    
    # Salvar cookies de sessao
    session_path = Path(__file__).parent.parent / "data" / "instagram_session.json"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(session_path))
    print(f"\n[OK] Sessao do Instagram salva com sucesso em: {session_path}")
    
    await browser.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(main())
