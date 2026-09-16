import { NextResponse } from "next/server";
import path from "path";
import fs from "fs";
import { getTenantContext } from "@/lib/auth";
import { tenantOutputDir } from "@/lib/tenant";

const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_OUTPUT = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

interface SlideContent {
  number: number;
  label: string;
  title?: string;
  headline?: string;
  supportingText?: string;
  accentKeywords?: string;
  photo?: string;
  background?: string;
  branding?: string;
  source?: string;
}

interface CarouselContent {
  format: string;
  slides: SlideContent[];
  caption: string;
  hashtags: string;
  runId: string;
}

function findLatestCarouselContent(outputDir: string): { filePath: string; runId: string } | null {
  if (!fs.existsSync(outputDir)) return null;

  const entries = fs
    .readdirSync(outputDir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
    .map((e) => e.name)
    .sort()
    .reverse();

  for (const runId of entries) {
    const runDir = path.join(outputDir, runId);

    // Check directly in run dir
    const directPath = path.join(runDir, "carousel-content.md");
    if (fs.existsSync(directPath)) {
      return { filePath: directPath, runId };
    }

    // Check versioned subdirs (v1, v2, etc.) — latest first
    const versions = fs
      .readdirSync(runDir, { withFileTypes: true })
      .filter((e) => e.isDirectory() && /^v\d+$/i.test(e.name))
      .map((e) => e.name)
      .sort()
      .reverse();

    for (const version of versions) {
      const versionedPath = path.join(runDir, version, "carousel-content.md");
      if (fs.existsSync(versionedPath)) {
        return { filePath: versionedPath, runId: `${runId}/${version}` };
      }
    }
  }

  return null;
}

function parseCarouselContent(raw: string): Omit<CarouselContent, "runId"> {
  let format = "";
  const slides: SlideContent[] = [];
  let caption = "";
  let hashtags = "";

  // Extract format
  const formatMatch = raw.match(/=== FORMAT ===\s*\n([^\n]+)/);
  if (formatMatch) {
    format = formatMatch[1].trim();
  }

  // Extract slides section
  const slidesMatch = raw.match(/=== SLIDES ===\s*\n([\s\S]*?)(?===\s*CAPTION|$)/);
  if (slidesMatch) {
    const slidesBlock = slidesMatch[1];
    const slideChunks = slidesBlock.split(/(?=Slide \d+)/);

    for (const chunk of slideChunks) {
      const headerMatch = chunk.match(/^Slide (\d+)\s*\(([^)]+)\):/);
      if (!headerMatch) continue;

      const slide: SlideContent = {
        number: parseInt(headerMatch[1], 10),
        label: headerMatch[2].trim(),
      };

      const fieldMatch = (field: string) => {
        const re = new RegExp(`^\\s*${field}:\\s*(.+)`, "mi");
        const m = chunk.match(re);
        return m ? m[1].trim() : undefined;
      };

      slide.title = fieldMatch("Title");
      slide.headline = fieldMatch("Headline");
      slide.supportingText = fieldMatch("Supporting text");
      slide.accentKeywords = fieldMatch("Accent keywords");
      slide.photo = fieldMatch("Photo");
      slide.background = fieldMatch("Background");
      slide.branding = fieldMatch("Branding");
      slide.source = fieldMatch("Source");

      slides.push(slide);
    }
  }

  // Extract caption
  const captionMatch = raw.match(/=== CAPTION ===\s*\n([\s\S]*?)(?===\s*HASHTAGS|$)/);
  if (captionMatch) {
    caption = captionMatch[1].trim();
  }

  // Extract hashtags
  const hashtagsMatch = raw.match(/=== HASHTAGS ===\s*\n([\s\S]*?)$/);
  if (hashtagsMatch) {
    hashtags = hashtagsMatch[1].trim();
  }

  return { format, slides, caption, hashtags };
}

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const ctx = await getTenantContext();
    const outputDir = ctx
      ? tenantOutputDir(ctx.tenantId, "carousel")
      : LEGACY_OUTPUT;
    const result = findLatestCarouselContent(outputDir);
    if (!result) {
      return NextResponse.json(
        { error: "Nenhum conteudo encontrado" },
        { status: 404 }
      );
    }

    const raw = fs.readFileSync(result.filePath, "utf-8");
    const parsed = parseCarouselContent(raw);

    return NextResponse.json({
      ...parsed,
      runId: result.runId,
    });
  } catch (err) {
    return NextResponse.json(
      { error: `Erro ao ler conteudo: ${err}` },
      { status: 500 }
    );
  }
}
