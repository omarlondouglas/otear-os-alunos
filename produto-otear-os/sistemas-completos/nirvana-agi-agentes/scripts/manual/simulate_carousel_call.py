import os
import json
import requests
import sys
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path para importar as ferramentas
sys.path.append(os.getcwd())

from app.agents.agno_tools import generate_carousel_tool

def test_carousel_direct():
    load_dotenv()
    
    print("--- Teste de Chamada do Agente Carrossel ---")
    print(f"URL: {os.getenv('CAROUSEL_API_URL')}")
    print(f"Key: {'***' if os.getenv('CAROUSEL_API_KEY') else 'NÃO DEFINIDA'}")

    # Simulação de slides que o agente criaria
    slides_data = [
        {
            "type": "cover", 
            "title": "TESTE DE COMUNICAÇÃO AGENTE", 
            "subtitle": "Testando se o backend do carrossel responde", 
            "bgColor": "#0a0a0a", 
            "titleColor": "#A3F12E"
        },
        {
            "type": "text-only", 
            "title": "Este é um teste automático", 
            "bgColor": "#1a1a1a", 
            "titleColor": "#ffffff"
        }
    ]

    print("\nChamando generate_carousel_tool...")
    try:
        result = generate_carousel_tool(slides_data=slides_data)
        print("\n--- RESULTADO ---")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\n✅ SUCESSO! O agente conseguiu falar com o serviço.")
        else:
            print(f"\n❌ FALHA: {result.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"\n💥 EXCEÇÃO CRÍTICA: {e}")

if __name__ == "__main__":
    test_carousel_direct()
