import { NextRequest, NextResponse } from "next/server";
import { execSync } from "child_process";
import fs from "fs";
import path from "path";
import Anthropic from "@anthropic-ai/sdk";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const PROFILES_DIR = path.join(ROOT, "_opensquad", "_memory", "reference-profiles");

const CHROMIUM =
  process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ||
  (process.platform === "win32" ? "" : "/usr/bin/chromium-browser");

/**
 * POST /api/analyze-profile
 * Body: { handle: string }
 *
 * 1. Screenshots the Instagram profile page via headless Chromium
 * 2. Uses Claude Vision to extract: fonts, colors, layout patterns
 * 3. Saves analysis to _opensquad/_memory/reference-profiles/{handle}/
 */
export async function POST(req: NextRequest) {
  const { handle } = (await req.json()) as { handle?: string };
  if (!handle) {
    return NextResponse.json({ error: "handle required" }, { status: 400 });
  }

  const clean = handle.replace(/^@/, "").replace(/[^a-zA-Z0-9._]/g, "");
  const profileDir = path.join(PROFILES_DIR, clean);
  fs.mkdirSync(profileDir, { recursive: true });

  const screenshotPath = path.join(profileDir, "profile-grid.jpg");
  const analysisPath = path.join(profileDir, "design-analysis.json");

  // Step 1: Screenshot the profile page using headless Chromium
  const profileUrl = `https://www.instagram.com/${clean}/`;
  let screenshotOk = false;

  if (CHROMIUM && fs.existsSync(CHROMIUM)) {
    try {
      execSync(
        `"${CHROMIUM}" --headless --disable-gpu --no-sandbox --disable-dev-shm-usage ` +
          `--window-size=1440,2000 --screenshot="${screenshotPath}" --hide-scrollbars "${profileUrl}"`,
        { timeout: 25000, stdio: "ignore" }
      );
      screenshotOk = fs.existsSync(screenshotPath) && fs.statSync(screenshotPath).size > 5000;
    } catch (err) {
      console.error("[analyze-profile] Chromium screenshot failed:", err);
    }
  } else {
    console.warn("[analyze-profile] Chromium not found at:", CHROMIUM);
  }

  // Step 2: Analyze with Claude Vision
  let analysis: DesignAnalysis | null = null;

  if (screenshotOk) {
    try {
      analysis = await analyzeWithVision(screenshotPath, clean);
    } catch (err) {
      console.error("[analyze-profile] Vision analysis failed:", err);
    }
  }

  // Step 3: Fallback
  if (!analysis) {
    analysis = {
      handle: clean,
      fonts: [],
      primaryColors: [],
      style: "unknown",
      layoutPattern: "unknown",
      notes: screenshotOk
        ? "Screenshot captured but vision analysis unavailable (check ANTHROPIC_API_KEY or CLAUDE_OAUTH_ACCESS_TOKEN)"
        : !CHROMIUM || !fs.existsSync(CHROMIUM)
        ? "Chromium not available in this environment"
        : "Could not screenshot profile — Instagram may require login or profile is private",
      analyzedAt: new Date().toISOString(),
    };
  }

  fs.writeFileSync(analysisPath, JSON.stringify(analysis, null, 2), "utf-8");

  return NextResponse.json({ ok: analysis.style !== "unknown", analysis, screenshotOk });
}

// ─── Claude Vision Analysis ──────────────────────────────────

interface DesignAnalysis {
  handle: string;
  fonts: string[];
  primaryColors: string[];
  style: string;
  layoutPattern: string;
  notes: string;
  analyzedAt: string;
}

async function analyzeWithVision(
  screenshotPath: string,
  handle: string
): Promise<DesignAnalysis> {
  const oauthToken = process.env.CLAUDE_OAUTH_ACCESS_TOKEN;
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!oauthToken && !apiKey) {
    throw new Error("CLAUDE_OAUTH_ACCESS_TOKEN or ANTHROPIC_API_KEY required");
  }

  const client = oauthToken
    ? new Anthropic({
        apiKey: "placeholder",
        defaultHeaders: { Authorization: `Bearer ${oauthToken}` },
        baseURL: "https://api.anthropic.com",
      })
    : new Anthropic({ apiKey: apiKey! });

  const imageData = fs.readFileSync(screenshotPath).toString("base64");

  const response = await client.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/jpeg",
              data: imageData,
            },
          },
          {
            type: "text",
            text: `Analyze this Instagram profile (@${handle}) screenshot and extract the design system used in their posts/carousels.

Return ONLY a JSON object (no markdown, no explanation):
{
  "handle": "${handle}",
  "fonts": ["font name 1", "font name 2"],
  "primaryColors": ["#hex1", "#hex2", "#hex3"],
  "style": "description of visual style in 1 sentence",
  "layoutPattern": "description of how text is positioned in their posts",
  "notes": "any other design observations (gradients, overlays, icons, branding elements)"
}

Focus on: What fonts do they use in carousel text? What are the dominant colors? How do they structure text hierarchy in posts?
If you can't identify specific fonts, describe the font style (e.g., "geometric sans-serif similar to Poppins/Urbanist").`,
          },
        ],
      },
    ],
  });

  const text =
    response.content[0].type === "text" ? response.content[0].text : "";

  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    throw new Error("No JSON in vision response");
  }

  const parsed = JSON.parse(jsonMatch[0]) as DesignAnalysis;
  parsed.analyzedAt = new Date().toISOString();
  return parsed;
}

/**
 * GET /api/analyze-profile?handle=X
 * Returns saved analysis if it exists
 */
export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const handle = url.searchParams.get("handle")?.replace(/^@/, "") || "";

  if (!handle) {
    if (!fs.existsSync(PROFILES_DIR)) return NextResponse.json({ profiles: [] });
    const dirs = fs
      .readdirSync(PROFILES_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory());

    const profiles = dirs.map((d) => {
      const ap = path.join(PROFILES_DIR, d.name, "design-analysis.json");
      if (fs.existsSync(ap)) {
        return JSON.parse(fs.readFileSync(ap, "utf-8"));
      }
      return { handle: d.name, fonts: [], primaryColors: [], style: "not analyzed" };
    });

    return NextResponse.json({ profiles });
  }

  const ap = path.join(PROFILES_DIR, handle, "design-analysis.json");
  if (!fs.existsSync(ap)) {
    return NextResponse.json({ exists: false });
  }

  const analysis = JSON.parse(fs.readFileSync(ap, "utf-8"));
  return NextResponse.json({ exists: true, analysis });
}
