"""
DIAGNÓSTICO SIMPLES: Testa a chamada ao carrossel SEM depender de agno/redis/postgres.
Simula exatamente o que generate_carousel_tool() faz no agno_tools.py.
"""
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

# Replicando EXATAMENTE as linhas 13-15 do agno_tools.py
CAROUSEL_SERVICE_URL = os.getenv("CAROUSEL_API_URL", os.getenv("CAROUSEL_SERVICE_URL", "http://localhost:8002"))
CAROUSEL_API_KEY = os.getenv("CAROUSEL_API_KEY")

print("=" * 60)
print("DIAGNÓSTICO SIMPLES - sem agno/redis/postgres")
print("=" * 60)
print(f"\n📍 CAROUSEL_SERVICE_URL = {CAROUSEL_SERVICE_URL}")
print(f"🔑 CAROUSEL_API_KEY    = {'✅ Definida' if CAROUSEL_API_KEY else '❌ NÃO DEFINIDA'}")

if "localhost" in CAROUSEL_SERVICE_URL:
    print("\n🔴 PROBLEMA: URL aponta para localhost! Em produção isso deve ser a URL externa.")

# Testar health primeiro (rápido)
print(f"\n1️⃣  Testando health: {CAROUSEL_SERVICE_URL}/api/health")
try:
    r = httpx.get(f"{CAROUSEL_SERVICE_URL}/api/health", timeout=10.0)
    print(f"   Status: {r.status_code} | Body: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ FALHOU: {e}")
    print("   → Isso significa que o agente também vai falhar com ConnectError!")

# Simular chamada generate-multi (igual ao generate_carousel_tool)
print(f"\n2️⃣  Testando geração de carrossel: {CAROUSEL_SERVICE_URL}/api/generate-multi")

slides = [
    {"type": "cover", "title": "TESTE", "bgColor": "#000000", "titleColor": "#ffffff"},
    {"type": "text-only", "title": "Slide 2", "bgColor": "#111111", "titleColor": "#ffffff"},
]

headers = {"Content-Type": "application/json"}
if CAROUSEL_API_KEY:
    headers["X-API-Key"] = CAROUSEL_API_KEY
    print(f"   Header 'X-API-Key' adicionado: {CAROUSEL_API_KEY[:8]}...")

print("   ⏳ Aguardando resposta (pode levar ~60s)...")

try:
    r = httpx.post(
        f"{CAROUSEL_SERVICE_URL}/api/generate-multi",
        json={"slides": slides},
        headers=headers,
        timeout=120.0
    )
    print(f"   Status: {r.status_code}")
    result = r.json()
    
    if result.get("success"):
        print(f"   ✅ SUCESSO! Gerados {result.get('totalSlides')} slides.")
        for s in result.get("slides", []):
            print(f"      Slide {s.get('order')}: {s.get('url', 'sem URL')}")
    else:
        print(f"   ❌ ERRO NA API: {result.get('error')}")
        print(f"   Resposta completa: {json.dumps(result, indent=2)}")
        
except httpx.ConnectError as e:
    print(f"   ❌ ConnectError: {e}")
    print("   → Causa provável: CAROUSEL_API_URL não está definida corretamente.")
    print("   → No EasyPanel, verifique se CAROUSEL_API_URL está configurada.")
except httpx.HTTPStatusError as e:
    print(f"   ❌ HTTPError {e.response.status_code}: {e.response.text}")
    print("   → Pode ser erro de auth (CAROUSEL_API_KEY incorreta ou ausente)")
except httpx.ReadTimeout:
    print(f"   ❌ Timeout (120s excedido)")
except Exception as e:
    print(f"   ❌ Exceção: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
