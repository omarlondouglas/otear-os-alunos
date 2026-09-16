import { NextResponse } from "next/server";
import path from "path";
import fs from "fs";
import { isS3Configured, listCarouselsFromS3 } from "@/lib/s3";
import { getTenantContext } from "@/lib/auth";
import { tenantOutputDir } from "@/lib/tenant";

const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_OUTPUT = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

interface Carousel {
  id: string;
  version: string;
  date: string;
  topic: string;
  slides: string[];
  slideType: "image" | "html";
}

function findSlideFiles(dir: string): { file: string; type: "image" | "html" }[] {
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter((f) => /^slide-\d+/i.test(f)).sort();

  // Prefer JPGs (rendered slides with text)
  const jpgs = files.filter((f) => /\.(jpg|jpeg|png)$/i.test(f));
  if (jpgs.length > 0) return jpgs.map((f) => ({ file: f, type: "image" }));

  // Fallback: HTML slides (render in browser)
  const htmls = files.filter((f) => /\.html$/i.test(f));
  return htmls.map((f) => ({ file: f, type: "html" }));
}

function readTopic(dir: string): string {
  // Try multiple files to find topic
  const candidates = ["strategy-brief.md", "research-focus.md", "carousel-content.md"];
  for (const file of candidates) {
    const filePath = path.join(dir, file);
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf-8");
      const match = content.match(/(?:tema|foco|assunto)[:\s]+([^\n]+)/i);
      if (match) return match[1].trim();
    }
  }
  return "";
}

function listCarouselsLocal(outputDir: string): Carousel[] {
  const carousels: Carousel[] = [];
  if (!fs.existsSync(outputDir)) return carousels;

  const entries = fs.readdirSync(outputDir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
    .map((e) => e.name)
    .sort()
    .reverse();

  for (const runId of entries) {
    const runDir = path.join(outputDir, runId);

    // Check if slides are directly in runDir/slides/
    const directSlides = path.join(runDir, "slides");
    if (fs.existsSync(directSlides)) {
      const found = findSlideFiles(directSlides);
      if (found.length > 0) {
        carousels.push({
          id: runId,
          version: "",
          date: runId,
          topic: readTopic(runDir),
          slides: found.map((f) => `/api/slides/${runId}/slides/${f.file}`),
          slideType: found[0].type,
        });
        continue;
      }
    }

    // Check versioned subdirectories (v1, v2, etc.) — skip images/, slides/
    const versions = fs.readdirSync(runDir, { withFileTypes: true })
      .filter((e) => e.isDirectory() && /^v\d+$/i.test(e.name))
      .map((e) => e.name)
      .sort()
      .reverse();

    for (const version of versions) {
      const slidesDir = path.join(runDir, version, "slides");
      const found = findSlideFiles(slidesDir);
      if (found.length === 0) continue;

      carousels.push({
        id: runId,
        version,
        date: runId,
        topic: readTopic(path.join(runDir, version)),
        slides: found.map((f) => `/api/slides/${runId}/${version}/slides/${f.file}`),
        slideType: found[0].type,
      });
    }
  }

  return carousels;
}

export async function GET() {
  const ctx = await getTenantContext();
  const outputDir = ctx
    ? tenantOutputDir(ctx.tenantId, "carousel")
    : LEGACY_OUTPUT;

  // Collect from both sources and merge (local takes priority for same runId)
  const localCarousels = listCarouselsLocal(outputDir);
  const localIds = new Set(localCarousels.map((c) => c.id));

  let s3Carousels: Carousel[] = [];
  if (isS3Configured()) {
    try {
      const s3Result = await listCarouselsFromS3();
      // Only add S3 carousels that don't exist locally
      s3Carousels = s3Result
        .filter((c) => !localIds.has(c.id))
        .map((c) => ({ ...c, version: c.version || "", slideType: c.slideType || "image" as const }));
    } catch { /* S3 failed */ }
  }

  const carousels = [...localCarousels, ...s3Carousels];
  return NextResponse.json({ carousels, source: localCarousels.length > 0 ? "local" : "s3" });
}
