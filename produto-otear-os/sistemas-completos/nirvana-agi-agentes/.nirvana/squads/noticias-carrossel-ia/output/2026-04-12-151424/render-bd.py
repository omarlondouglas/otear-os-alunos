import json, os, subprocess, pathlib

RUN = pathlib.Path(__file__).resolve().parent
TEMPLATE = RUN / "slide-template-bd.html"
SLIDES = RUN / "slides-data.json"
OUT = RUN / "slides-bd"
OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

template = TEMPLATE.read_text(encoding="utf-8")
data = json.loads(SLIDES.read_text(encoding="utf-8"))


def render_el(el):
    t = el["type"]
    if t == "tag":
        return f'<div class="tag">{el["text"]}</div>'
    if t == "stat":
        return f'<div class="stat">{el["text"]}</div>'
    if t == "headline":
        return f'<h1 class="headline">{el["text"]}</h1>'
    if t == "sub":
        return f'<p class="sub">{el["text"]}</p>'
    if t == "body":
        return f'<p class="body-text">{el["text"]}</p>'
    if t == "list":
        return '<ul class="list">' + "".join(f"<li>{i}</li>" for i in el["items"]) + "</ul>"
    if t == "cta":
        return f'<div class="cta-box">{el["text"]}</div>'
    if t == "swipe":
        return '<div class="swipe">arraste</div>'
    if t == "spacer":
        return '<div class="spacer"></div>'
    return ""


for slide in data["slides"]:
    theme = f"theme-{slide['theme']}"
    body = "\n    ".join(render_el(e) for e in slide["elements"])
    img = slide.get("imageFile")
    if img:
        abs_img = str(RUN / img).replace("\\", "/")
        img_layer = f'<div class="img-layer" style="background-image: url(\'file:///{abs_img}\');"></div>'
    else:
        img_layer = ""
    html = (template
            .replace("{{THEME}}", theme)
            .replace("{{IMG_CLASS}}", "")
            .replace("{{IMG_LAYER}}", img_layer)
            .replace("{{BODY_HTML}}", body))
    html_path = OUT / f"slide-{slide['id']:02d}.html"
    html_path.write_text(html, encoding="utf-8")
    print(f"html: {html_path.name}")

print("\n--- Screenshots ---")
ok = 0
for slide in data["slides"]:
    html_path = OUT / f"slide-{slide['id']:02d}.html"
    png_path = OUT / f"slide-{slide['id']:02d}.png"
    uri = f"file:///{str(html_path.resolve()).replace(chr(92), '/')}"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1080,1440", f"--screenshot={png_path}", uri],
                   check=False, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if png_path.exists():
        print(f"png : {png_path.name}")
        ok += 1
    else:
        print(f"FAIL: {png_path.name}")
print(f"\nDone: {ok}/{len(data['slides'])}")
