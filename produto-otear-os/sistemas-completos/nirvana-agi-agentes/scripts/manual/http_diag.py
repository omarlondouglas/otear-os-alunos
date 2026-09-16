import urllib.request
import urllib.error
import json
import os
from dotenv import load_dotenv

load_dotenv()

with open("http_diag.txt", "w", encoding="utf-8") as f:
    f.write("=== TEST GENERATE VIA HTTPX / URLLIB ===\n")
    url = os.getenv("CAROUSEL_API_URL", "http://localhost:8002").rstrip('/') + "/api/generate-multi"
    key = os.getenv("CAROUSEL_API_KEY", "")
    f.write(f"URL: {url}\n")
    f.flush()
    
    payload = json.dumps({
        "slides": [{"type": "cover", "title": "TESTE RAW", "bgColor": "#000000"}]
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "X-API-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            f.write(f"Status: {response.status}\n")
            f.write(response.read().decode('utf-8') + "\n")
    except urllib.error.HTTPError as e:
        f.write(f"HTTP Error: {e.code}\n")
        f.write(e.read().decode('utf-8') + "\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
