import { NextRequest, NextResponse } from "next/server";
import path from "path";
import { renderSlideHtml, SlideData } from "@/lib/render-slides";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");

// POST /api/render-slide — render a single slide JSON to HTML (for live editor preview)
export async function POST(req: NextRequest) {
  try {
    const { slide, runId } = await req.json() as { slide: SlideData; runId?: string };
    if (!slide) return NextResponse.json({ error: "slide required" }, { status: 400 });

    // Resolve images dir for local file fallback
    const imagesDir = runId
      ? path.join(ROOT, "squads", "noticias-carrossel-ia", "output", runId, "v1", "images")
      : "";

    const html = await renderSlideHtml(slide, imagesDir);
    return new NextResponse(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  } catch (err) {
    console.error("[render-slide]", err);
    return NextResponse.json({ error: "render failed" }, { status: 500 });
  }
}
