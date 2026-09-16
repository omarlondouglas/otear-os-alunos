import { NextRequest, NextResponse } from "next/server";
import path from "path";
import fs from "fs";
import { getTenantContext } from "@/lib/auth";
import { tenantOutputDir } from "@/lib/tenant";

const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_OUTPUT = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: segments } = await params;

  if (!segments || segments.length < 2) {
    return new NextResponse("Not found", { status: 404 });
  }

  const ctx = await getTenantContext();
  let outputDir = LEGACY_OUTPUT;
  if (ctx) {
    const tenantDir = tenantOutputDir(ctx.tenantId, "carousel");
    if (fs.existsSync(tenantDir)) outputDir = tenantDir;
  }

  const filePath = path.join(outputDir, ...segments);

  // Safety: must stay within output dir
  if (!filePath.startsWith(outputDir)) {
    return new NextResponse("Forbidden", { status: 403 });
  }

  if (!fs.existsSync(filePath)) {
    return new NextResponse("Not found", { status: 404 });
  }

  const ext = path.extname(filePath).toLowerCase();
  const mimeMap: Record<string, string> = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
  };
  const mime = mimeMap[ext] || "application/octet-stream";

  const buffer = fs.readFileSync(filePath);
  return new NextResponse(buffer, {
    headers: {
      "Content-Type": mime,
      "Cache-Control": "public, max-age=86400",
    },
  });
}
