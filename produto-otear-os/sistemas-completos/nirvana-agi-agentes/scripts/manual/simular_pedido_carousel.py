import os
import httpx
import json
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# CONFIGURAÇÃO DA API
# Ajuste estas URLs se necessário ou defina-as no seu arquivo .env
CAROUSEL_API_URL = os.getenv("CAROUSEL_API_URL", "https://otear-carrocel-backend.qc7qit.easypanel.host")
CAROUSEL_API_KEY = os.getenv("CAROUSEL_API_KEY", os.getenv("CAROUSEL_API_KEY", "test-key"))

def simular_criacao_carousel():
    """
    Simula um pedido completo de criação de carrossel.
    """
    print("🚀 INICIANDO SIMULAÇÃO DE PEDIDO DE CARROSSEL")
    print("-" * 50)
    print(f"URL da API: {CAROUSEL_API_URL}")
    print(f"API Key: {'Configurada' if CAROUSEL_API_KEY else 'NÃO ENCONTRADA'}")
    print("-" * 50)

    # 1. Definir os slides (Payload)
    # Aqui simulamos o que um agente de IA ou usuário enviaria para a API
    slides_payload = [
        {
            "type": "cover",
            "title": "COMO CRIAR CARROSSEIS",
            "subtitle": "Guia Prático com Python & IA",
            "titleColor": "#A3F12E",
            "bgColor": "#0a0a0a",
            "fontFamily": "montserrat",
            "images": {
                "bg": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=1080"
            }
        },
        {
            "type": "text-only",
            "title": "Passo 1: Defina seu conteúdo estratégico",
            "highlight": "estratégico",
            "highlightColor": "#FFD700",
            "bgColor": "#1a1a1a",
            "fontFamily": "montserrat",
            "titleColor": "#ffffff"
        },
        {
            "type": "text-only",
            "title": "Passo 2: Use ferramentas de geração automatizada",
            "highlight": "geração automatizada",
            "highlightColor": "#A3F12E",
            "bgColor": "#0a0a0a",
            "fontFamily": "montserrat",
            "titleColor": "#ffffff"
        },
        {
            "type": "text-only",
            "title": "Gostaria de automatizar seu conteúdo também?",
            "subtitle": "Me pergunte como agora!",
            "bgColor": "#FFD700",
            "titleColor": "#000000",
            "fontFamily": "montserrat"
        }
    ]

    # Preparar headers
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": CAROUSEL_API_KEY
    }

    # 2. Enviar a requisição
    print("\n⏳ Enviando API Request (POST /api/generate-multi)...")
    start_time = time.time()
    
    try:
        # Usamos um timeout longo porque a geração de imagens/design pode demorar
        response = httpx.post(
            f"{CAROUSEL_API_URL}/api/generate-multi",
            json={"slides": slides_payload},
            headers=headers,
            timeout=180.0
        )
        
        duration = time.time() - start_time
        print(f"✅ Resposta recebida em {duration:.2f} segundos.")
        print(f"Status HTTP: {response.status_code}")

        # 3. Processar resultado
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("\n✨ CARROSSEL GERADO COM SUCESSO! ✨")
                print(f"ID do Carrossel: {result.get('carouselId')}")
                print(f"Total de Slides: {result.get('totalSlides')}")
                
                print("\n🔗 LINKS DOS SLIDES GERADOS:")
                for slide in result.get("slides", []):
                    order = slide.get("order")
                    url = slide.get("url")
                    print(f"   Slide {order}: {url}")
                
                print("\n💡 Dica: Você pode abrir as URLs acima no seu navegador para ver o resultado.")
            else:
                print(f"\n❌ ERRO NA GERAÇÃO: {result.get('error')}")
        else:
            print(f"\n❌ ERRO NA REQUISIÇÃO: {response.status_code}")
            print(f"Detalhes: {response.text}")

    except Exception as e:
        print(f"\n❌ EXCEÇÃO DISPARADA: {str(e)}")

if __name__ == "__main__":
    simular_criacao_carousel()
