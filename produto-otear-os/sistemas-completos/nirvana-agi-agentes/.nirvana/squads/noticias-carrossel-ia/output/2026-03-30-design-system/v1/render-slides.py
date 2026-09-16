import json, os

TEMPLATE_PATH = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-design-system/v1/slide-template-16x9.html"
SLIDES_PATH = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-design-system/v1/slides-data.json"
OUTPUT_DIR = "d:/opensquad/squads/noticias-carrossel-ia/output/2026-03-30-design-system/v1/html"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

with open(SLIDES_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data["slides"])

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
        text = el["text"].replace("\n", "<br>")
        return f'<p class="body-text">{text}</p>'
    elif t == "list":
        items = "".join(f"<li>{item}</li>" for item in el["items"])
        return f'<ul class="list">{items}</ul>'
    elif t == "code":
        return f'<div class="code-block">{el["text"]}</div>'
    elif t == "spacer":
        return '<div class="spacer"></div>'
    elif t == "columns":
        left_html = render_element(el["left"])
        right_html = render_element(el["right"])
        return f'<div class="columns"><div class="col">{left_html}</div><div class="col">{right_html}</div></div>'
    return ""

for slide in data["slides"]:
    theme = f"theme-{slide['theme']}"
    body_html = "\n    ".join(render_element(el) for el in slide["elements"])

    html = template.replace("{{THEME}}", theme)
    html = html.replace("{{BODY_HTML}}", body_html)
    html = html.replace("{{SLIDE_NUM}}", f"{slide['id']}/{total}")

    out_path = os.path.join(OUTPUT_DIR, f"slide-{slide['id']:02d}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: slide-{slide['id']:02d}.html")

print(f"\nAll {total} slides generated")
