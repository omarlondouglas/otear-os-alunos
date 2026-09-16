"use client";

import * as React from "react";
import { Dashboard } from "@/components/dashboard";
import { Office3DPanel } from "@/components/office3d-panel";
import { createClient } from "@/lib/supabase-browser";
import { LogOut, Monitor, Zap } from "lucide-react";

interface SaasDashboardProps {
  onReset: () => void;
}

export function SaasDashboard({ onReset }: SaasDashboardProps) {
  const [showOffice, setShowOffice] = React.useState(false);
  const [tenantInfo, setTenantInfo] = React.useState<{
    name: string;
    plan: string;
    runsUsed: number;
    runsLimit: number;
  } | null>(null);

  React.useEffect(() => {
    async function loadTenantInfo() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: membership } = await supabase
        .from("tenant_members")
        .select("role, tenants(name, plan, runs_used, runs_limit)")
        .eq("user_id", user.id)
        .limit(1)
        .maybeSingle();

      if (membership?.tenants) {
        const t = membership.tenants as any;
        setTenantInfo({
          name: t.name,
          plan: t.plan,
          runsUsed: t.runs_used,
          runsLimit: t.runs_limit,
        });
      }
    }
    loadTenantInfo();
  }, []);

  async function handleLogout() {
    const supabase = createClient();
    await supabase.auth.signOut();
    window.location.href = "/login";
  }

  return (
    <div className="min-h-dvh flex flex-col">
      {/* Top bar - tenant info + controls */}
      <header className="flex items-center justify-between px-4 h-10 border-b border-surface-border bg-card shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-muted-foreground">
            {tenantInfo?.name || ""}
          </span>
          {tenantInfo && (
            <>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface border border-surface-border text-muted-foreground">
                {tenantInfo.plan === "pro" ? "Pro" : tenantInfo.plan === "starter" ? "Starter" : "Free"}
                {tenantInfo.plan !== "pro" && ` ${tenantInfo.runsUsed}/${tenantInfo.runsLimit}`}
              </span>
              {tenantInfo.plan !== "pro" && tenantInfo.runsUsed >= tenantInfo.runsLimit && (
                <a href="/upgrade" className="flex items-center gap-1 text-[10px] text-neon hover:underline">
                  <Zap className="w-3 h-3" /> Upgrade
                </a>
              )}
            </>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowOffice(!showOffice)}
            className={`flex items-center gap-1 px-2 py-1 rounded text-[10px] transition ${
              showOffice
                ? "bg-neon/10 text-neon border border-neon/30"
                : "text-muted-foreground hover:text-foreground hover:bg-surface"
            }`}
          >
            <Monitor className="w-3 h-3" />
            Escritorio 3D
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1 px-2 py-1 rounded text-[10px] text-muted-foreground hover:text-foreground hover:bg-surface transition"
          >
            <LogOut className="w-3 h-3" />
          </button>
        </div>
      </header>

      {/* 3D Office panel (overlay) */}
      {showOffice && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-6" onClick={() => setShowOffice(false)}>
          <div className="w-full max-w-5xl h-[85vh] rounded-xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <Office3DPanel className="w-full h-full" />
          </div>
        </div>
      )}

      {/* Dashboard - full width */}
      <div className="flex-1">
        <Dashboard onReset={onReset} />
      </div>
    </div>
  );
}
