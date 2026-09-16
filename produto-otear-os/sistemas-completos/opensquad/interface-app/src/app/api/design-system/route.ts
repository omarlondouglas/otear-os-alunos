import { NextResponse } from "next/server";
import path from "path";
import fs from "fs";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");

export async function GET() {
  try {
    const dsPath = path.join(ROOT, "_opensquad", "_memory", "user-design-system.json");

    if (!fs.existsSync(dsPath)) {
      return NextResponse.json({ exists: false });
    }

    const content = fs.readFileSync(dsPath, "utf-8");
    const designSystem = JSON.parse(content);
    return NextResponse.json({ exists: true, designSystem });
  } catch (err) {
    console.error("[design-system GET]", err);
    return NextResponse.json({ exists: false });
  }
}
