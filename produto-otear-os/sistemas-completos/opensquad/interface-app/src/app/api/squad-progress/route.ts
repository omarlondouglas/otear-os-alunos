import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { getTenantContext } from "@/lib/auth";
import { tenantOutputDir } from "@/lib/tenant";

const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_OUTPUT = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

function readFileSafe(filePath: string): string | null {
  try {
    if (fs.existsSync(filePath)) return fs.readFileSync(filePath, "utf-8");
  } catch { /* ignore */ }
  return null;
}

function getLatestRunDir(outputDir: string): { name: string; dir: string } | null {
  if (!fs.existsSync(outputDir)) return null;

  // Prefer dated dirs (2026-03-20-...)
  const entries = fs.readdirSync(outputDir, { withFileTypes: true })
    .filter((e) => e.isDirectory());

  const dated = entries
    .filter((e) => /^\d{4}-\d{2}-\d{2}/.test(e.name))
    .map((e) => ({ name: e.name, mtime: fs.statSync(path.join(outputDir, e.name)).mtimeMs }))
    .sort((a, b) => b.mtime - a.mtime);

  if (dated.length > 0) {
    return { name: dated[0].name, dir: path.join(outputDir, dated[0].name) };
  }

  // Fallback: any subdirectory, sorted by mtime
  const any = entries
    .map((e) => ({ name: e.name, mtime: fs.statSync(path.join(outputDir, e.name)).mtimeMs }))
    .sort((a, b) => b.mtime - a.mtime);

  if (any.length > 0) {
    return { name: any[0].name, dir: path.join(outputDir, any[0].name) };
  }

  // Last fallback: output dir itself might have files flat
  const hasContent = fs.readdirSync(outputDir).some((f) =>
    /\.(md|json)$/i.test(f)
  );
  if (hasContent) return { name: ".", dir: outputDir };

  return null;
}

function findVersionDir(runDir: string): string {
  const v1 = path.join(runDir, "v1");
  if (fs.existsSync(v1)) return v1;
  return runDir;
}

function findSlideImages(dir: string): string[] {
  const results: string[] = [];
  if (!fs.existsSync(dir)) return results;

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findSlideImages(full));
    } else if (/^slide-\d+\.(jpg|jpeg|png)$/i.test(entry.name)) {
      results.push(full);
    }
  }
  return results.sort();
}

function findSlideHtmls(dir: string): string[] {
  const results: string[] = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...findSlideHtmls(full));
    else if (/^slide-\d+\.html$/i.test(entry.name)) results.push(full);
  }
  return results.sort();
}

function imageToDataUrl(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase().replace(".", "");
  const mime = ext === "png" ? "image/png" : "image/jpeg";
  const data = fs.readFileSync(filePath).toString("base64");
  return `data:${mime};base64,${data}`;
}

export async function GET() {
  const ctx = await getTenantContext();
  const outputDir = ctx ? tenantOutputDir(ctx.tenantId, "carousel") : LEGACY_OUTPUT;
  const latest = getLatestRunDir(outputDir);
  if (!latest) {
    return NextResponse.json({ hasRun: false });
  }

  const vDir = findVersionDir(latest.dir);

  // Read key files
  const researchBrief = readFileSafe(path.join(vDir, "research-brief.md"));
  const carouselContent = readFileSafe(path.join(vDir, "carousel-content.md"));
  const reviewReport = readFileSafe(path.join(vDir, "review-report.md"));
  const publishResult = readFileSafe(path.join(vDir, "publish-result.md"));
  const slidesData = readFileSafe(path.join(vDir, "slides-data.json"));

  // Find images (raw AI images)
  const imagesDir = path.join(vDir, "images");
  const rawImages: string[] = [];
  if (fs.existsSync(imagesDir)) {
    fs.readdirSync(imagesDir).forEach((f) => {
      if (/\.(png|jpg|jpeg)$/i.test(f)) {
        rawImages.push(path.join(imagesDir, f));
      }
    });
  }

  // Find rendered slides
  const slideImages = findSlideImages(vDir);
  const slideHtmls = findSlideHtmls(vDir);

  // Build slide URLs (prefer JPG over HTML)
  const slides: Array<{ type: "image" | "html"; url: string; name: string }> = [];

  if (slideImages.length > 0) {
    for (const imgPath of slideImages) {
      slides.push({
        type: "image",
        url: imageToDataUrl(imgPath),
        name: path.basename(imgPath),
      });
    }
  } else if (slideHtmls.length > 0) {
    for (const htmlPath of slideHtmls) {
      const content = fs.readFileSync(htmlPath, "utf-8");
      slides.push({
        type: "html",
        url: `data:text/html;charset=utf-8;base64,${Buffer.from(content).toString("base64")}`,
        name: path.basename(htmlPath),
      });
    }
  }

  // Parse carousel-content.md into slides array
  const copySlides = parseCarouselContent(carouselContent);

  return NextResponse.json({
    hasRun: true,
    runId: latest.name,
    stages: {
      research: !!researchBrief,
      copy: !!carouselContent,
      images: rawImages.length > 0,
      slides: slides.length > 0,
      review: !!reviewReport,
      done: !!publishResult,
    },
    researchBrief: researchBrief ? extractResearchSummary(researchBrief) : null,
    copySlides,
    slideCount: Math.max(slides.length, slideHtmls.length, copySlides.length),
    slides,
    publishResult,
  });
}

function extractResearchSummary(md: string): { title: string; bullets: string[] } {
  const lines = md.split("\n").filter((l) => l.trim());
  const title = lines.find((l) => l.startsWith("# ") || l.startsWith("## "))
    ?.replace(/^#+\s*/, "") || "Pesquisa concluída";
  const bullets = lines
    .filter((l) => l.startsWith("- ") || l.startsWith("* "))
    .slice(0, 5)
    .map((l) => l.replace(/^[-*]\s*/, ""));
  return { title, bullets };
}

function parseCarouselContent(md: string | null): Array<{ num: number; label: string; text: string }> {
  if (!md) return [];
  const slides: Array<{ num: number; label: string; text: string }> = [];
  const lines = md.split("\n");
  let current: { num: number; label: string; lines: string[] } | null = null;

  for (const line of lines) {
    const slideMatch = line.match(/^##\s+(?:Slide\s+)?(\d+)[\s—:-]*(.*)/i);
    if (slideMatch) {
      if (current) {
        slides.push({ num: current.num, label: current.label, text: current.lines.filter(Boolean).join(" ") });
      }
      current = { num: parseInt(slideMatch[1]), label: slideMatch[2].trim(), lines: [] };
    } else if (current && line.trim() && !line.startsWith("#")) {
      current.lines.push(line.replace(/^\*+\s*/, "").replace(/\*+/g, "").trim());
    }
  }
  if (current) {
    slides.push({ num: current.num, label: current.label, text: current.lines.filter(Boolean).join(" ") });
  }
  return slides;
}
