"use client";

import * as React from "react";
import { motion } from "motion/react";
import {
  ScrollXCarousel,
  ScrollXCarouselContainer,
  ScrollXCarouselProgress,
  ScrollXCarouselWrap,
} from "@/components/ui/scroll-x-carousel";
import {
  CardHoverReveal,
  CardHoverRevealContent,
  CardHoverRevealMain,
} from "@/components/ui/reveal-on-hover";
import { Badge } from "@/components/ui/badge";
import { ImageIcon, Loader2, Download } from "lucide-react";

// Scales an HTML slide iframe to fill its container dynamically
function HtmlSlide({ url, title }: { url: string; title: string }) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [scale, setScale] = React.useState(0.25);

  React.useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver(([entry]) => {
      setScale(entry.contentRect.width / 1080);
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full overflow-hidden bg-black"
      style={{ aspectRatio: "3/4" }}
    >
      <iframe
        src={url}
        title={title}
        style={{
          width: 1080,
          height: 1440,
          transform: `scale(${scale})`,
          transformOrigin: "top left",
          border: "none",
          pointerEvents: "none",
          display: "block",
        }}
        loading="lazy"
      />
    </div>
  );
}

function downloadImage(url: string, filename: string) {
  if (url.startsWith("data:")) {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    fetch(url)
      .then((r) => r.blob())
      .then((blob) => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(a.href);
        document.body.removeChild(a);
      })
      .catch(() => window.open(url, "_blank"));
  }
}

function downloadAllSlides(slides: { url: string; slideNum: number }[]) {
  slides.forEach((slide, i) => {
    setTimeout(() => downloadImage(slide.url, `slide-${slide.slideNum}.jpg`), i * 300);
  });
}

interface Carousel {
  id: string;
  version: string;
  date: string;
  topic: string;
  slides: string[];
  slideType: "image" | "html";
}

interface CarouselShowcaseProps {
  refreshKey?: number;
  onEdit?: (carouselId: string) => void;
}

export function CarouselShowcase({ refreshKey, onEdit }: CarouselShowcaseProps) {
  const [carousels, setCarousels] = React.useState<Carousel[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchCarousels = async () => {
      setLoading(true);
      try {
        const res = await fetch("/api/carousels");
        const data = await res.json();
        setCarousels(data.carousels || []);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchCarousels();
  }, [refreshKey]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24 text-[#3d3d3d]">
        <Loader2 className="w-5 h-5 animate-spin mr-2" />
        <span className="text-sm">Carregando...</span>
      </div>
    );
  }

  // Empty state — no carousels yet
  if (carousels.length === 0) {
    return (
      <div className="px-6 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center justify-center gap-4 py-20 rounded-[20px] border border-[rgba(255,255,255,0.04)] bg-[#0d0d0d]"
        >
          <div className="w-16 h-16 rounded-[15px] bg-[#141414] border border-[rgba(255,255,255,0.06)] flex items-center justify-center">
            <ImageIcon className="w-7 h-7 text-[#262626]" />
          </div>
          <div className="text-center">
            <p className="text-sm font-semibold text-[#5e5e5e]">Nenhum carrossel gerado ainda</p>
            <p className="text-xs text-[#3d3d3d] mt-1 max-w-xs">
              Digite um tema acima e clique em Criar. Os slides aparecerão aqui quando prontos.
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  // Flatten all slides from all carousels into one list
  const allSlides = carousels.flatMap((carousel) =>
    carousel.slides.map((url, i) => ({
      url,
      slideNum: i + 1,
      total: carousel.slides.length,
      topic: carousel.topic,
      date: carousel.date,
      carouselId: carousel.id,
      slideType: carousel.slideType || "image",
    }))
  );

  return (
    <ScrollXCarousel className="h-[150vh]">
      <ScrollXCarouselContainer className="h-dvh place-content-center flex flex-col gap-8 py-12">
        {/* Side fades */}
        <div className="pointer-events-none w-[6vw] h-[103%] absolute inset-[0_auto_0_0] z-10 bg-[linear-gradient(90deg,_#050505_20%,_transparent)]" />
        <div className="pointer-events-none w-[15vw] h-[103%] absolute inset-[0_0_0_auto] z-10 bg-[linear-gradient(270deg,_#050505_35%,_transparent)]" />

        <ScrollXCarouselWrap className="flex space-x-5 [&>*:first-child]:ml-10">
          {allSlides.map((slide, i) => (
            <motion.div
              key={`${slide.carouselId}-${slide.slideNum}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <CardHoverReveal className="w-[200px] md:w-[240px] xl:w-[270px] shrink-0 shadow-xl border border-[rgba(255,255,255,0.06)] rounded-[15px]">
                <CardHoverRevealMain>
                  {slide.slideType === "html" ? (
                    <HtmlSlide url={slide.url} title={`Slide ${slide.slideNum}`} />
                  ) : (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      alt={`Slide ${slide.slideNum}`}
                      src={slide.url}
                      className="size-full aspect-[4/5] object-cover"
                      loading="lazy"
                    />
                  )}
                </CardHoverRevealMain>
                <CardHoverRevealContent className="space-y-3 rounded-[15px] bg-[rgba(5,5,5,0.85)] backdrop-blur-2xl p-5">
                  <div className="flex flex-wrap gap-2">
                    <Badge className="capitalize rounded-full bg-[#ff6a00] text-black border-0 text-[10px] font-bold">
                      Slide {slide.slideNum}/{slide.total}
                    </Badge>
                    <Badge className="capitalize rounded-full bg-[#0d0d0d] text-[#8e8e8e] border border-[rgba(255,255,255,0.1)] text-[10px]">
                      {slide.date}
                    </Badge>
                  </div>
                  {slide.topic && (
                    <div>
                      <h3 className="text-white text-sm font-semibold leading-snug line-clamp-2">
                        {slide.topic}
                      </h3>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(slide.carouselId)}
                        className="text-[10px] font-semibold px-2.5 py-1 rounded-full border border-[#ff6a00]/50 text-[#ff6a00] hover:bg-[#ff6a00]/10 transition-colors"
                      >
                        ✏ Editar
                      </button>
                    )}
                    {slide.slideType === "image" && (
                      <>
                        <button
                          onClick={(e) => { e.stopPropagation(); downloadImage(slide.url, `slide-${slide.slideNum}.jpg`); }}
                          className="flex items-center gap-1 text-[10px] font-semibold px-2.5 py-1 rounded-full border border-[rgba(255,255,255,0.15)] text-[#8e8e8e] hover:text-white hover:border-[rgba(255,255,255,0.3)] transition-colors"
                        >
                          <Download className="w-3 h-3" /> Slide
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            const carousel = carousels.find(c => c.id === slide.carouselId);
                            if (carousel) downloadAllSlides(carousel.slides.map((url, j) => ({ url, slideNum: j + 1 })));
                          }}
                          className="flex items-center gap-1 text-[10px] font-semibold px-2.5 py-1 rounded-full border border-[rgba(255,255,255,0.15)] text-[#8e8e8e] hover:text-white hover:border-[rgba(255,255,255,0.3)] transition-colors"
                        >
                          <Download className="w-3 h-3" /> Tudo ({slide.total})
                        </button>
                      </>
                    )}
                  </div>
                </CardHoverRevealContent>
              </CardHoverReveal>
            </motion.div>
          ))}
        </ScrollXCarouselWrap>

        <ScrollXCarouselProgress
          className="bg-[#0d0d0d] mx-10 h-1 rounded-full overflow-hidden"
          progressStyle="size-full bg-[#ff6a00]/70 rounded-full"
        />
      </ScrollXCarouselContainer>
    </ScrollXCarousel>
  );
}
