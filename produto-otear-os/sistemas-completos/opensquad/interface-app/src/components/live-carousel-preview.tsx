"use client";

import * as React from "react";
import { createClient } from "@/lib/supabase-browser";
import { motion, AnimatePresence } from "motion/react";
import { FileText, Image, Loader2, CheckCircle2 } from "lucide-react";

interface LiveSlide {
  num: number;
  label: string;
  text: string;
  imageUrl?: string;
  status: "pending" | "text" | "image" | "done";
}

interface LiveCarouselPreviewProps {
  isRunning: boolean;
}

export function LiveCarouselPreview({ isRunning }: LiveCarouselPreviewProps) {
  const [slides, setSlides] = React.useState<LiveSlide[]>([]);
  const [stage, setStage] = React.useState<string>("idle");
  const wsRef = React.useRef<WebSocket | null>(null);

  React.useEffect(() => {
    if (!isRunning) {
      return;
    }

    // Reset state on new run
    setSlides([]);
    setStage("pesquisando");

    async function connectWs() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: membership } = await supabase
        .from("tenant_members")
        .select("tenant_id")
        .eq("user_id", user.id)
        .limit(1)
        .maybeSingle();

      if (!membership) return;

      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      const port = process.env.NEXT_PUBLIC_WS_PORT || "3001";
      const url = `${proto}//${host}:${port}/ws/office/${membership.tenant_id}`;

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);

          // State updates -> detect pipeline stage
          if (msg.type === "state" && msg.state) {
            const agents = msg.state.agents || [];
            const working = agents.find((a: any) => a.status === "working");
            if (working) {
              const id = (working.id || working.name || "").toLowerCase();
              if (id.includes("pesquis")) setStage("pesquisando");
              else if (id.includes("estrateg")) setStage("estrategia");
              else if (id.includes("redator")) setStage("escrevendo");
              else if (id.includes("designer")) setStage("desenhando");
              else if (id.includes("curador") || id.includes("gerador") || id.includes("conceituador")) setStage("imagens");
              else if (id.includes("revisor")) setStage("revisando");
              else if (id.includes("publicador")) setStage("finalizando");
            }
          }

          // Output file updates -> populate slides
          if (msg.type === "output-file") {
            if (msg.file === "slides-data.json" && msg.path) {
              // Fetch the slides data from the API
              fetch("/api/squad-progress")
                .then((r) => r.ok ? r.json() : null)
                .then((data) => {
                  if (data?.copySlides) {
                    setSlides(
                      data.copySlides.map((s: any) => ({
                        num: s.num,
                        label: s.label,
                        text: s.text,
                        status: "text" as const,
                      }))
                    );
                  }
                  if (data?.slides?.length > 0) {
                    setSlides((prev) =>
                      prev.map((s, i) => ({
                        ...s,
                        imageUrl: data.slides[i]?.url,
                        status: data.slides[i]?.url ? "done" : s.status,
                      }))
                    );
                  }
                })
                .catch(() => {});
            }

            if (msg.file === "carousel-content.md") {
              setStage("escrevendo");
              // Fetch parsed content
              fetch("/api/squad-progress")
                .then((r) => r.ok ? r.json() : null)
                .then((data) => {
                  if (data?.copySlides) {
                    setSlides(
                      data.copySlides.map((s: any) => ({
                        num: s.num,
                        label: s.label,
                        text: s.text,
                        status: "text" as const,
                      }))
                    );
                  }
                })
                .catch(() => {});
            }
          }

          // Image output updates
          if (msg.type === "output-image") {
            setStage("imagens");
          }

          // Job completed
          if (msg.type === "job-completed") {
            setStage("concluido");
            // Final fetch to get rendered slides
            setTimeout(() => {
              fetch("/api/squad-progress")
                .then((r) => r.ok ? r.json() : null)
                .then((data) => {
                  if (data?.slides?.length > 0) {
                    setSlides((prev) =>
                      prev.map((s, i) => ({
                        ...s,
                        imageUrl: data.slides[i]?.url || s.imageUrl,
                        status: "done",
                      }))
                    );
                  }
                })
                .catch(() => {});
            }, 2000);
          }
        } catch {
          // ignore parse errors
        }
      };

      ws.onclose = () => {
        // Reconnect after 3s if still running
        if (isRunning) {
          setTimeout(connectWs, 3000);
        }
      };
    }

    connectWs();

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [isRunning]);

  // Also poll squad-progress every 8s as fallback
  React.useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      fetch("/api/squad-progress")
        .then((r) => r.ok ? r.json() : null)
        .then((data) => {
          if (data?.copySlides && data.copySlides.length > 0 && slides.length === 0) {
            setSlides(
              data.copySlides.map((s: any) => ({
                num: s.num,
                label: s.label,
                text: s.text,
                status: "text" as const,
              }))
            );
          }
          if (data?.slides?.length > 0) {
            setSlides((prev) =>
              prev.map((s, i) => ({
                ...s,
                imageUrl: data.slides[i]?.url || s.imageUrl,
                status: data.slides[i]?.url ? "done" : s.status,
              }))
            );
          }
        })
        .catch(() => {});
    }, 8000);

    return () => clearInterval(interval);
  }, [isRunning, slides.length]);

  if (!isRunning && slides.length === 0) return null;

  const STAGE_LABELS: Record<string, string> = {
    idle: "Preparando...",
    pesquisando: "Pesquisando noticias...",
    estrategia: "Definindo estrategia...",
    escrevendo: "Escrevendo copy...",
    desenhando: "Criando layout...",
    imagens: "Gerando imagens...",
    revisando: "Revisando conteudo...",
    finalizando: "Finalizando...",
    concluido: "Carrossel pronto!",
  };

  return (
    <div className="space-y-3">
      {/* Stage indicator */}
      <div className="flex items-center gap-2 px-1">
        {stage === "concluido" ? (
          <CheckCircle2 className="w-4 h-4 text-green-400" />
        ) : (
          <Loader2 className="w-4 h-4 text-neon animate-spin" />
        )}
        <span className="text-xs font-medium text-muted-foreground">
          {STAGE_LABELS[stage] || stage}
        </span>
      </div>

      {/* Slides preview */}
      {slides.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
          <AnimatePresence>
            {slides.map((slide, i) => (
              <motion.div
                key={slide.num}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1, duration: 0.3 }}
                className="shrink-0 w-28 rounded-lg overflow-hidden border border-surface-border bg-surface"
              >
                {/* Slide thumbnail */}
                <div className="aspect-[3/4] relative">
                  {slide.imageUrl ? (
                    <img
                      src={slide.imageUrl}
                      alt={`Slide ${slide.num}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center p-2 bg-card">
                      {slide.status === "pending" ? (
                        <div className="w-full h-full bg-surface-border/30 animate-pulse rounded" />
                      ) : (
                        <>
                          <FileText className="w-4 h-4 text-muted-foreground mb-1" />
                          <p className="text-[8px] text-muted-foreground text-center line-clamp-4 leading-tight">
                            {slide.text}
                          </p>
                        </>
                      )}
                    </div>
                  )}

                  {/* Status badge */}
                  <div className="absolute top-1 right-1">
                    {slide.status === "done" ? (
                      <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center">
                        <CheckCircle2 className="w-3 h-3 text-white" />
                      </div>
                    ) : slide.status === "text" ? (
                      <div className="w-4 h-4 rounded-full bg-blue-500 flex items-center justify-center">
                        <FileText className="w-2.5 h-2.5 text-white" />
                      </div>
                    ) : (
                      <div className="w-4 h-4 rounded-full bg-surface-border animate-pulse" />
                    )}
                  </div>
                </div>

                {/* Label */}
                <div className="px-1.5 py-1">
                  <p className="text-[9px] text-muted-foreground truncate">
                    {slide.label || `Slide ${slide.num}`}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Skeleton while no slides yet */}
      {slides.length === 0 && isRunning && (
        <div className="flex gap-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="shrink-0 w-28 aspect-[3/4] rounded-lg bg-surface-border/20 animate-pulse"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
