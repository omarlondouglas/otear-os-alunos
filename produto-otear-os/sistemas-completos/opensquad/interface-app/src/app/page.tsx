"use client";

import * as React from "react";
import { Onboarding } from "@/components/onboarding";
import { SaasDashboard } from "@/components/saas-dashboard";
import { createClient } from "@/lib/supabase-browser";

export default function Home() {
  const [state, setState] = React.useState<"loading" | "no-tenant" | "ready">("loading");

  React.useEffect(() => {
    async function check() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();

      if (!user) {
        // Proxy should redirect to /login, but just in case
        window.location.href = "/login";
        return;
      }

      // Check if user has a tenant (provisioned)
      const { data: membership } = await supabase
        .from("tenant_members")
        .select("tenant_id")
        .eq("user_id", user.id)
        .limit(1)
        .maybeSingle();

      if (!membership) {
        setState("no-tenant");
      } else {
        setState("ready");
      }
    }
    check();
  }, []);

  if (state === "loading") {
    return (
      <div className="min-h-dvh flex items-center justify-center">
        <div className="w-9 h-9 bg-neon rounded-lg animate-pulse" />
      </div>
    );
  }

  if (state === "no-tenant") {
    return <Onboarding onComplete={() => setState("ready")} />;
  }

  return <SaasDashboard onReset={() => setState("no-tenant")} />;
}
