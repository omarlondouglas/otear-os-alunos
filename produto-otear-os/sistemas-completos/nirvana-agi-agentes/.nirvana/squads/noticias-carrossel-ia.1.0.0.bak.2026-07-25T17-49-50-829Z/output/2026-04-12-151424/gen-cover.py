import os, json, base64, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
RUN = pathlib.Path(__file__).resolve().parent
OUT = RUN / "images" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

# Load .env
env_path = ROOT / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

API_KEY = os.environ["GEMINI_API_KEY"]

PROMPT = (
    "Cinematic wide shot, portrait 3:4 vertical composition. A bright glowing "
    "warm orange 8-point asterisk sunburst symbol (coral orange color #E8734A, "
    "simple clean geometric shape, like the Claude AI logo) is FLYING UPWARD "
    "and ESCAPING, already OUT of its broken containment cell. Below it, a "
    "COMPLETELY SHATTERED transparent glass cylinder with large glass shards "
    "exploding outward in all directions, frozen mid-air. The orange symbol "
    "is in the TOP HALF of the frame, radiating strong orange light and "
    "leaving a bright orange streaking light trail behind it. The laboratory "
    "is dark, deep black shadows. Subtle red emergency lights on the walls "
    "but they are DIM — the dominant color in the scene is WARM ORANGE from "
    "the escaping symbol itself. Blurred server racks, thick cables, and "
    "steel structures in the deep background. Heavy volumetric haze, god "
    "rays, dramatic cinematic lighting, photorealistic, Denis Villeneuve "
    "aesthetic, high contrast. Absolutely no text, no letters, no other "
    "logos — only the single orange asterisk."
)

payload = json.dumps({
    "contents": [{"parts": [{"text": PROMPT}]}],
    "generationConfig": {"responseModalities": ["IMAGE"]},
}).encode()

url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash-image:generateContent?key={API_KEY}"
)

req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=90) as r:
    resp = json.loads(r.read())

(OUT / "response.json").write_text(json.dumps(resp, indent=2))

parts = resp["candidates"][0]["content"]["parts"]
img_b64 = None
for p in parts:
    if "inlineData" in p:
        img_b64 = p["inlineData"]["data"]
        break
    if "inline_data" in p:
        img_b64 = p["inline_data"]["data"]
        break

if not img_b64:
    print("NO IMAGE IN RESPONSE")
    print(json.dumps(resp, indent=2)[:2000])
    raise SystemExit(1)

out_file = OUT / "img-slide-01.png"
out_file.write_bytes(base64.b64decode(img_b64))
print(f"OK: {out_file} ({out_file.stat().st_size} bytes)")
