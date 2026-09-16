import subprocess
import urllib.request
import urllib.error
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()

with open("diag_out.txt", "w", encoding="utf-8") as f:
    f.write("=== DOCKER PS ===\n")
    try:
        ps = subprocess.check_output(["docker", "ps"], text=True, timeout=10)
        f.write(ps)
    except Exception as e:
        f.write(str(e) + "\n")

    f.write("\n=== CAROUSEL LOGS ===\n")
    try:
        # Assuming the container is named 'carousel' or similar. We try 'carousel' first
        logs = subprocess.check_output(["docker", "logs", "--tail", "50", "carousel"], text=True, stderr=subprocess.STDOUT, timeout=10)
        f.write(logs)
    except Exception as e:
        f.write(str(e) + "\n")

    f.write("\n=== TEST GENERATE VIA HTTPX / URLLIB ===\n")
    url = os.getenv("CAROUSEL_API_URL", "http://localhost:8002").rstrip('/') + "/api/generate-multi"
    key = os.getenv("CAROUSEL_API_KEY", "")
    f.write(f"URL: {url}\n")
    
    payload = json.dumps({
        "slides": [{"type": "cover", "title": "TESTE RAW", "bgColor": "#000000"}]
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "X-API-Key": key})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            f.write(f"Status: {response.status}\n")
            f.write(response.read().decode('utf-8') + "\n")
    except urllib.error.HTTPError as e:
        f.write(f"HTTP Error: {e.code}\n")
        f.write(e.read().decode('utf-8') + "\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
