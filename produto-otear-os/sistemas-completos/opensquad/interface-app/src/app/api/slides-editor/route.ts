import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { renderSlidesToJpg } from "@/lib/render-slides";
import { SlidesJson } from "@/lib/render-slides";
import { isS3Configured, fetchSlidesJsonFromS3, saveSlidesJsonToS3, getPublicBaseUrl } from "@/lib/s3";
import { getTenantContext } from "@/lib/auth";
import { tenantOutputDir } from "@/lib/tenant";

const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_OUTPUT = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

async function resolveOutputDir(): Promise<string> {
  const ctx = await getTenantContext();
  if (ctx) {
    const dir = tenantOutputDir(ctx.tenantId, "carousel");
    if (fs.existsSync(dir)) return dir;
  }
  return LEGACY_OUTPUT;
}

function getRunDir(outputDir: string, runId?: string | null): { name: string; dir: string } | null {
  if (!fs.existsSync(outputDir)) return null;
  if (runId && runId !== "latest") {
    const dir = path.join(outputDir, runId);
    if (fs.existsSync(dir)) return { name: runId, dir };
  }
  const dirs = fs.readdirSync(outputDir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
    .map((e) => e.name)
    .sort()
    .reverse();
  if (!dirs.length) return null;
  return { name: dirs[0], dir: path.join(outputDir, dirs[0]) };
}

function findVersionDir(runDir: string): string {
  const v1 = path.join(runDir, "v1");
  return fs.existsSync(v1) ? v1 : runDir;
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

/** Resolve imageFile references to full URLs */
function resolveImageUrls(slides: SlidesJson["slides"], runId: string, source: "local" | "s3", vDir?: string): SlidesJson["slides"] {
  return slides.map((slide) => {
    if (!slide.imageFile || slide.imageFile.startsWith("http")) return slide;

    // Local file: check if exists and serve via API
    if (source === "local" && vDir) {
      const imgPath = path.join(vDir, "images", slide.imageFile);
      if (fs.existsSync(imgPath)) {
        // Convert to base64 data URI for editor preview
        const data = fs.readFileSync(imgPath).toString("base64");
        const ext = path.extname(slide.imageFile).replace(".", "");
        const mime = ext === "png" ? "image/png" : "image/jpeg";
        return { ...slide, imageFile: `data:${mime};base64,${data}` };
      }
    }

    // S3: resolve to public URL
    if (isS3Configured()) {
      const publicBase = getPublicBaseUrl();
      return { ...slide, imageFile: `${publicBase}/noticias-carrossel-ia/${runId}/images/${slide.imageFile}` };
    }

    return slide;
  });
}

// GET /api/slides-editor?runId= — return slides-data.json for the specified run (or latest)
export async function GET(req: NextRequest) {
  const runId = new URL(req.url).searchParams.get("runId");
  const outputDir = await resolveOutputDir();

  // Try local first
  const run = getRunDir(outputDir, runId);
  if (run) {
    const vDir = findVersionDir(run.dir);
    const jsonPath = findSlidesJson(vDir);
    if (jsonPath) {
      const json: SlidesJson = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
      const slides = resolveImageUrls(json.slides, run.name, "local", vDir);
      return NextResponse.json({ slides, runId: run.name, jsonPath, source: "local" });
    }
  }

  // Fallback: try S3
  if (runId && isS3Configured()) {
    const s3Data = await fetchSlidesJsonFromS3(runId);
    if (s3Data) {
      const slides = resolveImageUrls((s3Data as SlidesJson).slides, runId, "s3");
      return NextResponse.json({ slides, runId, source: "s3" });
    }
  }

  return NextResponse.json({ error: "slides-data.json not found" }, { status: 404 });
}

// POST /api/slides-editor — save edited slides-data.json and re-render
export async function POST(req: NextRequest) {
  const urlRunId = new URL(req.url).searchParams.get("runId");
  const body = await req.json() as { slides: SlidesJson["slides"]; runId?: string };
  const runId = body.runId ?? urlRunId;

  const { slides } = body;
  if (!slides?.length) return NextResponse.json({ error: "slides required" }, { status: 400 });

  const updated: SlidesJson = { slides };

  const outputDir = await resolveOutputDir();

  // Try local first
  const run = getRunDir(outputDir, runId);
  if (run) {
    const vDir = findVersionDir(run.dir);
    const jsonPath = findSlidesJson(vDir);
    if (jsonPath) {
      // Save updated JSON
      fs.writeFileSync(jsonPath, JSON.stringify(updated, null, 2), "utf-8");

      // Delete old rendered slides so they get re-generated
      const slidesDir = path.join(path.dirname(jsonPath), "slides");
      if (fs.existsSync(slidesDir)) {
        for (const f of fs.readdirSync(slidesDir)) {
          if (/\.(jpg|jpeg|png)$/i.test(f)) {
            fs.unlinkSync(path.join(slidesDir, f));
          }
        }
      }

      // Re-render
      const rendered = await renderSlidesToJpg(vDir);

      const slideResults = rendered.map((p) => {
        const ext = path.extname(p).replace(".", "");
        const mime = ext === "png" ? "image/png" : "image/jpeg";
        const data = fs.readFileSync(p).toString("base64");
        return { type: "image" as const, url: `data:${mime};base64,${data}`, name: path.basename(p) };
      });

      return NextResponse.json({ ok: true, slides: slideResults, count: rendered.length });
    }
  }

  // Fallback: save to S3 (no re-render, just save JSON)
  if (runId && isS3Configured()) {
    const saved = await saveSlidesJsonToS3(runId, updated);
    if (saved) {
      return NextResponse.json({ ok: true, source: "s3", count: slides.length });
    }
  }

  return NextResponse.json({ error: "no run found" }, { status: 404 });
}
