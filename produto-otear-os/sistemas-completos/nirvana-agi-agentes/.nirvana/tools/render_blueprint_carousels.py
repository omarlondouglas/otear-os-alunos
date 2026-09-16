from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
W, H = 1080, 1350


@dataclass
class Slide:
    index: int
    title: str
    copy: str
    visual: str


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default(size=size)


FONT_TITLE = font(64, True)
FONT_SUBTITLE = font(42, True)
FONT_BODY = font(32)
FONT_BODY_BOLD = font(32, True)
FONT_SMALL = font(24)
FONT_META = font(22, True)


def extract_value(block: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}\**\s*:?\s*(.*?)(?=\n\*\*|$)"
    match = re.search(pattern, block, flags=re.S | re.I)
    if not match:
        return ""
    value = match.group(1)
    value = re.sub(r"\n\s*", "\n", value)
    value = value.replace("  \n", "\n").strip()
    return clean_text(value)


def clean_text(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"__(.*?)__", r"\1", value)
    value = value.replace("**", "")
    return value.strip()


def parse_slides(path: Path) -> tuple[str, list[Slide]]:
    text = path.read_text(encoding="utf-8")
    deck_title = re.search(r"^#\s+(.+)$", text, flags=re.M)
    title = deck_title.group(1).strip() if deck_title else path.stem
    parts = re.split(r"(?m)^## Slide\s+(\d+)\s*$", text)
    slides: list[Slide] = []
    for i in range(1, len(parts), 2):
        index = int(parts[i])
        block = parts[i + 1]
        slides.append(
            Slide(
                index=index,
                title=extract_value(block, "Título"),
                copy=extract_value(block, "Copy"),
                visual=extract_value(block, "Direção visual"),
            )
        )
    return title, slides


def draw_text_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    width: int,
    font_obj: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int = 12,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines: list[str] = []
    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            lines.append("")
            continue
        avg = max(8, int(width / (font_obj.size * 0.54)))
        lines.extend(textwrap.wrap(paragraph, width=avg, break_long_words=False))
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [lines[max_lines - 1].rstrip(".") + "..."]
    for line in lines:
        if line:
            draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + line_gap
    return y


def draw_blueprint_grid(draw: ImageDraw.ImageDraw) -> None:
    bg = "#07192c"
    minor = "#123b60"
    major = "#1d5f91"
    draw.rectangle((0, 0, W, H), fill=bg)
    for step, color, width in [(36, minor, 1), (180, major, 2)]:
        for x in range(0, W + 1, step):
            draw.line((x, 0, x, H), fill=color, width=width)
        for y in range(0, H + 1, step):
            draw.line((0, y, W, y), fill=color, width=width)
    draw.rectangle((54, 54, W - 54, H - 54), outline="#4cb4e7", width=3)
    draw.rectangle((78, 78, W - 78, H - 78), outline="#1f6f9f", width=1)


def draw_diagram(draw: ImageDraw.ImageDraw, slide: Slide, y0: int) -> None:
    cyan = "#62d9ff"
    white = "#e9fbff"
    accent = "#b8ff4d"
    red = "#ff6b5c"
    if "funil" in (slide.copy + slide.title).lower():
        levels = [(180, "TOPO"), (280, "MEIO"), (380, "FUNDO")]
        for i, (width, label) in enumerate(levels):
            y = y0 + i * 86
            cx = W // 2
            points = [(cx - width, y), (cx + width, y), (cx + width - 45, y + 62), (cx - width + 45, y + 62)]
            draw.polygon(points, outline=cyan, fill=None)
            draw.line(points + [points[0]], fill=cyan, width=4)
            draw.text((cx - 58, y + 17), label, font=FONT_META, fill=white)
    elif any(word in slide.copy.lower() for word in ["processo", "tarefas", "gargalo", "caso de uso"]):
        labels = ["PROCESSO", "GARGALO", "IA", "IMPACTO"]
        for i, label in enumerate(labels):
            x = 112 + i * 224
            draw.rounded_rectangle((x, y0, x + 165, y0 + 82), radius=0, outline=cyan, width=4)
            draw.text((x + 22, y0 + 28), label, font=FONT_META, fill=white)
            if i < len(labels) - 1:
                draw.line((x + 172, y0 + 41, x + 215, y0 + 41), fill=accent, width=4)
                draw.polygon([(x + 215, y0 + 41), (x + 197, y0 + 29), (x + 197, y0 + 53)], fill=accent)
    else:
        for i in range(4):
            y = y0 + i * 62
            draw.line((150, y, 930, y), fill=cyan, width=3)
            draw.ellipse((130, y - 10, 150, y + 10), fill=accent if i == 2 else red)
        draw.arc((355, y0 - 60, 725, y0 + 245), 205, 335, fill=accent, width=5)


def render_slide(deck_title: str, slide: Slide, total: int, out_path: Path) -> None:
    img = Image.new("RGB", (W, H), "#07192c")
    draw = ImageDraw.Draw(img)
    draw_blueprint_grid(draw)

    cyan = "#62d9ff"
    white = "#e9fbff"
    pale = "#b7d7e8"
    accent = "#b8ff4d"

    draw.text((92, 92), f"BLUEPRINT / {slide.index:02d}-{total:02d}", font=FONT_META, fill=accent)
    header = deck_title.upper()
    if len(header) > 58:
        header = header[:55].rstrip() + "..."
    draw.text((92, 124), header, font=FONT_SMALL, fill=pale)
    draw.line((92, 174, 988, 174), fill=cyan, width=2)

    title = slide.title.strip().rstrip(".")
    y = draw_text_box(draw, title, (92, 230), 880, FONT_TITLE, white, line_gap=10, max_lines=3)
    draw.line((92, y + 22, 355, y + 22), fill=accent, width=6)

    y = max(y + 70, 455)
    body_bottom = draw_text_box(draw, slide.copy.strip(), (92, y), 895, FONT_BODY, white, line_gap=11, max_lines=7)

    diagram_y = min(max(body_bottom + 38, 760), 875)
    draw_diagram(draw, slide, diagram_y)

    visual = slide.visual.strip()
    draw.rectangle((92, 1114, 988, 1237), outline=cyan, width=2)
    draw.text((116, 1136), "NOTA DE DIREÇÃO VISUAL", font=FONT_META, fill=accent)
    draw_text_box(draw, visual, (116, 1174), 835, FONT_SMALL, pale, line_gap=7, max_lines=2)
    draw.text((92, 1266), "diagnóstico > ferramenta > piloto > métrica > escala", font=FONT_SMALL, fill="#75b9d7")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def main() -> None:
    decks = [
        ROOT / ".nirvana/outputs/36e72cb2-be85-4763-b083-4f8e014cda15/carrossel-metricas-funil.md",
        ROOT / ".nirvana/outputs/9ffec8b0-02d4-4b22-a2e1-d1518101af55/carrossel-adocao-ia-empresa.md",
    ]
    for deck in decks:
        deck_title, slides = parse_slides(deck)
        out_dir = deck.parent / "blueprint-images"
        for slide in slides:
            render_slide(deck_title, slide, len(slides), out_dir / f"slide-{slide.index:02d}.png")
        print(f"{deck.name}: {len(slides)} imagens em {out_dir}")


if __name__ == "__main__":
    main()
