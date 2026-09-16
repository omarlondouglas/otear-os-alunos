import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LOCAL_BANK_DIR = path.join(ROOT, "_opensquad", "_image-bank");

/**
 * GET /api/image-bank/file?path=categoria/filename.jpg
 * Serves local image bank files
 */
export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const filePath = url.searchParams.get("path") || "";

  if (!filePath || filePath.includes("..")) {
    return new NextResponse("Not found", { status: 404 });
  }

  const fullPath = path.join(LOCAL_BANK_DIR, filePath);
  if (!fs.existsSync(fullPath)) {
    return new NextResponse("Not found", { status: 404 });
  }

  const buffer = fs.readFileSync(fullPath);
  const ext = path.extname(fullPath).toLowerCase();
  const contentType = ext === ".png" ? "image/png" : "image/jpeg";

  return new NextResponse(buffer, {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=31536000",
    },
  });
}
