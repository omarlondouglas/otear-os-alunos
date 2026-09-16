import os
import httpx
import json
import time
import sys
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÃO
# Pega a URL do arquivo .env ou usa o valor padrão se não encontrar
BASE_URL = os.getenv("CAROUSEL_API_URL", "http://localhost:8002")
API_KEY = os.getenv("CAROUSEL_API_KEY")

def test_carousel_gen():
    print(f"--- INICIANDO TESTE DE CARROSSEL ---")
    print(f"Alvo: {BASE_URL}")
    print(f"API Key: {API_KEY[:4]}***" if API_KEY else "SEM API KEY")
    
    # 1. CRIAR PEDIDO
    print("\n1. Enviando solicitação de carrossel (SÍNCRONO)...")
    print("⏳ Aguardando geração (pode levar até 60 segundos)...")
    
    slides_payload = [
        {"type": "cover", "title": "TESTE CARROSSEL", "subtitle": "Verificando API", "titleColor": "#ffffff", "bgColor": "#000000"},
        {"type": "text-only", "title": "Slide 2", "bgColor": "#333333"},
        {"type": "text-only", "title": "Slide 3", "bgColor": "#666666"}
    ]
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    try:
        start_t = time.time()
        # Timeout de 5 minutos para garantir
        response = httpx.post(
            f"{BASE_URL}/api/generate-multi",
            json={"slides": slides_payload},
            headers=headers,
            timeout=300.0 
        )
        duration = time.time() - start_t
        
        print(f"\n✅ Resposta recebida em {duration:.2f}s")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n✅ CARROSSEL GERADO COM SUCESSO!")
                print(f"ID: {data.get('carouselId')}")
                print(f"Slides: {len(data.get('slides', []))}")
                for slide in data.get('slides', []):
                    print(f"  - Slide {slide['order']}: {slide['url']}")
            else:
                print(f"\n❌ ERRO NA GERAÇÃO: {data.get('error')}")
        else:
             print(f"\n❌ ERRO HTTP: {response.status_code}")
             print(response.text)

    except Exception as e:
        print(f"\n❌ EXCEÇÃO AO CONECTAR: {e}")

if __name__ == "__main__":
    test_carousel_gen()
