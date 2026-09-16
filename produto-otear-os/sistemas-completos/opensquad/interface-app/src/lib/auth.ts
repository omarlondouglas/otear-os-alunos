import { createClient } from "./supabase-server";
import { supabase } from "./supabase";

export interface TenantContext {
  userId: string;
  tenantId: string;
  tenantSlug: string;
  plan: "free" | "starter" | "pro";
  runsUsed: number;
  runsLimit: number;
  role: "owner" | "admin" | "member";
}

/** Get authenticated user from Supabase Auth (server-side) */
export async function getUser() {
  const client = await createClient();
  const { data: { user } } = await client.auth.getUser();
  return user;
}

/** Get tenant context for the current authenticated user (uses service_role) */
export async function getTenantContext(): Promise<TenantContext | null> {
  try {
    const user = await getUser();
    if (!user) return null;

    const { data: membership, error } = await supabase.client
      .from("tenant_members")
      .select("tenant_id, role, tenants(id, slug, plan, runs_used, runs_limit)")
      .eq("user_id", user.id)
      .limit(1)
      .maybeSingle();

    if (error || !membership || !membership.tenants) return null;

    const t = membership.tenants as any;
    return {
      userId: user.id,
      tenantId: t.id,
      tenantSlug: t.slug,
      plan: t.plan,
      runsUsed: t.runs_used,
      runsLimit: t.runs_limit,
      role: membership.role as TenantContext["role"],
    };
  } catch {
    return null;
  }
}

/** Check if tenant can start a new run */
export function canStartRun(ctx: TenantContext): boolean {
  if (ctx.plan === "pro") return true; // ilimitado
  return ctx.runsUsed < ctx.runsLimit;
}

/** Increment runs_used for a tenant */
export async function incrementRunsUsed(tenantId: string): Promise<void> {
  await supabase.client.rpc("increment_runs_used", { p_tenant_id: tenantId });
}
