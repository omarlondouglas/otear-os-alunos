import { NextResponse } from "next/server";
import fs from "fs";
import { getTenantContext } from "@/lib/auth";
import { tenantStatePath } from "@/lib/tenant";

// Legacy fallback for non-tenant mode
import path from "path";
const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_STATE = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "state.json");

export async function GET() {
  // Try tenant-aware path first
  const ctx = await getTenantContext();
  const stateFile = ctx
    ? tenantStatePath(ctx.tenantId, "carousel")
    : LEGACY_STATE;

  if (!fs.existsSync(stateFile)) {
    return NextResponse.json({ state: null });
  }
  try {
    const raw = fs.readFileSync(stateFile, "utf-8");
    const state = JSON.parse(raw);
    return NextResponse.json({ state });
  } catch {
    return NextResponse.json({ state: null });
  }
}
