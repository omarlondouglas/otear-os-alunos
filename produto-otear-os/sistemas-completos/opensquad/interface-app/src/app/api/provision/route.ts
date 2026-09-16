import { NextRequest, NextResponse } from "next/server";
import { getUser } from "@/lib/auth";
import { createTenant } from "@/lib/provisioning";
import { supabase } from "@/lib/supabase";

export async function POST(req: NextRequest) {
  const user = await getUser();
  if (!user) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  // Check if user already has a tenant
  const { data: existing } = await supabase.client
    .from("tenant_members")
    .select("tenant_id")
    .eq("user_id", user.id)
    .limit(1)
    .maybeSingle();

  if (existing) {
    return NextResponse.json({ tenantId: existing.tenant_id });
  }

  const body = await req.json();
  const {
    agencyName,
    niche,
    instagramHandle,
    website,
    referenceProfiles,
  } = body as {
    agencyName: string;
    niche: string;
    instagramHandle?: string;
    website?: string;
    referenceProfiles?: string[];
  };

  if (!agencyName || !niche) {
    return NextResponse.json({ error: "agencyName and niche are required" }, { status: 400 });
  }

  try {
    const tenantId = await createTenant(user.id, agencyName, niche, {
      instagramHandle,
      website,
      referenceProfiles,
    });
    return NextResponse.json({ tenantId });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
