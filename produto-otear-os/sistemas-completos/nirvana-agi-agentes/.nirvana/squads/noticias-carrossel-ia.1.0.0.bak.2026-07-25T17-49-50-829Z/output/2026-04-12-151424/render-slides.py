import json, os, subprocess, sys

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.abspath(os.path.join(RUN_DIR, "..", "..", "pipeline", "slide-template.html"))
SLIDES_PATH = os.path.join(RUN_DIR, "slides-data.json")
OUTPUT_DIR = os.path.join(RUN_DIR, "slides")
IMAGES_DIR = os.path.join(RUN_DIR, "images", "v1")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    template = f.read()

with open(SLIDES_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


def render_element(el):
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
        items = "".join(f"<li>{i}</li>" for i in el["items"])
        return f'<ul class="list">{items}</ul>'
    if t == "cta":
        return f'<div class="cta-box">{el["text"]}</div>'
    if t == "swipe":
        return '<div class="swipe">arraste</div>'
    if t == "spacer":
        return '<div class="spacer"></div>'
    return ""


def render_all():
    htmls = []
    for slide in data["slides"]:
        theme = f"theme-{slide['theme']}"
        img_file = slide.get("imageFile")
        body_html = "\n    ".join(render_element(el) for el in slide["elements"])
        if img_file:
            abs_img = os.path.join(RUN_DIR, img_file).replace("\\", "/")
            img_layer = f'<div class="img-layer" style="background-image: url(\'file:///{abs_img}\');"></div>'
        else:
            img_layer = ""
        html = template.replace("{{THEME}}", theme)
        html = html.replace("{{IMG_CLASS}}", "")
        html = html.replace("{{IMG_LAYER}}", img_layer)
        html = html.replace("{{BODY_HTML}}", body_html)
        out_html = os.path.join(OUTPUT_DIR, f"slide-{slide['id']:02d}.html")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        htmls.append((slide["id"], out_html))
        print(f"html: slide-{slide['id']:02d}.html")
    return htmls


def screenshot(html_path, png_path):
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--window-size=1080,1440",
        f"--screenshot={png_path}",
        f"file:///{os.path.abspath(html_path).replace(chr(92), '/')}",
    ]
    subprocess.run(cmd, check=False, timeout=60, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.exists(png_path)


if __name__ == "__main__":
    htmls = render_all()
    print("\n--- Screenshots ---")
    ok = 0
    for sid, html in htmls:
        png = os.path.join(OUTPUT_DIR, f"slide-{sid:02d}.png")
        if screenshot(html, png):
            print(f"png : slide-{sid:02d}.png")
            ok += 1
        else:
            print(f"FAIL: slide-{sid:02d}.png")
    print(f"\nDone: {ok}/{len(htmls)} PNG gerados em {OUTPUT_DIR}")
