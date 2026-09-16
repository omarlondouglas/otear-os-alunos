"""Carousel diagnostic - ASCII only for Windows"""
import httpx
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.getenv("PUBLIC_API_URL", "https://otear-agentes-otear.qc7qit.easypanel.host")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
CAROUSEL_SERVICE_URL = os.getenv("CAROUSEL_API_URL") or os.getenv("CAROUSEL_SERVICE_URL", "")

print("=" * 60)
print("CAROUSEL DIAGNOSTIC")
print("=" * 60)
print("Backend: " + BACKEND_URL)
print("Carousel: " + (CAROUSEL_SERVICE_URL or "(not set)"))

headers = {"x-admin-password": ADMIN_PASSWORD, "Content-Type": "application/json"}

# TEST 1
print("\n--- TEST 1: Backend Health ---")
try:
    s = time.time()
    r = httpx.get(BACKEND_URL + "/api/health", headers=headers, timeout=10.0)
    print("OK status=%d time=%.2fs resp=%s" % (r.status_code, time.time()-s, r.text[:200]))
except Exception as e:
    print("FAIL: %s" % e)

# TEST 2
print("\n--- TEST 2: Carousel Health (direct) ---")
if CAROUSEL_SERVICE_URL:
    try:
        s = time.time()
        r = httpx.get(CAROUSEL_SERVICE_URL + "/api/health", timeout=15.0)
        print("OK status=%d time=%.2fs resp=%s" % (r.status_code, time.time()-s, r.text[:200]))
    except Exception as e:
        print("FAIL: %s" % e)
else:
    print("Skipped")

# TEST 3
print("\n--- TEST 3: Direct Carousel Generation ---")
payload = {"slides": [
    {"type": "cover", "title": "TESTE", "subtitle": "Verificando", "bgColor": "#0a0a0a", "titleColor": "#A3F12E"},
    {"type": "text-only", "title": "Slide de teste operacional", "bgColor": "#1a1a1a", "titleColor": "#ffffff"}
]}
url3 = (CAROUSEL_SERVICE_URL or BACKEND_URL) + "/api/generate-multi"
print("  Calling: " + url3)
try:
    s = time.time()
    r = httpx.post(url3, json=payload, headers={"Content-Type": "application/json"}, timeout=120.0)
    el = time.time()-s
    result = r.json()
    print("OK status=%d time=%.2fs success=%s" % (r.status_code, el, result.get("success")))
    if result.get("slides"):
        for sl in result["slides"]:
            print("  Slide %s: %s" % (sl.get("order"), sl.get("url", "NO URL")))
    elif result.get("error"):
        print("  Error: %s" % result.get("error"))
    else:
        print("  Response: %s" % json.dumps(result)[:500])
except httpx.ReadTimeout:
    print("FAIL: TIMEOUT after %.2fs" % (time.time()-s))
except Exception as e:
    print("FAIL: %s: %s" % (type(e).__name__, e))

# TEST 4
print("\n--- TEST 4: Agent Pipeline via /api/chat ---")
print("  Sending carousel request through agent pipeline...")
print("  This may take 2-5 minutes. Set 600s timeout...")
chat = {"message": "Crie um carrossel simples com 2 slides sobre produtividade. Use text-only.", "context": {}}
try:
    s = time.time()
    r = httpx.post(BACKEND_URL + "/api/chat", json=chat, headers=headers, timeout=600.0)
    el = time.time()-s
    result = r.json()
    resp = result.get("response", "")
    print("OK status=%d time=%.2fs len=%d" % (r.status_code, el, len(resp)))
    print("  Has URLs: %s" % ("http" in resp))
    print("  Has error: %s" % ("erro" in resp.lower() or "error" in resp.lower()))
    print("\n  === RESPONSE ===")
    print("  " + resp[:2000])
except httpx.ReadTimeout:
    print("FAIL: TIMEOUT after %.2fs" % (time.time()-s))
except httpx.RemoteProtocolError as e:
    print("FAIL: CONNECTION CUT after %.2fs: %s" % (time.time()-s, e))
except Exception as e:
    print("FAIL: %s: %s" % (type(e).__name__, e))

print("\n" + "=" * 60)
print("DONE")
