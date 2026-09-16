"use client";

import * as React from "react";

interface Office3DPanelProps {
  className?: string;
}

export function Office3DPanel({ className }: Office3DPanelProps) {
  return (
    <div className={`relative bg-[#0a0a0a] rounded-xl overflow-hidden border border-surface-border ${className || ""}`}>
      <iframe
        src="/office3d/index.html"
        className="w-full h-full border-0"
        title="OpenSquad 3D Office"
        allow="autoplay"
      />
    </div>
  );
}
