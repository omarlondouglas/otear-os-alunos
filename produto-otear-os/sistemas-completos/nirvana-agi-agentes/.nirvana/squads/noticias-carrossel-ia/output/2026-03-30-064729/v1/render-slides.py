import json, os

TEMPLATE_PATH = "d:/opensquad/squads/noticias-carrossel-ia/pipeline/slide-template.html"
SLIDES_PATH = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-064729/v1/slides-data.json"
OUTPUT_DIR = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-064729/v1/html"
IMAGES_DIR = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-064729/v1/images"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

with open(SLIDES_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def render_element(el):
    t = el["type"]
    if t == "tag":
        return f'<div class="tag">{el["text"]}</div>'
    elif t == "stat":
        return f'<div class="stat">{el["text"]}</div>'
    elif t == "headline":
        return f'<h1 class="headline">{el["text"]}</h1>'
    elif t == "sub":
        return f'<p class="sub">{el["text"]}</p>'
    elif t == "body":
        return f'<p class="body-text">{el["text"]}</p>'
    elif t == "list":
        items = "".join(f"<li>{item}</li>" for item in el["items"])
        return f'<ul class="list">{items}</ul>'
    elif t == "cta":
        return f'<div class="cta-box">{el["text"]}</div>'
    elif t == "swipe":
        return '<div class="swipe">arraste</div>'
    elif t == "spacer":
        return '<div class="spacer"></div>'
    return ""

for slide in data["slides"]:
    theme = f"theme-{slide['theme']}"
    img_file = slide.get("imageFile")

    # Build body HTML
    body_html = "\n    ".join(render_element(el) for el in slide["elements"])

    # Image layer
    if img_file:
        img_layer = f'<div class="img-layer" style="background-image: url(\'../images/{img_file}\');"></div>'
        img_class = ""
    else:
        img_layer = ""
        img_class = ""

    html = template.replace("{{THEME}}", theme)
    html = html.replace("{{IMG_CLASS}}", img_class)
    html = html.replace("{{IMG_LAYER}}", img_layer)
    html = html.replace("{{BODY_HTML}}", body_html)

    out_path = os.path.join(OUTPUT_DIR, f"slide-{slide['id']:02d}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: slide-{slide['id']:02d}.html")

print(f"\nAll {len(data['slides'])} slides generated in {OUTPUT_DIR}")
