"use client";

import * as React from "react";
import { createClient } from "@/lib/supabase-browser";

interface OfficePanelProps {
  className?: string;
}

export function OfficePanel({ className }: OfficePanelProps) {
  const [officeUrl, setOfficeUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    async function resolve() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: membership } = await supabase
        .from("tenant_members")
        .select("tenant_id")
        .eq("user_id", user.id)
        .limit(1)
        .maybeSingle();

      if (!membership) {
        // No tenant — load dashboard without WebSocket
        setOfficeUrl("/office/index.html");
        return;
      }

      // Build URL with tenant ID and WS port as params
      const wsPort = process.env.NEXT_PUBLIC_WS_PORT || "3001";
      setOfficeUrl(`/office/index.html?tenant=${membership.tenant_id}&wsPort=${wsPort}`);
    }
    resolve();
  }, []);

  return (
    <div className={`relative bg-[#101018] rounded-xl overflow-hidden border border-surface-border ${className || ""}`}>
      {officeUrl ? (
        <iframe
          src={officeUrl}
          className="w-full h-full border-0"
          title="OpenSquad Office"
          allow="autoplay"
        />
      ) : (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-neon/30 border-t-neon rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}
