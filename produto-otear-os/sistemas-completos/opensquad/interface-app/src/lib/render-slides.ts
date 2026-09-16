import { execSync } from "child_process";
import fs from "fs";
import path from "path";

const TEMPLATE_PATH = path.resolve(
  process.cwd(),
  "..",
  "squads/noticias-carrossel-ia/pipeline/slide-template.html"
);

export interface SlideElement {
  type: "tag" | "stat" | "headline" | "sub" | "body" | "list" | "cta" | "spacer" | "swipe";
  text?: string;
  items?: string[];
}

export interface SlideData {
  id: number;
  theme: "dark" | "light" | "accent" | "black";
  imageFile?: string | null;
  elements: SlideElement[];
}

export interface SlidesJson {
  slides: SlideData[];
}

function elementToHtml(el: SlideElement): string {
  switch (el.type) {
    case "tag":
      return `<div class="tag">${el.text || ""}</div>`;
    case "stat":
      return `<div class="stat">${el.text || ""}</div>`;
    case "headline":
      return `<div class="headline">${el.text || ""}</div>`;
    case "sub":
      return `<div class="sub">${el.text || ""}</div>`;
    case "body":
      return `<div class="body-text">${el.text || ""}</div>`;
    case "list":
      const items = (el.items || []).map((i) => `<li>${i}</li>`).join("\n");
      return `<ul class="list">${items}</ul>`;
    case "cta":
      return `<div class="cta-box">${el.text || ""}</div>`;
    case "spacer":
      return `<div class="spacer"></div>`;
    case "swipe":
      return `<div class="swipe">arraste para continuar</div>`;
    default:
      return "";
  }
}

async function fetchImageAsBase64(imageFile: string, imagesDir: string): Promise<{ data: string; mimeType: string } | null> {
  // Remote URL (from R2 image bank)
  if (imageFile.startsWith("http://") || imageFile.startsWith("https://")) {
    try {
      const res = await fetch(imageFile);
      if (!res.ok) return null;
      const buf = Buffer.from(await res.arrayBuffer());
      const ct = res.headers.get("content-type") || "image/jpeg";
      const mimeType = ct.split(";")[0].trim();
      return { data: buf.toString("base64"), mimeType };
    } catch {
      return null;
    }
  }

  // Local file (from AI image generator)
  const imgPath = path.join(imagesDir, imageFile);
  if (fs.existsSync(imgPath)) {
    const data = fs.readFileSync(imgPath).toString("base64");
    const ext = path.extname(imageFile).replace(".", "").replace("jpg", "jpeg");
    const mimeType = ext === "png" ? "image/png" : "image/jpeg";
    return { data, mimeType };
  }

  return null;
}

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const VYVE_FONT_IMPORT =
  "@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..900;1,400..900&family=Space+Mono:wght@400;700&display=swap');";
const VYVE_FONT_STACK = "'Instrument Sans', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
const VYVE_MONO_STACK = "'Space Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace";

export async function renderSlideHtml(slide: SlideData, imagesDir: string): Promise<string> {
  const template = fs.readFileSync(TEMPLATE_PATH, "utf-8");
  const vyveFontOverride = `<style>
      ${VYVE_FONT_IMPORT}
      body { font-family: ${VYVE_FONT_STACK}; }
      .tag,
      .swipe,
      .eyebrow,
      .label,
      nav,
      .skip-link {
        font-family: ${VYVE_MONO_STACK};
      }
    </style>`;

  // Load user design system if available
  const dsPath = path.join(ROOT, "_opensquad", "_memory", "user-design-system.json");
  let dsOverride = "";
  if (fs.existsSync(dsPath)) {
    try {
      const ds = JSON.parse(fs.readFileSync(dsPath, "utf-8"));
      const fontImport = ds.fontUrl ? `@import url('${ds.fontUrl}');` : VYVE_FONT_IMPORT;
      const fontStack = ds.font ? `'${ds.font}', sans-serif` : VYVE_FONT_STACK;
      dsOverride = `<style>
      ${fontImport}
      ${fontStack ? `body { font-family: ${fontStack}; }` : ""}
      .tag, .swipe, .eyebrow, .label, nav, .skip-link { font-family: ${VYVE_MONO_STACK}; }
      .tag { background: ${ds.primary}; color: ${ds.background}; }
      .stat { color: ${ds.primary}; }
      .list li::before { color: ${ds.primary}; }
      .cta-box { border-color: ${ds.primary}; background: ${ds.primary}22; }
      .headline em { background: ${ds.primary}; color: ${ds.background}; }
      .body-text em { background: ${ds.primary}; color: ${ds.background}; }
      body.theme-accent { background: ${ds.primary}; color: ${ds.background}; }
    </style>`;
    } catch { /* ignore */ }
  }

  // Theme class
  const themeClass = `theme-${slide.theme}`;

  // Image layer
  const imgClass = "";
  let imgLayer = "";
  if (slide.imageFile) {
    const img = await fetchImageAsBase64(slide.imageFile, imagesDir);
    if (img) {
      imgLayer = `<div class="img-layer" style="background-image:url('data:${img.mimeType};base64,${img.data}')"></div>`;
    }
  }

  // Body HTML from elements
  const bodyHtml = slide.elements.map(elementToHtml).join("\n    ");

  let html = template
    .replace("{{THEME}}", themeClass)
    .replace("{{IMG_CLASS}}", imgClass)
    .replace("{{IMG_LAYER}}", imgLayer)
    .replace("{{BODY_HTML}}", bodyHtml);

  // Inject design system override after </style>
  if (dsOverride) {
    html = html.replace("</style>", `</style>${dsOverride}`);
  } else {
    html = html.replace("</style>", `</style>${vyveFontOverride}`);
  }

  return html;
}

/**
 * Find slides-data.json, render HTML files, then render to JPG via Chromium.
 */
export async function renderSlidesToJpg(runDir: string): Promise<string[]> {
  // Find slides-data.json
  const jsonPath = findSlidesJson(runDir);

  if (jsonPath) {
    return renderFromJson(jsonPath);
  }

  // Fallback: render existing HTML files
  return renderExistingHtmls(runDir);
}

function findSlidesJson(dir: string): string | null {
  if (!fs.existsSync(dir)) return null;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const found = findSlidesJson(full);
      if (found) return found;
    } else if (entry.name === "slides-data.json") {
      return full;
    }
  }
  return null;
}

async function renderFromJson(jsonPath: string): Promise<string[]> {
  const json: SlidesJson = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
  const slidesDir = path.join(path.dirname(jsonPath), "slides");
  const imagesDir = path.join(path.dirname(jsonPath), "images");

  fs.mkdirSync(slidesDir, { recursive: true });

  const rendered: string[] = [];

  for (const slide of json.slides) {
    const num = String(slide.id).padStart(2, "0");
    const htmlPath = path.join(slidesDir, `slide-${num}.html`);
    const jpgPath = path.join(slidesDir, `slide-${num}.jpg`);

    // Write HTML from template
    const html = await renderSlideHtml(slide, imagesDir);
    fs.writeFileSync(htmlPath, html, "utf-8");

    // Render to JPG
    const jpg = await chromiumScreenshot(htmlPath, jpgPath);
    if (jpg) rendered.push(jpg);
  }

  return rendered;
}

async function renderExistingHtmls(runDir: string): Promise<string[]> {
  const htmlFiles = findSlideHtmlFiles(runDir);
  const rendered: string[] = [];

  for (const htmlPath of htmlFiles) {
    const jpgPath = htmlPath.replace(/\.html$/i, ".jpg");
    if (fs.existsSync(jpgPath)) {
      rendered.push(jpgPath);
      continue;
    }
    const jpg = await chromiumScreenshot(htmlPath, jpgPath);
    if (jpg) rendered.push(jpg);
  }

  return rendered;
}

async function chromiumScreenshot(htmlPath: string, jpgPath: string): Promise<string | null> {
  const chromium =
    process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || "/usr/bin/chromium-browser";

  const absHtml = path.resolve(htmlPath);
  const absJpg = path.resolve(jpgPath);

  try {
    execSync(
      `"${chromium}" --headless --disable-gpu --no-sandbox --disable-dev-shm-usage ` +
        `--window-size=1080,1440 --screenshot="${absJpg}" --hide-scrollbars "file://${absHtml}"`,
      { timeout: 30000 }
    );
    return fs.existsSync(absJpg) ? absJpg : null;
  } catch (err) {
    console.error(`[render] chromium screenshot failed for ${htmlPath}:`, err);
    return null;
  }
}

function findSlideHtmlFiles(dir: string): string[] {
  const results: string[] = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...findSlideHtmlFiles(full));
    else if (/^slide-\d+\.html$/i.test(entry.name)) results.push(full);
  }
  return results;
}
