"""
DIAGNÓSTICO: Simula EXATAMENTE como o agno_tools.py chama o carousel.

Este script carrega as variáveis de ambiente da MESMA FORMA que o agente faz,
e então chama a função generate_carousel_tool() diretamente para identificar
em qual ponto a falha ocorre.
"""
import os
import sys
from dotenv import load_dotenv

# === PASSO 1: VERIFICAR VARIÁVEIS ANTES DO DOTENV ===
print("=" * 60)
print("PASSO 1: Variáveis de ambiente ANTES de load_dotenv()")
print("=" * 60)
print(f"  CAROUSEL_API_URL (antes)   : {os.getenv('CAROUSEL_API_URL', '❌ NÃO DEFINIDA')}")
print(f"  CAROUSEL_API_KEY (antes)   : {os.getenv('CAROUSEL_API_KEY', '❌ NÃO DEFINIDA')}")

# === PASSO 2: CARREGAR .ENV COMO O AGENTE FAZ ===
load_dotenv()

print("\n" + "=" * 60)
print("PASSO 2: Variáveis de ambiente DEPOIS de load_dotenv()")
print("=" * 60)
carousel_url = os.getenv("CAROUSEL_API_URL")
carousel_key = os.getenv("CAROUSEL_API_KEY")
print(f"  CAROUSEL_API_URL (depois)  : {carousel_url or '❌ NÃO DEFINIDA'}")
print(f"  CAROUSEL_API_KEY (depois)  : {'✅ Definida' if carousel_key else '❌ NÃO DEFINIDA'}")

# === PASSO 3: SIMULAR A INICIALIZAÇÃO DO MÓDULO agno_tools.py ===
print("\n" + "=" * 60)
print("PASSO 3: Simulando resolução de variáveis igual ao agno_tools.py (linha 13)")
print("=" * 60)
CAROUSEL_SERVICE_URL = os.getenv("CAROUSEL_API_URL", os.getenv("CAROUSEL_SERVICE_URL", "http://localhost:8002"))
CAROUSEL_API_KEY = os.getenv("CAROUSEL_API_KEY")
print(f"  CAROUSEL_SERVICE_URL resolvido : {CAROUSEL_SERVICE_URL}")
print(f"  CAROUSEL_API_KEY resolvido     : {'✅ Definida' if CAROUSEL_API_KEY else '❌ NÃO DEFINIDA'}")

if "localhost" in CAROUSEL_SERVICE_URL:
    print("\n  ⚠️  PROBLEMA DETECTADO: A URL está apontando para localhost!")
    print("     Isso significa que o agente não está conseguindo ler o .env corretamente.")
    print("     Dentro do Docker, localhost:8002 não existe e a conexão falha.")
else:
    print("\n  ✅ URL parece correta (não é localhost).")

# === PASSO 4: CHAMAR A FERRAMENTA DIRETAMENTE ===
print("\n" + "=" * 60)
print("PASSO 4: Chamando generate_carousel_tool() diretamente")
print("=" * 60)

try:
    from app.agents.agno_tools import generate_carousel_tool, CAROUSEL_SERVICE_URL as URL_DO_MODULO
    
    print(f"\n  ⚠️ URL lida pelo MÓDULO após importação: {URL_DO_MODULO}")
    if "localhost" in URL_DO_MODULO:
        print("  🔴 BUG CONFIRMADO: O módulo foi importado ANTES do .env ser carregado!")
        print("     O agno_tools.py lê CAROUSEL_API_URL na linha 13 (em tempo de importação),")
        print("     mas o load_dotenv() pode estar sendo chamado DEPOIS da importação do módulo.")
        print("     Solução: Garantir que load_dotenv() seja chamado antes de importar agno_tools.")
        sys.exit(1)
    
    print("\n  Executando generate_carousel_tool com slides de teste...")
    slides = [
        {"type": "cover", "title": "TESTE DIAGNÓSTICO", "subtitle": "Chamado via agno_tools", "bgColor": "#000000", "titleColor": "#A3F12E"},
        {"type": "text-only", "title": "Slide 2 - Verificando agente", "bgColor": "#1a1a1a", "titleColor": "#ffffff"},
    ]
    
    result = generate_carousel_tool(slides)
    
    print(f"\n  Resultado da ferramenta:")
    if result.get("success"):
        print(f"  ✅ SUCESSO! Carrossel gerado com {len(result.get('slides', []))} slides.")
        for s in result.get("slides", []):
            print(f"     Slide {s.get('order')}: {s.get('url')}")
    else:
        print(f"  ❌ ERRO: {result.get('error')}")
        print(f"  Detalhes: {result}")

except ImportError as e:
    print(f"\n  ❌ ERRO DE IMPORTAÇÃO: {e}")
    print("     Verifique se todas as dependências estão instaladas (agno, redis, etc).")
except Exception as e:
    print(f"\n  ❌ EXCEÇÃO: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIM DO DIAGNÓSTICO")
print("=" * 60)
