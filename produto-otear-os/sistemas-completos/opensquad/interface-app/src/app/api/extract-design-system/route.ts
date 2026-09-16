import { NextRequest, NextResponse } from "next/server";
import path from "path";
import fs from "fs";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");

interface UserDesignSystem {
  primary: string;
  background: string;
  text: string;
  font: string;
  fontUrl: string;
  borderRadius: number;
  sourceUrl: string;
  extractedAt: string;
}

function rgbToHex(rgb: string): string {
  const m = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  if (!m) return rgb;
  return (
    "#" +
    [m[1], m[2], m[3]]
      .map((x) => parseInt(x).toString(16).padStart(2, "0"))
      .join("")
  );
}

function cleanFont(fontFamily: string | null | undefined): string {
  if (!fontFamily) return "";
  // Take first font in the stack, remove quotes
  const first = fontFamily.split(",")[0].trim().replace(/['"]/g, "");
  return first;
}

function cleanRadius(borderRadius: string | null | undefined): number {
  if (!borderRadius) return 12;
  const match = borderRadius.match(/(\d+(\.\d+)?)/);
  if (!match) return 12;
  const val = parseFloat(match[1]);
  return isNaN(val) || val === 0 ? 12 : Math.round(val);
}

function detectGoogleFont(fontName: string): string {
  if (!fontName) return "";
  const systemFonts = [
    "arial",
    "helvetica",
    "sans-serif",
    "serif",
    "monospace",
    "times",
    "georgia",
    "verdana",
    "tahoma",
    "trebuchet",
    "impact",
    "comic sans",
    "courier",
    "lucida",
    "system-ui",
    "-apple-system",
    "segoe ui",
    "roboto",
    "ubuntu",
  ];
  const lower = fontName.toLowerCase();
  if (systemFonts.some((f) => lower.includes(f))) return "";
  // Looks like a Google Font candidate
  const encoded = encodeURIComponent(fontName).replace(/%20/g, "+");
  return `https://fonts.googleapis.com/css2?family=${encoded}:wght@400;700&display=swap`;
}

interface ExtractedRaw {
  cssVars: Record<string, string>;
  bodyFont: string;
  bodyBg: string;
  bodyColor: string;
  headingFont: string | null;
  headingColor: string | null;
  headingWeight: string | null;
  btnBg: string | null;
  btnColor: string | null;
  btnRadius: string | null;
  linkColor: string | null;
}

async function extractViaPlaywright(url: string): Promise<ExtractedRaw | null> {
  try {
    // Dynamically import playwright to avoid build errors if not installed
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const playwrightModule = "playwright";
    const { chromium } = require(/* webpackIgnore: true */ playwrightModule);

    const chromiumExec = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
    const launchOptions: Record<string, unknown> = {
      args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"],
    };
    if (chromiumExec) {
      launchOptions.executablePath = chromiumExec;
    }

    const browser = await chromium.launch(launchOptions);
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(15000);

    await page.goto(url, { waitUntil: "domcontentloaded" });

    const extracted = await page.evaluate(() => {
      // 1. Collect all CSS custom properties from stylesheets
      const cssVars: Record<string, string> = {};
      for (const sheet of Array.from(document.styleSheets)) {
        try {
          for (const rule of Array.from((sheet as CSSStyleSheet).cssRules || [])) {
            if (
              rule instanceof CSSStyleRule &&
              rule.selectorText === ":root"
            ) {
              for (const prop of Array.from(rule.style)) {
                if (prop.startsWith("--")) {
                  cssVars[prop] = rule.style.getPropertyValue(prop).trim();
                }
              }
            }
          }
        } catch {
          /* cross-origin */
        }
      }

      // 2. Computed styles of key elements
      const bodyStyle = window.getComputedStyle(document.body);
      const h1 = document.querySelector(
        'h1, h2, .hero-title, [class*="title"], [class*="heading"]'
      );
      const h1Style = h1
        ? window.getComputedStyle(h1 as Element)
        : null;
      const btn = document.querySelector(
        'button, a.btn, .btn, .button, [class*="button"], [class*="cta"]'
      );
      const btnStyle = btn
        ? window.getComputedStyle(btn as Element)
        : null;
      const link = document.querySelector("a[href]");
      const linkStyle = link
        ? window.getComputedStyle(link as Element)
        : null;

      return {
        cssVars,
        bodyFont: bodyStyle.fontFamily,
        bodyBg: bodyStyle.backgroundColor,
        bodyColor: bodyStyle.color,
        headingFont: h1Style?.fontFamily ?? null,
        headingColor: h1Style?.color ?? null,
        headingWeight: h1Style?.fontWeight ?? null,
        btnBg: btnStyle?.backgroundColor ?? null,
        btnColor: btnStyle?.color ?? null,
        btnRadius: btnStyle?.borderRadius ?? null,
        linkColor: linkStyle?.color ?? null,
      };
    });

    await browser.close();
    return extracted as ExtractedRaw;
  } catch (err) {
    console.error("[extract-design-system] Playwright failed:", err);
    return null;
  }
}

async function extractViaFetch(url: string): Promise<Partial<ExtractedRaw> | null> {
  try {
    const res = await fetch(url, {
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      },
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return null;
    const html = await res.text();

    // Extract colors from inline CSS / style tags using regex
    const cssVars: Record<string, string> = {};

    // Look for CSS custom properties
    const varMatches = html.matchAll(/--([a-zA-Z][\w-]*):\s*([^;}\n]+)/g);
    for (const m of varMatches) {
      cssVars[`--${m[1]}`] = m[2].trim();
    }

    // Extract hex colors for a rough primary candidate
    const hexColors = [...new Set(html.match(/#[0-9a-fA-F]{6}/g) || [])];

    // Try to find font-family references
    const fontMatch = html.match(/font-family:\s*['"]?([^'";\n,]+)/i);
    const bodyFont = fontMatch ? fontMatch[1].trim() : "";

    // Use most frequent/early hex as a fallback primary
    const primary = hexColors.find((c) => c.toLowerCase() !== "#ffffff" && c.toLowerCase() !== "#000000") || "";

    return {
      cssVars,
      bodyFont,
      bodyBg: "",
      bodyColor: "",
      headingFont: null,
      headingColor: null,
      headingWeight: null,
      btnBg: primary || null,
      btnColor: null,
      btnRadius: null,
      linkColor: null,
    };
  } catch (err) {
    console.error("[extract-design-system] fetch fallback failed:", err);
    return null;
  }
}

function parseDesignSystem(
  raw: Partial<ExtractedRaw>,
  url: string
): UserDesignSystem {
  const vars = raw.cssVars || {};

  // Primary color
  const primaryRaw =
    vars["--primary"] ||
    vars["--color-primary"] ||
    vars["--brand"] ||
    vars["--accent"] ||
    raw.btnBg ||
    "";
  const primary = rgbToHex(primaryRaw.trim()) || "#FF6A00";

  // Background color
  const backgroundRaw =
    vars["--background"] ||
    vars["--bg"] ||
    vars["--color-background"] ||
    raw.bodyBg ||
    "";
  const background = rgbToHex(backgroundRaw.trim()) || "#FFFFFF";

  // Text color
  const textRaw =
    vars["--foreground"] ||
    vars["--text"] ||
    vars["--color-text"] ||
    raw.bodyColor ||
    "";
  const text = rgbToHex(textRaw.trim()) || "#111111";

  // Font
  const fontRaw = raw.headingFont || raw.bodyFont || null;
  const font = cleanFont(fontRaw);

  // Google Fonts URL
  const fontUrl = detectGoogleFont(font);

  // Border radius
  const borderRadius = cleanRadius(raw.btnRadius);

  return {
    primary,
    background,
    text,
    font,
    fontUrl,
    borderRadius,
    sourceUrl: url,
    extractedAt: new Date().toISOString(),
  };
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json() as { url?: string };
    const url = body?.url;

    if (!url || typeof url !== "string") {
      return NextResponse.json(
        { ok: false, error: "url is required", partial: null },
        { status: 400 }
      );
    }

    // Ensure URL has a protocol
    const normalizedUrl = url.startsWith("http") ? url : `https://${url}`;

    // Try Playwright first, fall back to fetch
    let raw: Partial<ExtractedRaw> | null = await extractViaPlaywright(normalizedUrl);
    if (!raw) {
      raw = await extractViaFetch(normalizedUrl);
    }

    if (!raw) {
      return NextResponse.json({
        ok: false,
        error: "Could not extract design system from the provided URL",
        partial: null,
      });
    }

    const designSystem = parseDesignSystem(raw, normalizedUrl);

    // Save to _opensquad/_memory/user-design-system.json
    const memoryDir = path.join(ROOT, "_opensquad", "_memory");
    fs.mkdirSync(memoryDir, { recursive: true });
    const dsPath = path.join(memoryDir, "user-design-system.json");
    fs.writeFileSync(dsPath, JSON.stringify(designSystem, null, 2), "utf-8");

    return NextResponse.json({ ok: true, designSystem });
  } catch (err) {
    console.error("[extract-design-system] unexpected error:", err);
    return NextResponse.json({
      ok: false,
      error: String(err),
      partial: null,
    });
  }
}
