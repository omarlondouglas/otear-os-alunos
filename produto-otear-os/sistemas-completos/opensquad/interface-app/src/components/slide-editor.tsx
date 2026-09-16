"use client";

import * as React from "react";
import { X, Save, Loader2, Check, Image, Upload, Trash2 } from "lucide-react";

type ElementType = "tag" | "stat" | "headline" | "sub" | "body" | "list" | "cta" | "spacer" | "swipe";
type Theme = "dark" | "light" | "accent" | "black";

interface SlideElement {
  type: ElementType;
  text?: string;
  items?: string[];
  x?: number;
  y?: number;
  w?: number;
  fontSize?: number;
  color?: string;
  align?: "left" | "center" | "right";
}

interface SlideData {
  id: number;
  theme: Theme;
  imageFile?: string | null;
  elements: SlideElement[];
}

interface SlideEditorProps {
  runId: string;
  onClose: () => void;
  onSaved: (slides: { type: "image" | "html"; url: string; name: string }[]) => void;
}

const THEMES: { id: Theme; label: string; bg: string; text: string }[] = [
  { id: "dark",   label: "Dark",   bg: "#0a0a0a", text: "#fff"     },
  { id: "light",  label: "Light",  bg: "#F5F5F0", text: "#0a0a0a"  },
  { id: "accent", label: "Verde",  bg: "#A3F12E", text: "#0a0a0a"  },
  { id: "black",  label: "Black",  bg: "#000000", text: "#fff"     },
];

const ELEMENT_LABELS: Record<ElementType, string> = {
  tag:     "Tag (label do topo)",
  stat:    "Stat (numero em destaque)",
  headline:"Headline (titulo principal)",
  sub:     "Sub (subtitulo)",
  body:    "Texto corrido",
  list:    "Lista de itens",
  cta:     "CTA (chamada p/ acao)",
  spacer:  "Espaco",
  swipe:   "Swipe hint",
};

// Strip HTML tags for clean display in input fields
function stripHtml(html: string): string {
  return html
    .replace(/<[^>]*>/g, "")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&nbsp;/g, " ")
    .trim();
}

// Render text with <em> highlights (BrandsDecoded neon green effect)
function RichText({ text, theme, scale: s }: { text: string; theme: Theme; scale: number }) {
  const emBg = theme === "accent" ? "#0a0a0a" : "#A3F12E";
  const emColor = theme === "accent" ? "#A3F12E" : "#0a0a0a";
  const parts = text.split(/(<em>.*?<\/em>|<strong>.*?<\/strong>)/g);
  return (
    <>
      {parts.map((part, i) => {
        const emMatch = part.match(/^<em>(.*?)<\/em>$/);
        if (emMatch) {
          return (
            <span key={i} style={{
              background: emBg, color: emColor,
              padding: `0 ${3 * s}px ${1.5 * s}px`,
              fontStyle: "normal",
            }}>
              {emMatch[1]}
            </span>
          );
        }
        const strongMatch = part.match(/^<strong>(.*?)<\/strong>$/);
        if (strongMatch) {
          return <strong key={i} style={{ fontWeight: 900 }}>{strongMatch[1]}</strong>;
        }
        return <span key={i}>{stripHtml(part)}</span>;
      })}
    </>
  );
}

// Theme-aware accent color
function accentColor(theme: Theme): string {
  return theme === "accent" || theme === "light" ? "#0a0a0a" : "#A3F12E";
}

// Theme-aware text colors
function headerColor(theme: Theme): string {
  return theme === "dark" || theme === "black"
    ? "rgba(255,255,255,0.4)"
    : "rgba(0,0,0,0.4)";
}

// Slide coordinate system
const SLIDE_W = 1080;
const SLIDE_H = 1440;
const CANVAS_W = 360;
const SCALE = CANVAS_W / SLIDE_W;
const CANVAS_H = Math.round(SLIDE_H * SCALE);

// Default positions per element type (in slide coords 1080x1440)
const DEFAULTS: Record<ElementType, { x: number; y: number; w: number; fontSize: number; color: string; align: "left" | "center" | "right" }> = {
  tag:     { x: 60,  y: 196,  w: 320, fontSize: 22,  color: "#A3F12E",               align: "left"   },
  stat:    { x: 60,  y: 420,  w: 800, fontSize: 160, color: "#A3F12E",               align: "left"   },
  headline:{ x: 60,  y: 320,  w: 960, fontSize: 72,  color: "#ffffff",               align: "left"   },
  sub:     { x: 60,  y: 680,  w: 960, fontSize: 44,  color: "rgba(255,255,255,0.75)", align: "left"  },
  body:    { x: 60,  y: 760,  w: 960, fontSize: 34,  color: "rgba(255,255,255,0.7)",  align: "left"  },
  list:    { x: 60,  y: 700,  w: 900, fontSize: 34,  color: "rgba(255,255,255,0.85)", align: "left"  },
  cta:     { x: 60,  y: 1180, w: 960, fontSize: 38,  color: "#ffffff",               align: "center" },
  spacer:  { x: 0,   y: 0,   w: 0,   fontSize: 0,   color: "transparent",            align: "left"   },
  swipe:   { x: 60,  y: 1360, w: 960, fontSize: 26,  color: "rgba(255,255,255,0.35)", align: "center"},
};

const THEME_BG: Record<Theme, string> = {
  dark:   "#0a0a0a",
  light:  "#F5F5F0",
  accent: "#A3F12E",
  black:  "#000000",
};

function getElValue<K extends keyof typeof DEFAULTS[ElementType]>(
  el: SlideElement,
  key: K
): (typeof DEFAULTS)[ElementType][K] {
  const def = DEFAULTS[el.type];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return (el as any)[key] ?? def[key];
}

// Canvas component — BrandsDecoded-faithful slide editor
function SlideCanvas({
  slide,
  selectedElIdx,
  onSelectEl,
  onUpdateEl,
}: {
  slide: SlideData;
  selectedElIdx: number;
  onSelectEl: (idx: number) => void;
  onUpdateEl: (idx: number, patch: Partial<SlideElement>) => void;
}) {
  const S = SCALE; // shorthand
  const dragRef = React.useRef<{
    elIdx: number;
    startX: number;
    startY: number;
    origX: number;
    origY: number;
  } | null>(null);

  const bg = THEME_BG[slide.theme] ?? "#0a0a0a";
  const accent = accentColor(slide.theme);
  const hdrColor = headerColor(slide.theme);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!dragRef.current) return;
    const { elIdx, startX, startY, origX, origY } = dragRef.current;
    const dx = (e.clientX - startX) / S;
    const dy = (e.clientY - startY) / S;
    onUpdateEl(elIdx, {
      x: Math.round(origX + dx),
      y: Math.round(origY + dy),
    });
  };

  const handleMouseUp = () => { dragRef.current = null; };

  const clickedElRef = React.useRef(false);

  const mkDown = (i: number, el: SlideElement) => (e: React.MouseEvent) => {
    e.stopPropagation();
    clickedElRef.current = true;
    onSelectEl(i);
    const def = DEFAULTS[el.type];
    dragRef.current = {
      elIdx: i,
      startX: e.clientX, startY: e.clientY,
      origX: el.x ?? def.x, origY: el.y ?? def.y,
    };
  };

  const selOutline = (i: number): string =>
    i === selectedElIdx ? "2px dashed #ff6a00" : "none";

  return (
    <>
      {/* Urbanist font */}
      {/* eslint-disable-next-line @next/next/no-css-tags */}
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Urbanist:wght@300;400;500;600;700;800;900&display=swap"
      />
      <div
        className="relative select-none"
        style={{
          width: CANVAS_W,
          height: CANVAS_H,
          backgroundColor: bg,
          borderRadius: 8,
          overflow: "hidden",
          flexShrink: 0,
          fontFamily: "'Urbanist', sans-serif",
          ...(slide.imageFile ? {
            backgroundImage: `url(${slide.imageFile})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          } : {}),
        }}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onClick={() => {
          if (clickedElRef.current) {
            clickedElRef.current = false;
            return;
          }
          onSelectEl(-1);
        }}
      >
        {/* Dark overlay on image backgrounds for text readability */}
        {slide.imageFile && (
          <div style={{
            position: "absolute", inset: 0,
            background: "linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 100%)",
            zIndex: 0,
          }} />
        )}
        {/* Header bar — fixed (not draggable) */}
        <div
          style={{
            position: "absolute",
            top: 0, left: 0, right: 0,
            display: "flex", justifyContent: "space-between", alignItems: "center",
            padding: `${24 * S}px ${24 * S}px`,
            fontSize: 22 * S,
            fontWeight: 500,
            color: hdrColor,
            letterSpacing: "0.01em",
            zIndex: 1,
          }}
        >
          <span>Powered by Tear</span>
          <span>@marlonlima.ia</span>
          <span>2026 //</span>
        </div>

        {/* Elements */}
        {slide.elements.map((el, i) => {
          if (el.type === "spacer") return null;
          const def = DEFAULTS[el.type];
          const x = (el.x ?? def.x) * S;
          const y = (el.y ?? def.y) * S;
          const w = (el.w ?? def.w) * S;
          const fs = (el.fontSize ?? def.fontSize) * S;
          const color = el.color ?? def.color;
          const align = el.align ?? def.align;

          const base: React.CSSProperties = {
            position: "absolute", left: x, top: y, width: w,
            fontSize: fs, color, textAlign: align,
            cursor: "move", userSelect: "none",
            outline: selOutline(i),
            outlineOffset: 2,
            boxSizing: "border-box",
            lineHeight: 1.1,
            fontFamily: "'Urbanist', sans-serif",
            zIndex: 1,
          };

          // --- TAG (pill) ---
          if (el.type === "tag") {
            const tagBg = slide.theme === "accent" ? "#0a0a0a" : "#A3F12E";
            const tagColor = slide.theme === "accent" ? "#A3F12E" : "#0a0a0a";
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base,
                background: tagBg, color: tagColor,
                fontWeight: 700, textTransform: "uppercase",
                letterSpacing: "0.08em",
                padding: `${3.3 * S}px ${7.3 * S}px`,
                borderRadius: 8 * S,
                display: "inline-block",
                width: "auto", maxWidth: w,
              }}>
                {stripHtml(el.text || "TAG")}
              </div>
            );
          }

          // --- STAT (big number) ---
          if (el.type === "stat") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, color: accent,
                fontWeight: 800, letterSpacing: "-0.05em", lineHeight: 0.88,
              }}>
                <RichText text={el.text || ""} theme={slide.theme} scale={S} />
              </div>
            );
          }

          // --- HEADLINE ---
          if (el.type === "headline") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.05,
              }}>
                <RichText text={el.text || ""} theme={slide.theme} scale={S} />
              </div>
            );
          }

          // --- SUB ---
          if (el.type === "sub") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, fontWeight: 600, letterSpacing: "-0.02em",
                lineHeight: 1.2, opacity: 0.75,
              }}>
                {stripHtml(el.text || "")}
              </div>
            );
          }

          // --- BODY ---
          if (el.type === "body") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, fontWeight: 500, letterSpacing: "-0.01em",
                lineHeight: 1.55, opacity: 0.75,
              }}>
                <RichText text={el.text || ""} theme={slide.theme} scale={S} />
              </div>
            );
          }

          // --- LIST ---
          if (el.type === "list") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, fontWeight: 500, lineHeight: 1.3,
                display: "flex", flexDirection: "column", gap: 8 * S,
              }}>
                {(el.items || []).map((item, j) => (
                  <div key={j} style={{ display: "flex", gap: 6.6 * S, alignItems: "flex-start" }}>
                    <span style={{ color: accent, fontWeight: 800, flexShrink: 0 }}>→</span>
                    <span>{stripHtml(item)}</span>
                  </div>
                ))}
              </div>
            );
          }

          // --- CTA ---
          if (el.type === "cta") {
            const ctaBorder = slide.theme === "accent" ? "rgba(0,0,0,0.5)" : "#A3F12E";
            const ctaBg = slide.theme === "accent" ? "rgba(0,0,0,0.12)" : "rgba(163,241,46,0.1)";
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base,
                background: ctaBg,
                border: `${2 * S}px solid ${ctaBorder}`,
                borderRadius: 20 * S,
                padding: `${14.6 * S}px ${17.3 * S}px`,
                fontWeight: 700, lineHeight: 1.3,
                textAlign: "center",
              }}>
                <RichText text={el.text || ""} theme={slide.theme} scale={S} />
              </div>
            );
          }

          // --- SWIPE ---
          if (el.type === "swipe") {
            return (
              <div key={i} onMouseDown={mkDown(i, el)} style={{
                ...base, fontWeight: 600, opacity: 0.35,
                textAlign: "center", letterSpacing: "0.02em",
              }}>
                deslize →
              </div>
            );
          }

          return null;
        })}
      </div>
    </>
  );
}

interface BankImage {
  url: string;
  description: string;
  tags: string[];
  categoria: string;
}

export function SlideEditor({ runId, onClose, onSaved }: SlideEditorProps) {
  const effectiveRunId = runId || "latest";

  const [slides, setSlides] = React.useState<SlideData[]>([]);
  const [selectedSlideIdx, setSelectedSlideIdx] = React.useState(0);
  const [selectedElIdx, setSelectedElIdx] = React.useState(-1);
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  // Image bank state
  const [showImageBank, setShowImageBank] = React.useState(false);
  const [bankImages, setBankImages] = React.useState<BankImage[]>([]);
  const [bankLoading, setBankLoading] = React.useState(false);
  const [bankCategory, setBankCategory] = React.useState("");
  const [uploading, setUploading] = React.useState(false);

  // Load slides on mount
  React.useEffect(() => {
    fetch(`/api/slides-editor?runId=${encodeURIComponent(effectiveRunId)}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.slides) setSlides(data.slides);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [effectiveRunId]);

  const selectedSlide = slides[selectedSlideIdx];

  const updateTheme = (theme: Theme) => {
    setSaved(false);
    setSlides((prev) =>
      prev.map((s, si) => si === selectedSlideIdx ? { ...s, theme } : s)
    );
  };

  const updateElement = (elIdx: number, patch: Partial<SlideElement>) => {
    setSaved(false);
    setSlides((prev) =>
      prev.map((s, si) => {
        if (si !== selectedSlideIdx) return s;
        return {
          ...s,
          elements: s.elements.map((el, ei) =>
            ei === elIdx ? { ...el, ...patch } : el
          ),
        };
      })
    );
  };

  const updateListItem = (elIdx: number, itemIdx: number, value: string) => {
    setSaved(false);
    setSlides((prev) =>
      prev.map((s, si) => {
        if (si !== selectedSlideIdx) return s;
        return {
          ...s,
          elements: s.elements.map((el, ei) => {
            if (ei !== elIdx) return el;
            const items = [...(el.items || [])];
            items[itemIdx] = value;
            return { ...el, items };
          }),
        };
      })
    );
  };

  const setSlideImage = (imageFile: string | null) => {
    setSaved(false);
    setSlides((prev) =>
      prev.map((s, si) =>
        si === selectedSlideIdx
          ? { ...s, imageFile, theme: imageFile ? "black" : s.theme === "black" ? "dark" : s.theme }
          : s
      )
    );
  };

  const loadBankImages = async (cat?: string) => {
    setBankLoading(true);
    try {
      const q = cat ? `?categoria=${cat}&limit=50` : "?limit=50";
      const res = await fetch(`/api/image-bank${q}`);
      const data = await res.json();
      setBankImages(data.images || []);
    } catch { setBankImages([]); }
    setBankLoading(false);
  };

  const handleOpenBank = () => {
    setShowImageBank(true);
    loadBankImages(bankCategory || undefined);
  };

  const handleUploadImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);

    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result as string;

      // Save to bank
      try {
        const res = await fetch("/api/image-bank", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            imageBase64: base64,
            description: file.name.replace(/\.[^.]+$/, ""),
            tags: [],
            categoria: "upload",
          }),
        });
        const data = await res.json();
        if (data.ok) {
          const url = data.urlPublica || data.url;
          setSlideImage(url);
          // Refresh bank
          if (showImageBank) loadBankImages(bankCategory || undefined);
        }
      } catch { /* ignore */ }

      setUploading(false);
    };
    reader.readAsDataURL(file);
    // Reset input
    e.target.value = "";
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`/api/slides-editor?runId=${encodeURIComponent(effectiveRunId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slides, runId: effectiveRunId }),
      });
      const data = await res.json();
      if (data.ok) {
        setSaved(true);
        onSaved(data.slides || []);
      }
    } catch { /* ignore */ }
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(5,5,5,0.95)]">
        <Loader2 className="w-8 h-8 text-[#ff6a00] animate-spin" />
      </div>
    );
  }

  if (!slides.length) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(5,5,5,0.95)]">
        <div className="text-center">
          <p className="text-[#626262] mb-4">slides-data.json nao encontrado</p>
          <button onClick={onClose} className="text-sm text-[#ff6a00] hover:underline">Fechar</button>
        </div>
      </div>
    );
  }

  const selectedEl = selectedSlide?.elements[selectedElIdx];
  const showProps = selectedElIdx >= 0 && selectedEl && selectedEl.type !== "spacer" && selectedEl.type !== "swipe";

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#050505]">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(255,255,255,0.07)] shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 bg-[#ff6a00] rounded-[8px] flex items-center justify-center text-black font-black text-xs">
            E
          </div>
          <span className="font-bold tracking-[-0.03em]">Editor de Carrossel</span>
          <span className="text-xs text-[#626262]">{slides.length} slides</span>
          {effectiveRunId !== "latest" && (
            <span className="text-xs text-[#8e8e8e] font-mono bg-[#141414] px-2 py-0.5 rounded-[6px]">
              {effectiveRunId}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className={`flex items-center gap-2 px-5 h-9 rounded-[12px] font-bold text-sm transition-all ${
              saved
                ? "bg-[#217a28]/20 border border-[#217a28]/40 text-[#8cff2e]"
                : "bg-[#ff6a00] text-black hover:bg-[#e05e00]"
            } disabled:opacity-50`}
          >
            {saving ? (
              <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Renderizando...</>
            ) : saved ? (
              <><Check className="w-3.5 h-3.5" /> Salvo</>
            ) : (
              <><Save className="w-3.5 h-3.5" /> Salvar</>
            )}
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded-[10px] text-[#626262] hover:text-white hover:bg-[#141414] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Body: 3 columns */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: slide thumbnails (180px) */}
        <div className="w-[180px] border-r border-[rgba(255,255,255,0.06)] overflow-y-auto shrink-0 p-3 space-y-2">
          {slides.map((slide, i) => {
            const theme = THEMES.find((t) => t.id === slide.theme) ?? THEMES[0];
            const headline = stripHtml(slide.elements.find((e) => e.type === "headline")?.text || `Slide ${slide.id}`);
            return (
              <button
                key={slide.id}
                onClick={() => { setSelectedSlideIdx(i); setSelectedElIdx(-1); }}
                className={`w-full text-left rounded-[10px] border overflow-hidden transition-all ${
                  selectedSlideIdx === i
                    ? "border-[#ff6a00]/60 ring-1 ring-[#ff6a00]/30"
                    : "border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.15)]"
                }`}
              >
                <div
                  className="w-full aspect-[3/4] flex flex-col justify-between p-2"
                  style={{ backgroundColor: theme.bg, color: theme.text }}
                >
                  <span className="text-[8px] opacity-50 font-bold">{slide.id}</span>
                  <p className="text-[9px] font-bold leading-tight line-clamp-3">{headline}</p>
                </div>
                <div className="px-2 py-1.5 bg-[#0d0d0d]">
                  <p className="text-[9px] text-[#626262] truncate">
                    {slide.elements.filter((e) => e.type !== "spacer" && e.type !== "swipe").length} elementos
                  </p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Center: canvas */}
        <div className="flex-1 flex flex-col items-center justify-center p-8 overflow-auto bg-[#080808]">
          <div className="text-xs text-[#626262] mb-4 font-mono">
            Slide {selectedSlideIdx + 1}/{slides.length}
            {selectedElIdx >= 0 && selectedEl && (
              <span className="ml-3 text-[#ff6a00]/70">
                {ELEMENT_LABELS[selectedEl.type]}
              </span>
            )}
          </div>
          {selectedSlide && (
            <SlideCanvas
              slide={selectedSlide}
              selectedElIdx={selectedElIdx}
              onSelectEl={setSelectedElIdx}
              onUpdateEl={updateElement}
            />
          )}
          <p className="text-[10px] text-[#3d3d3d] mt-4">
            Clique para selecionar · Arraste para reposicionar
          </p>
        </div>

        {/* Right: properties panel (320px) */}
        <div className="w-[320px] border-l border-[rgba(255,255,255,0.06)] overflow-y-auto shrink-0 p-5 space-y-5">
          {/* Theme selector — always visible */}
          {selectedSlide && (
            <div>
              <p className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#8e8e8e] mb-2">Fundo do slide</p>
              <div className="grid grid-cols-4 gap-1.5">
                {THEMES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => updateTheme(t.id)}
                    className={`flex flex-col items-center gap-1 p-2 rounded-[10px] border text-[9px] font-bold transition-all ${
                      selectedSlide.theme === t.id
                        ? "border-[#ff6a00]/60 bg-[#ff6a00]/10 text-[#ff6a00]"
                        : "border-[rgba(255,255,255,0.06)] text-[#626262] hover:border-[rgba(255,255,255,0.15)]"
                    }`}
                  >
                    <div className="w-6 h-6 rounded-[5px] border border-[rgba(255,255,255,0.1)]" style={{ backgroundColor: t.bg }} />
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Image selector — always visible when slide selected */}
          {selectedSlide && (
            <div>
              <p className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#8e8e8e] mb-2">Imagem de fundo</p>

              {selectedSlide.imageFile ? (
                <div className="space-y-2">
                  <div className="relative rounded-[10px] overflow-hidden border border-[rgba(255,255,255,0.1)]">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={selectedSlide.imageFile}
                      alt="Fundo do slide"
                      className="w-full h-24 object-cover"
                    />
                  </div>
                  <div className="flex gap-1.5">
                    <button
                      onClick={handleOpenBank}
                      className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-[10px] border border-[rgba(255,255,255,0.07)] text-[10px] font-semibold text-[#8e8e8e] hover:border-[#ff6a00]/40 hover:text-[#ff6a00] transition-all"
                    >
                      <Image className="w-3 h-3" /> Trocar
                    </button>
                    <button
                      onClick={() => setSlideImage(null)}
                      className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-[10px] border border-[rgba(255,255,255,0.07)] text-[10px] font-semibold text-[#626262] hover:border-red-500/40 hover:text-red-400 transition-all"
                    >
                      <Trash2 className="w-3 h-3" /> Remover
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-1.5">
                  <button
                    onClick={handleOpenBank}
                    className="flex-1 flex items-center justify-center gap-1.5 h-10 rounded-[10px] border border-dashed border-[rgba(255,255,255,0.12)] text-[10px] font-semibold text-[#626262] hover:border-[#ff6a00]/40 hover:text-[#ff6a00] transition-all"
                  >
                    <Image className="w-3.5 h-3.5" /> Banco de imagens
                  </button>
                  <label className="flex items-center justify-center gap-1.5 px-3 h-10 rounded-[10px] border border-dashed border-[rgba(255,255,255,0.12)] text-[10px] font-semibold text-[#626262] hover:border-[#ff6a00]/40 hover:text-[#ff6a00] transition-all cursor-pointer">
                    {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
                    Upload
                    <input
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleUploadImage}
                      className="hidden"
                    />
                  </label>
                </div>
              )}
            </div>
          )}

          {selectedSlide && <div className="h-px bg-[rgba(255,255,255,0.05)]" />}

          {!showProps && (
            <div className="text-center py-8 text-[#3d3d3d]">
              <p className="text-sm">Selecione um elemento no canvas</p>
              <p className="text-xs mt-1">para editar suas propriedades</p>
            </div>
          )}

          {showProps && selectedEl && (
            <>
              <p className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#8e8e8e]">
                {ELEMENT_LABELS[selectedEl.type]}
              </p>

              {/* Text content */}
              {selectedEl.type !== "list" && (
                <div className="space-y-1.5">
                  <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                    Texto
                  </label>
                  <textarea
                    value={stripHtml(selectedEl.text || "")}
                    rows={3}
                    onChange={(e) => updateElement(selectedElIdx, { text: e.target.value })}
                    className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 focus:border-[rgba(255,106,0,0.5)] transition-colors resize-none leading-relaxed"
                    placeholder={`Texto do ${selectedEl.type}...`}
                  />
                </div>
              )}

              {/* List items */}
              {selectedEl.type === "list" && (
                <div className="space-y-1.5">
                  <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                    Itens da lista
                  </label>
                  <div className="space-y-1.5">
                    {(selectedEl.items || []).map((item, itemIdx) => (
                      <input
                        key={itemIdx}
                        value={stripHtml(item)}
                        onChange={(e) => updateListItem(selectedElIdx, itemIdx, e.target.value)}
                        className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 focus:border-[rgba(255,106,0,0.5)] transition-colors"
                        placeholder={`Item ${itemIdx + 1}`}
                      />
                    ))}
                  </div>
                </div>
              )}

              <div className="h-px bg-[rgba(255,255,255,0.05)]" />

              {/* Position */}
              <div className="space-y-1.5">
                <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                  Posicao (coords slide)
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-[9px] text-[#626262] mb-1 block">X</span>
                    <input
                      type="number"
                      value={getElValue(selectedEl, "x") as number}
                      onChange={(e) => updateElement(selectedElIdx, { x: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 transition-colors"
                    />
                  </div>
                  <div>
                    <span className="text-[9px] text-[#626262] mb-1 block">Y</span>
                    <input
                      type="number"
                      value={getElValue(selectedEl, "y") as number}
                      onChange={(e) => updateElement(selectedElIdx, { y: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Size */}
              <div className="space-y-1.5">
                <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                  Tamanho
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-[9px] text-[#626262] mb-1 block">Largura (W)</span>
                    <input
                      type="number"
                      value={getElValue(selectedEl, "w") as number}
                      onChange={(e) => updateElement(selectedElIdx, { w: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 transition-colors"
                    />
                  </div>
                  <div>
                    <span className="text-[9px] text-[#626262] mb-1 block">Fonte (px)</span>
                    <input
                      type="number"
                      value={getElValue(selectedEl, "fontSize") as number}
                      onChange={(e) => updateElement(selectedElIdx, { fontSize: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Color */}
              <div className="space-y-1.5">
                <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                  Cor do texto
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={(() => {
                      const c = getElValue(selectedEl, "color") as string;
                      // Convert rgba to hex approx for the color picker
                      if (c.startsWith("#")) return c;
                      return "#ffffff";
                    })()}
                    onChange={(e) => updateElement(selectedElIdx, { color: e.target.value })}
                    className="w-10 h-10 rounded-[8px] border border-[rgba(255,255,255,0.1)] bg-transparent cursor-pointer"
                  />
                  <input
                    type="text"
                    value={getElValue(selectedEl, "color") as string}
                    onChange={(e) => updateElement(selectedElIdx, { color: e.target.value })}
                    className="flex-1 px-3 py-2 rounded-[10px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.07)] text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-[#ff6a00]/40 transition-colors font-mono"
                    placeholder="#ffffff"
                  />
                </div>
              </div>

              {/* Align */}
              <div className="space-y-1.5">
                <label className="block text-[10px] text-[#8e8e8e] font-semibold uppercase tracking-[0.04em]">
                  Alinhamento
                </label>
                <div className="flex gap-1.5">
                  {(["left", "center", "right"] as const).map((a) => {
                    const cur = getElValue(selectedEl, "align") as string;
                    return (
                      <button
                        key={a}
                        onClick={() => updateElement(selectedElIdx, { align: a })}
                        className={`flex-1 py-2 rounded-[10px] border text-xs font-semibold transition-all ${
                          cur === a
                            ? "border-[#ff6a00]/60 bg-[#ff6a00]/10 text-[#ff6a00]"
                            : "border-[rgba(255,255,255,0.07)] text-[#626262] hover:border-[rgba(255,255,255,0.2)]"
                        }`}
                      >
                        {a === "left" ? "Esq" : a === "center" ? "Centro" : "Dir"}
                      </button>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Image Bank Modal */}
      {showImageBank && (
        <div
          className="fixed inset-0 z-[60] bg-black/70 flex items-center justify-center p-6"
          onClick={() => setShowImageBank(false)}
        >
          <div
            className="w-full max-w-3xl max-h-[80vh] bg-[#0d0d0d] rounded-[16px] border border-[rgba(255,255,255,0.08)] flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-[rgba(255,255,255,0.06)] shrink-0">
              <div className="flex items-center gap-3">
                <Image className="w-4 h-4 text-[#ff6a00]" />
                <span className="font-bold text-sm">Banco de Imagens</span>
                <span className="text-xs text-[#626262]">{bankImages.length} imagens</span>
              </div>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] border border-[rgba(255,255,255,0.1)] text-[10px] font-semibold text-[#8e8e8e] hover:border-[#ff6a00]/40 hover:text-[#ff6a00] transition-all cursor-pointer">
                  {uploading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Upload className="w-3 h-3" />}
                  Upload
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleUploadImage}
                    className="hidden"
                  />
                </label>
                <button
                  onClick={() => setShowImageBank(false)}
                  className="p-1.5 rounded-[8px] text-[#626262] hover:text-white hover:bg-[#1a1a1a] transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Category filter */}
            <div className="flex gap-1.5 px-5 py-3 border-b border-[rgba(255,255,255,0.04)] shrink-0 overflow-x-auto">
              {["", "ia", "negocios", "marketing", "tecnologia", "upload", "geral"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => { setBankCategory(cat); loadBankImages(cat || undefined); }}
                  className={`px-3 py-1.5 rounded-full text-[10px] font-semibold whitespace-nowrap transition-all ${
                    bankCategory === cat
                      ? "bg-[#ff6a00]/15 text-[#ff6a00] border border-[#ff6a00]/30"
                      : "text-[#626262] border border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.15)]"
                  }`}
                >
                  {cat || "Todas"}
                </button>
              ))}
            </div>

            {/* Image grid */}
            <div className="flex-1 overflow-y-auto p-5">
              {bankLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-6 h-6 text-[#ff6a00] animate-spin" />
                </div>
              ) : bankImages.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-[#626262] text-sm mb-2">Nenhuma imagem encontrada</p>
                  <p className="text-[#3d3d3d] text-xs">Faca upload ou rode um squad para gerar imagens</p>
                </div>
              ) : (
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                  {bankImages.map((img, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setSlideImage(img.url);
                        setShowImageBank(false);
                      }}
                      className="group relative rounded-[10px] overflow-hidden border border-[rgba(255,255,255,0.06)] hover:border-[#ff6a00]/50 transition-all aspect-square"
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={img.url}
                        alt={img.description}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2">
                        <span className="text-[9px] text-white font-medium leading-tight line-clamp-2">
                          {img.description}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
