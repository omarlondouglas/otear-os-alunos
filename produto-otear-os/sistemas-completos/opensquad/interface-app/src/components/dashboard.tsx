"use client";

import * as React from "react";
import { motion, AnimatePresence } from "motion/react";
import { CarouselShowcase } from "@/components/carousel-showcase";
import { SlideEditor } from "@/components/slide-editor";
import { getOnboardingData, clearOnboardingData } from "@/lib/store";
import {
  Newspaper,
  Play,
  Loader2,
  Settings,
  Sparkles,
  Clock,
  CheckCircle2,
  Zap,
  X,
  ChevronRight,
  ChevronDown,
  Calendar,
  Terminal,
  ImageIcon,
  FileText,
  Pencil,
  Bot,
  Database,
  Ban,
} from "lucide-react";

interface DashboardProps {
  onReset: () => void;
}

interface SlideContent {
  number: number;
  label: string;
  title?: string;
  headline?: string;
  supportingText?: string;
  accentKeywords?: string;
  photo?: string;
  background?: string;
  branding?: string;
  source?: string;
}

interface CarouselContentData {
  format: string;
  slides: SlideContent[];
  caption: string;
  hashtags: string;
  runId: string;
}

type FlowPhase =
  | "idle"
  | "running-copy"
  | "done";

const PIPELINE_STEPS = [
  "Pesquisador",
  "Estrategista",
  "Redator",
  "Imagens IA",
  "Designer",
  "Revisor",
  "Publicador",
];

const PRESET_TOPICS = [
  "IA e Agentes",
  "Automacao para agencias",
  "Empreendedorismo digital",
  "Outra noticia especifica",
];

const PERIOD_OPTIONS = [
  { id: "A", label: "Ultimas 24h" },
  { id: "B", label: "Ultimos 3 dias" },
  { id: "C", label: "Ultima semana" },
];

const STEP_KEYWORDS: Record<string, number> = {
  pesquisador: 0,
  pesquisa: 0,
  research: 0,
  estrateg: 1,
  strategy: 1,
  brief: 1,
  redator: 2,
  copy: 2,
  "carousel-content": 2,
  imagem: 3,
  image: 3,
  curador: 3,
  gerador: 3,
  designer: 4,
  slide: 4,
  html: 4,
  revisor: 5,
  review: 5,
  publicador: 6,
  publicar: 6,
  finalizado: 6,
};

function detectStepFromLogs(lines: string[]): number {
  const text = lines.slice(-30).join(" ").toLowerCase();
  let detected = -1;
  for (const [kw, idx] of Object.entries(STEP_KEYWORDS)) {
    if (text.includes(kw) && idx > detected) detected = idx;
  }
  return detected;
}

export function Dashboard({ onReset }: DashboardProps) {
  const [profile, setProfile] = React.useState<ReturnType<typeof getOnboardingData>>(null);
  const [isRunning, setIsRunning] = React.useState(false);
  const [runStatus, setRunStatus] = React.useState<"idle" | "running" | "done" | "error">("idle");
  const [launchedTopic, setLaunchedTopic] = React.useState("");
  const [showLogs, setShowLogs] = React.useState(false);
  const [logs, setLogs] = React.useState<string[]>([]);
  const [activeStep, setActiveStep] = React.useState<number>(-1);
  const [completedSteps, setCompletedSteps] = React.useState<number[]>([]);
  const [elapsedSecs, setElapsedSecs] = React.useState(0);
  const [carouselRefreshKey, setCarouselRefreshKey] = React.useState(0);
  const [squadState, setSquadState] = React.useState<{
    agents: { id: string; name: string; icon: string; status: string }[];
    handoff?: { from: string; to: string; message: string };
    step?: { label: string };
  } | null>(null);

  // Content preview state
  const [carouselContent, setCarouselContent] = React.useState<CarouselContentData | null>(null);
  const [contentOpen, setContentOpen] = React.useState(false);
  const [selectedModel, setSelectedModel] = React.useState("claude-sonnet-4-6");
  const [slideUrls, setSlideUrls] = React.useState<{ url: string; type: "image" | "html" }[]>([]);

  // Flow state (single-phase)
  const [flowPhase, setFlowPhase] = React.useState<FlowPhase>("idle");
  const [imageStrategy, setImageStrategy] = React.useState<"ia" | "capa" | "banco" | "nenhuma">("capa");
  const [currentRunId, setCurrentRunId] = React.useState<string>("");

  // Wizard state
  const [wizardOpen, setWizardOpen] = React.useState(false);
  const [wizardStep, setWizardStep] = React.useState<1 | 2>(1);
  const [selectedTopic, setSelectedTopic] = React.useState("");
  const [customTopic, setCustomTopic] = React.useState("");
  const [selectedPeriod, setSelectedPeriod] = React.useState("A");

  const [editorOpen, setEditorOpen] = React.useState(false);
  const [editorRunId, setEditorRunId] = React.useState("");

  // Progressive output state
  const [progress, setProgress] = React.useState<{
    stages: { research: boolean; copy: boolean; images: boolean; slides: boolean; done: boolean };
    researchBrief: { title: string; bullets: string[] } | null;
    copySlides: { num: number; label: string; text: string }[];
    slides: { url: string; type: "image" | "html"; name: string }[];
    publishResult: string | null;
  } | null>(null);

  const startTimeRef = React.useRef<number>(0);
  const logsRef = React.useRef<HTMLDivElement>(null);
  const pollRef = React.useRef<ReturnType<typeof setInterval> | null>(null);
  const progressPollRef = React.useRef<ReturnType<typeof setInterval> | null>(null);
  const timerRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  React.useEffect(() => {
    setProfile(getOnboardingData());
    // Load last run results on mount (persists across page refreshes)
    fetch("/api/squad-progress")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => { if (data?.hasRun) setProgress(data); })
      .catch(() => {});
  }, []);

  React.useEffect(() => {
    if (isRunning || runStatus === "running" || showLogs) {
      const fetchState = async () => {
        try {
          // Fetch squad state (agents progress)
          const [logsRes, stateRes] = await Promise.all([
            fetch("/api/run-squad?logs=1&tail=100"),
            fetch("/api/squad-state"),
          ]);
          const logsData = await logsRes.json();
          const stateData = await stateRes.json();

          if (logsData.logs?.length) setLogs(logsData.logs);

          // Use state.json for real agent tracking
          if (stateData.state?.agents) {
            setSquadState(stateData.state);
            const agents: { status: string }[] = stateData.state.agents;
            const runningIdx = agents.findIndex((a) => a.status === "running");
            const lastDoneIdx = agents.reduce((acc: number, a, i) => a.status === "done" ? i : acc, -1);
            const currentIdx = runningIdx >= 0 ? runningIdx : lastDoneIdx;
            if (currentIdx >= 0) {
              setActiveStep(currentIdx);
              setCompletedSteps(
                agents.map((a, i) => ({ a, i }))
                  .filter(({ a }) => a.status === "done")
                  .map(({ i }) => i)
              );
            }
          } else if (logsData.logs?.length) {
            // Fallback: keyword detection
            const step = detectStepFromLogs(logsData.logs);
            if (step >= 0) {
              setActiveStep(step);
              setCompletedSteps(Array.from({ length: step }, (_, i) => i));
            }
          }

          if (!logsData.isRunning && isRunning) {
            const lastLog = logsData.logs?.join("\n") || "";
            const failed =
              lastLog.includes("exit code: 1") ||
              lastLog.includes("Not logged in");
            setIsRunning(false);
            setActiveStep(-1);

            if (!failed) {
              setCompletedSteps(Array.from({ length: PIPELINE_STEPS.length }, (_, i) => i));
              setCarouselRefreshKey((k) => k + 1);

              // Pipeline finished — go straight to done
              setRunStatus("done");
              setFlowPhase("done");
            } else {
              setRunStatus("error");
            }

            if (timerRef.current) clearInterval(timerRef.current);
          }
        } catch { /* ignore */ }
      };
      fetchState();
      pollRef.current = setInterval(fetchState, 3000);
      return () => { if (pollRef.current) clearInterval(pollRef.current); };
    } else {
      if (pollRef.current) clearInterval(pollRef.current);
    }
  }, [isRunning, runStatus, showLogs, flowPhase]);

  React.useEffect(() => {
    if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight;
  }, [logs]);

  // Progressive output polling — runs every 5s while pipeline is active
  React.useEffect(() => {
    const fetchProgress = async () => {
      try {
        const res = await fetch("/api/squad-progress");
        if (res.ok) {
          const data = await res.json();
          if (data.hasRun) setProgress(data);
        }
      } catch { /* ignore */ }
    };

    if (isRunning || runStatus === "running") {
      fetchProgress();
      progressPollRef.current = setInterval(fetchProgress, 5000);
    } else if (runStatus === "done") {
      fetchProgress(); // one final fetch
      if (progressPollRef.current) clearInterval(progressPollRef.current);
    } else {
      if (progressPollRef.current) clearInterval(progressPollRef.current);
    }
    return () => { if (progressPollRef.current) clearInterval(progressPollRef.current); };
  }, [isRunning, runStatus]);

  // Fetch carousel content + slides when run completes
  React.useEffect(() => {
    if (flowPhase === "done" || runStatus === "done") {
      const fetchContent = async () => {
        try {
          const res = await fetch("/api/carousel-content");
          if (res.ok) {
            const data = await res.json();
            setCarouselContent(data);
            setContentOpen(true);
          }
        } catch { /* ignore */ }
        try {
          const res = await fetch("/api/carousels");
          if (res.ok) {
            const data = await res.json();
            const latest = data.carousels?.[0];
            if (latest) {
              setSlideUrls(
                latest.slides.map((url: string) => ({
                  url,
                  type: latest.slideType || "image",
                }))
              );
            }
          }
        } catch { /* ignore */ }
      };
      fetchContent();
      setCarouselRefreshKey((k) => k + 1);
    }
  }, [flowPhase, runStatus]);

  const resolvedTopic = selectedTopic === "Outra noticia especifica" ? customTopic : selectedTopic || customTopic;

  const handleRun = async (topic: string, period: string) => {
    if (!topic.trim() || isRunning) return;

    setIsRunning(true);
    setRunStatus("running");
    setLaunchedTopic(topic.trim());
    setWizardOpen(false);
    setActiveStep(0);
    setCompletedSteps([]);
    setLogs([]);
    setElapsedSecs(0);
    setFlowPhase("running-copy");
    startTimeRef.current = Date.now();
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setElapsedSecs(Math.floor((Date.now() - startTimeRef.current) / 1000));
    }, 1000);

    try {
      const res = await fetch("/api/run-squad", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: topic.trim(), period, mode: "full", imageStrategy, model: selectedModel }),
      });

      if (res.ok) {
        const data = await res.json();
        setCurrentRunId(data.runId || "");
        setSelectedTopic("");
        setCustomTopic("");
        setSelectedPeriod("A");
      } else {
        const err = await res.json();
        if (err.error !== "Squad already running") {
          setIsRunning(false);
          setRunStatus("idle");
          setFlowPhase("idle");
        }
      }
    } catch {
      setIsRunning(false);
      setRunStatus("idle");
      setFlowPhase("idle");
    }
  };

  const handleLogout = () => {
    clearOnboardingData();
    onReset();
  };

  const openWizard = () => {
    if (isRunning) return;
    setWizardStep(1);
    setWizardOpen(true);
  };

  const handleWizardNext = () => {
    if (!resolvedTopic.trim()) return;
    setWizardStep(2);
  };

  const handleWizardConfirm = () => {
    handleRun(resolvedTopic, selectedPeriod);
  };

  const periodLabel = PERIOD_OPTIONS.find((p) => p.id === selectedPeriod)?.label || "Ultimas 24h";

  // Derived: are we in any active run state
  const isAnyRunning = flowPhase === "running-copy";

  return (
    <div className="min-h-dvh">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-[rgba(255,255,255,0.06)] bg-[rgba(5,5,5,0.85)] backdrop-blur-xl">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-neon rounded-[10px] flex items-center justify-center font-black text-[#050505] text-sm">
              O
            </div>
            <span className="font-bold text-lg tracking-[-0.03em]">
              O Tear <span className="text-neon">Carrosseis</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            {profile && (
              <span className="text-sm text-[#8e8e8e]">
                @{profile.instagramHandle}
              </span>
            )}
            <button
              onClick={handleLogout}
              className="p-2 rounded-[10px] text-[#626262] hover:text-foreground hover:bg-[#141414] transition-colors"
              title="Resetar perfil"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero / Create Section */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center gap-3 mb-4">
            <Newspaper className="w-5 h-5 text-neon" />
            <span className="text-sm font-medium text-neon uppercase tracking-[0.06em]">
              Noticias Carrossel
            </span>
          </div>

          <h1 className="text-4xl md:text-[52px] font-black tracking-[-0.04em] leading-[1em] mb-5">
            Crie seu próximo{" "}
            <span className="text-neon">carrossel</span>
          </h1>
          <p className="text-lg text-[rgba(255,255,255,0.55)] max-w-2xl mb-10 leading-[1.5em]">
            A IA pesquisa noticias, cria a estrategia, escreve o copy, gera as
            imagens e monta tudo no formato do Instagram. Tudo automatico.
          </p>

          {/* Topic Input — opens wizard on click */}
          <div className="max-w-2xl">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Sparkles className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#626262]" />
                <input
                  type="text"
                  placeholder="Sobre qual tema? (ex: agentes de IA, automacao de vendas...)"
                  value={customTopic}
                  onChange={(e) => setCustomTopic(e.target.value)}
                  onFocus={openWizard}
                  disabled={isAnyRunning}
                  readOnly
                  className="w-full h-14 pl-12 pr-4 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)] text-foreground placeholder:text-[#626262] focus:outline-none focus:ring-2 focus:ring-neon/40 focus:border-[rgba(255,106,0,0.6)] transition-colors disabled:opacity-50 cursor-pointer"
                />
              </div>
              <button
                onClick={openWizard}
                disabled={isAnyRunning}
                className="h-14 px-8 rounded-[21px] bg-neon text-[#050505] font-bold flex items-center gap-2 hover:bg-neon-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_8px_20px_rgba(255,106,0,0.25)]"
              >
                {isAnyRunning ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                {isAnyRunning ? "Criando..." : "Criar"}
              </button>
            </div>

            {/* Pipeline preview */}
            <div className="flex items-center gap-2 mt-6 flex-wrap">
              {PIPELINE_STEPS.map((step, i) => {
                const isActive = activeStep === i;
                const isDone = completedSteps.includes(i);
                return (
                  <React.Fragment key={step}>
                    <motion.div
                      animate={isActive ? { scale: [1, 1.04, 1] } : { scale: 1 }}
                      transition={isActive ? { repeat: Infinity, duration: 1.6 } : {}}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs transition-all duration-300 ${
                        isActive
                          ? "bg-[#ff6a00]/10 border-[#ff6a00]/50 text-[#ff6a00]"
                          : isDone
                          ? "bg-[#217a28]/10 border-[#217a28]/40 text-[#8cff2e]"
                          : "bg-[#0d0d0d] border-[rgba(255,255,255,0.06)] text-[#737373]"
                      }`}
                    >
                      <span
                        className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          isActive
                            ? "bg-[#ff6a00] text-black"
                            : isDone
                            ? "bg-[#217a28] text-white"
                            : "bg-[#262626] text-[#8e8e8e]"
                        }`}
                      >
                        {isDone ? "v" : i + 1}
                      </span>
                      {isActive && (
                        <span className="w-1.5 h-1.5 rounded-full bg-[#ff6a00] animate-pulse" />
                      )}
                      {step}
                    </motion.div>
                    {i < PIPELINE_STEPS.length - 1 && (
                      <div
                        className={`w-4 h-px transition-colors duration-300 ${
                          isDone || isActive ? "bg-[#ff6a00]/30" : "bg-[#262626]"
                        }`}
                      />
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>
        </motion.div>
      </section>

      {/* Wizard Modal */}
      <AnimatePresence>
        {wizardOpen && !isAnyRunning && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            style={{ background: "rgba(5,5,5,0.85)", backdropFilter: "blur(8px)" }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-lg rounded-[24px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.08)] shadow-2xl overflow-hidden"
            >
              {/* Wizard header */}
              <div className="flex items-center justify-between px-6 py-5 border-b border-[rgba(255,255,255,0.06)]">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-neon" />
                  <span className="font-bold tracking-[-0.02em]">
                    {wizardStep === 1 ? "Configurar carrossel" : "Confirmar"}
                  </span>
                  <span className="text-xs text-[#626262] ml-1">
                    {wizardStep}/2
                  </span>
                </div>
                <button
                  onClick={() => setWizardOpen(false)}
                  className="p-1.5 rounded-[8px] text-[#626262] hover:text-foreground hover:bg-[#141414] transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Step 1: Topic + Period */}
              {wizardStep === 1 && (
                <div className="px-6 py-6 space-y-6">
                  {/* Topic */}
                  <div>
                    <p className="text-sm font-semibold text-foreground mb-3">
                      Qual e o tema?
                    </p>
                    <div className="grid grid-cols-2 gap-2 mb-3">
                      {PRESET_TOPICS.map((t) => (
                        <button
                          key={t}
                          onClick={() => {
                            setSelectedTopic(t);
                            if (t !== "Outra noticia especifica") setCustomTopic("");
                          }}
                          className={`px-3 py-2.5 rounded-[12px] border text-sm font-medium text-left transition-all duration-200 ${
                            selectedTopic === t
                              ? "bg-[#ff6a00]/10 border-[#ff6a00]/60 text-[#ff6a00]"
                              : "bg-[#141414] border-[rgba(255,255,255,0.06)] text-[#c4c4c4] hover:border-[rgba(255,255,255,0.15)] hover:text-foreground"
                          }`}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                    {(selectedTopic === "Outra noticia especifica" || (!selectedTopic && true)) && (
                      <input
                        type="text"
                        autoFocus={selectedTopic === "Outra noticia especifica"}
                        placeholder={
                          selectedTopic === "Outra noticia especifica"
                            ? "Descreva a noticia especifica..."
                            : "Ou escreva um tema personalizado..."
                        }
                        value={customTopic}
                        onChange={(e) => {
                          setCustomTopic(e.target.value);
                          if (e.target.value) setSelectedTopic("");
                        }}
                        className="w-full h-11 px-4 rounded-[12px] bg-[#141414] border border-[rgba(255,255,255,0.08)] text-foreground placeholder:text-[#626262] focus:outline-none focus:ring-2 focus:ring-neon/30 focus:border-[rgba(255,106,0,0.5)] transition-colors text-sm"
                      />
                    )}
                  </div>

                  {/* Period */}
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <Calendar className="w-4 h-4 text-[#626262]" />
                      <p className="text-sm font-semibold text-foreground">
                        Qual periodo de busca?
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {PERIOD_OPTIONS.map((p) => (
                        <button
                          key={p.id}
                          onClick={() => setSelectedPeriod(p.id)}
                          className={`flex-1 py-2.5 rounded-[12px] border text-sm font-medium transition-all duration-200 ${
                            selectedPeriod === p.id
                              ? "bg-[#ff6a00]/10 border-[#ff6a00]/60 text-[#ff6a00]"
                              : "bg-[#141414] border-[rgba(255,255,255,0.06)] text-[#c4c4c4] hover:border-[rgba(255,255,255,0.15)] hover:text-foreground"
                          }`}
                        >
                          {p.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Model selector */}
                  <div>
                    <p className="text-sm font-semibold text-foreground mb-2">Modelo de IA</p>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: "claude-haiku-4-5-20251001", label: "Haiku", desc: "Rapido · ~$0.03", color: "#8cff2e" },
                        { id: "claude-sonnet-4-6",         label: "Sonnet", desc: "Padrao · ~$1.00", color: "#ff6a00" },
                        { id: "claude-opus-4-6",           label: "Opus",  desc: "Melhor · ~$3.00", color: "#a78bfa" },
                      ].map((m) => (
                        <button
                          key={m.id}
                          onClick={() => setSelectedModel(m.id)}
                          className={`flex flex-col items-start gap-0.5 px-3 py-2.5 rounded-[12px] border text-left transition-all duration-200 ${
                            selectedModel === m.id
                              ? "border-[rgba(255,255,255,0.3)] bg-[#1a1a1a]"
                              : "bg-[#141414] border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.15)]"
                          }`}
                        >
                          <span className="font-bold text-sm" style={{ color: selectedModel === m.id ? m.color : "#c4c4c4" }}>
                            {m.label}
                          </span>
                          <span className="text-[10px] text-[#626262]">{m.desc}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Image strategy selector */}
                  <div>
                    <p className="text-sm font-semibold text-foreground mb-2">Imagens</p>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { id: "capa" as const, label: "So capa", desc: "Imagem IA so na capa", color: "#ff6a00", Icon: ImageIcon },
                        { id: "ia" as const, label: "Todas com IA", desc: "Imagem em todos slides", color: "#ff6a00", Icon: Bot },
                        { id: "banco" as const, label: "Banco R2", desc: "Imagens reais", color: "#8cff2e", Icon: Database },
                        { id: "nenhuma" as const, label: "Sem imagens", desc: "Apenas texto", color: "#626262", Icon: Ban },
                      ].map((opt) => (
                        <button
                          key={opt.id}
                          onClick={() => setImageStrategy(opt.id)}
                          className={`flex flex-col items-start gap-0.5 px-3 py-2.5 rounded-[12px] border text-left transition-all duration-200 ${
                            imageStrategy === opt.id
                              ? "border-[rgba(255,255,255,0.3)] bg-[#1a1a1a]"
                              : "bg-[#141414] border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.15)]"
                          }`}
                        >
                          <span className="font-bold text-sm" style={{ color: imageStrategy === opt.id ? opt.color : "#c4c4c4" }}>
                            {opt.label}
                          </span>
                          <span className="text-[10px] text-[#626262]">{opt.desc}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Next button */}
                  <button
                    onClick={handleWizardNext}
                    disabled={!resolvedTopic.trim()}
                    className="w-full h-12 rounded-[14px] bg-neon text-[#050505] font-bold flex items-center justify-center gap-2 hover:bg-neon-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_4px_14px_rgba(255,106,0,0.2)]"
                  >
                    Continuar
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Step 2: Confirm */}
              {wizardStep === 2 && (
                <div className="px-6 py-6 space-y-5">
                  {/* Summary card */}
                  <div className="rounded-[16px] bg-[#141414] border border-[rgba(255,255,255,0.06)] p-5">
                    <p className="text-xs text-[#8e8e8e] uppercase tracking-[0.06em] font-medium mb-3">
                      Resumo da criacao
                    </p>
                    <div className="space-y-2.5">
                      <div className="flex items-start gap-3">
                        <Newspaper className="w-4 h-4 text-neon mt-0.5 shrink-0" />
                        <div>
                          <p className="text-xs text-[#8e8e8e]">Tema</p>
                          <p className="font-semibold text-sm mt-0.5">{resolvedTopic}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4 text-[#626262] shrink-0" />
                        <div>
                          <p className="text-xs text-[#8e8e8e]">Periodo</p>
                          <p className="font-semibold text-sm mt-0.5">{periodLabel}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <ImageIcon className="w-4 h-4 text-[#626262] shrink-0" />
                        <div>
                          <p className="text-xs text-[#8e8e8e]">Imagens</p>
                          <p className="font-semibold text-sm mt-0.5">
                            {imageStrategy === "capa" ? "So capa (IA)" : imageStrategy === "ia" ? "Todas com IA" : imageStrategy === "banco" ? "Banco R2" : "Sem imagens"}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Zap className="w-4 h-4 text-[#626262] shrink-0" />
                        <div>
                          <p className="text-xs text-[#8e8e8e]">Modelo</p>
                          <p className="font-semibold text-sm mt-0.5">
                            {selectedModel.includes("haiku") ? "Haiku (rapido)" : selectedModel.includes("opus") ? "Opus (melhor)" : "Sonnet (padrao)"}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-[#737373] text-center leading-relaxed">
                    A IA vai pesquisar noticias, criar a estrategia, escrever o copy{imageStrategy !== "nenhuma" ? ", gerar as imagens" : ""} e montar os slides. Tudo de uma vez.
                  </p>

                  <button
                    onClick={handleWizardConfirm}
                    className="w-full h-14 rounded-[14px] bg-neon text-[#050505] font-bold text-base flex items-center justify-center gap-2 hover:bg-neon-dark transition-colors shadow-[0_8px_20px_rgba(255,106,0,0.25)]"
                  >
                    <Play className="w-5 h-5" />
                    Criar agora
                  </button>

                  <button
                    onClick={() => setWizardStep(1)}
                    className="w-full text-sm text-[#626262] hover:text-foreground transition-colors py-1"
                  >
                    Voltar e editar
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live execution panel */}
      <AnimatePresence>
        {runStatus !== "idle" && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-7xl mx-auto px-6 pb-8"
          >
            <div
              className={`rounded-[20px] border bg-[#0d0d0d] overflow-hidden ${
                flowPhase === "done"
                  ? "border-[#217a28]/40"
                  : runStatus === "error"
                  ? "border-red-500/30"
                  : "border-[rgba(255,106,0,0.2)]"
              }`}
            >
              {/* Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(255,255,255,0.06)]">
                <div className="flex items-center gap-3">
                  {isAnyRunning && (
                    <div className="w-2 h-2 rounded-full bg-[#ff6a00] animate-pulse" />
                  )}
                  {flowPhase === "done" && (
                    <CheckCircle2 className="w-4 h-4 text-[#8cff2e]" />
                  )}
                  {runStatus === "error" && <X className="w-4 h-4 text-red-400" />}
                  <span className="font-bold text-sm tracking-[-0.02em]">
                    {flowPhase === "done"
                      ? "Carrossel criado: "
                      : runStatus === "error"
                      ? "Erro ao criar: "
                      : "Criando carrossel: "}
                    <span
                      className={
                        flowPhase === "done"
                          ? "text-[#8cff2e]"
                          : runStatus === "error"
                          ? "text-red-400"
                          : "text-[#ff6a00]"
                      }
                    >
                      {launchedTopic}
                    </span>
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  {isAnyRunning && (
                    <>
                      <span className="text-xs text-[#626262] font-mono">
                        {Math.floor(elapsedSecs / 60)
                          .toString()
                          .padStart(2, "0")}
                        :{(elapsedSecs % 60).toString().padStart(2, "0")}
                      </span>
                      <Loader2 className="w-4 h-4 text-[#ff6a00] animate-spin" />
                    </>
                  )}
                  {flowPhase === "done" && (
                    <span className="text-xs text-[#8cff2e]">
                      Concluido em {Math.floor(elapsedSecs / 60)}m{elapsedSecs % 60}s
                    </span>
                  )}
                  {(runStatus === "error" || flowPhase === "done") && (
                    <button
                      onClick={() => { setRunStatus("idle"); setFlowPhase("idle"); }}
                      className="text-xs text-[#626262] hover:text-white flex items-center gap-1"
                    >
                      <X className="w-3 h-3" /> Fechar
                    </button>
                  )}
                </div>
              </div>

              {/* Agent grid — uses state.json when available */}
              <div className="p-6">
                {squadState?.agents ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    {squadState.agents.map((agent) => {
                      const isDone = agent.status === "done";
                      const isActive = agent.status === "running";
                      return (
                        <motion.div
                          key={agent.id}
                          animate={isActive ? { scale: [1, 1.02, 1] } : { scale: 1 }}
                          transition={isActive ? { repeat: Infinity, duration: 1.8 } : {}}
                          className={`flex items-center gap-3 p-3 rounded-[12px] border transition-all duration-300 ${
                            isActive
                              ? "bg-[#ff6a00]/08 border-[#ff6a00]/40"
                              : isDone
                              ? "bg-[#217a28]/06 border-[#217a28]/25"
                              : "bg-[#141414] border-[rgba(255,255,255,0.04)]"
                          }`}
                        >
                          <span className="text-lg leading-none">{agent.icon}</span>
                          <div className="min-w-0">
                            <p className={`text-xs font-semibold truncate ${
                              isActive ? "text-[#ff6a00]" : isDone ? "text-[#8cff2e]" : "text-[#5e5e5e]"
                            }`}>
                              {agent.name}
                            </p>
                            <p className="text-[10px] text-[#3d3d3d] mt-0.5">
                              {isActive ? "trabalhando..." : isDone ? "concluido" : "aguardando"}
                            </p>
                          </div>
                          {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#ff6a00] animate-pulse flex-shrink-0" />}
                          {isDone && <span className="ml-auto text-[#217a28] text-xs flex-shrink-0">v</span>}
                        </motion.div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex items-center gap-3 py-4 text-[#3d3d3d]">
                    <Loader2 className="w-4 h-4 animate-spin text-[#ff6a00]/50" />
                    <span className="text-sm">Iniciando agentes...</span>
                  </div>
                )}

                {/* Handoff message */}
                {squadState?.handoff?.message && isAnyRunning && (
                  <div className="mt-4 flex items-start gap-2 p-3 rounded-[10px] bg-[#141414] border border-[rgba(255,255,255,0.04)]">
                    <Zap className="w-3.5 h-3.5 text-[#ff6a00]/60 mt-0.5 flex-shrink-0" />
                    <p className="text-[11px] text-[#737373] leading-relaxed">
                      <span className="text-[#ff6a00]/70 font-medium">{squadState.handoff.from} {"->"} {squadState.handoff.to}: </span>
                      {squadState.handoff.message}
                    </p>
                  </div>
                )}

                {/* Logs toggle */}
                <button
                  onClick={() => setShowLogs((v) => !v)}
                  className="mt-4 text-[11px] text-[#3d3d3d] hover:text-[#626262] transition-colors flex items-center gap-1"
                >
                  <Terminal className="w-3 h-3" />
                  {showLogs ? "Ocultar logs tecnicos" : "Ver logs tecnicos"}
                </button>

                {/* Collapsible terminal */}
                {showLogs && (
                  <div
                    ref={logsRef}
                    className="mt-3 rounded-[10px] p-4 max-h-[200px] overflow-y-auto font-mono text-[10px] leading-relaxed bg-[#050505] border border-[rgba(255,255,255,0.04)]"
                  >
                    {logs.map((line, i) => {
                      const isErr = line.startsWith("[stderr]") || line.includes("Not logged in");
                      const isSys = line.startsWith("[sistema]");
                      return (
                        <div key={i} className={isErr ? "text-red-400" : isSys ? "text-[#ff6a00]/40" : "text-[#3d3d3d]"}>
                          {line}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Done banner — full pipeline complete */}
              {flowPhase === "done" && (
                <div className="px-6 py-4 border-t border-[#217a28]/20 bg-[#217a28]/05 flex items-center gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#8cff2e]" />
                  <div>
                    <p className="text-sm font-bold text-[#8cff2e]">
                      Carrossel pronto!
                    </p>
                    <p className="text-xs text-[#737373] mt-0.5">
                      Os arquivos foram salvos em{" "}
                      <span className="font-mono text-[#626262]">
                        squads/noticias-carrossel-ia/output/
                      </span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Copy Review Checkpoint Panel — removed: single-phase flow now */}

      {/* Progressive output panel */}
      <AnimatePresence>
        {progress && (isAnyRunning || runStatus === "done" || runStatus === "running" || runStatus === "idle") && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-7xl mx-auto px-6 pb-8"
          >
            <div className="rounded-[20px] border border-[rgba(255,255,255,0.06)] bg-[#0d0d0d] overflow-hidden divide-y divide-[rgba(255,255,255,0.04)]">

              {/* Research summary */}
              {progress.researchBrief && (
                <div className="px-6 py-5">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#ff6a00]">Pesquisa</span>
                    {isAnyRunning && !progress.stages.copy && <span className="w-1.5 h-1.5 rounded-full bg-[#ff6a00] animate-pulse" />}
                  </div>
                  <p className="font-bold text-sm tracking-[-0.02em] mb-2">{progress.researchBrief.title}</p>
                  <ul className="space-y-1">
                    {progress.researchBrief.bullets.map((b, i) => (
                      <li key={i} className="text-xs text-[rgba(255,255,255,0.55)] flex gap-2">
                        <span className="text-[#ff6a00] flex-shrink-0">{">"}</span>
                        {b}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Copy slides */}
              {progress.copySlides.length > 0 && (
                <div className="px-6 py-5">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#ff6a00]">Copy</span>
                    <span className="text-xs text-[#626262]">{progress.copySlides.length} slides</span>
                    {isAnyRunning && !progress.stages.images && <span className="w-1.5 h-1.5 rounded-full bg-[#ff6a00] animate-pulse" />}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {progress.copySlides.map((s) => (
                      <div key={s.num} className="p-3 rounded-[12px] bg-[#141414] border border-[rgba(255,255,255,0.04)]">
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className="w-4 h-4 rounded-full bg-[#ff6a00] flex items-center justify-center text-[9px] font-bold text-black">{s.num}</span>
                          <span className="text-[9px] uppercase tracking-[0.06em] text-[#8e8e8e] font-medium truncate">{s.label}</span>
                        </div>
                        <p className="text-xs text-[rgba(255,255,255,0.7)] leading-relaxed line-clamp-3">{s.text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Slide previews */}
              {progress.slides.length > 0 && (
                <div className="px-6 py-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase tracking-[0.06em] font-bold text-[#ff6a00]">Slides prontos</span>
                      <span className="text-xs text-[#626262]">{progress.slides.length} slides</span>
                    </div>
                    <button
                      onClick={() => {
                        setEditorRunId(progress?.publishResult ? "" : "latest");
                        setEditorOpen(true);
                      }}
                      className="flex items-center gap-1.5 px-3 h-7 rounded-[8px] border border-[rgba(255,106,0,0.3)] text-[#ff6a00] text-xs font-semibold hover:bg-[#ff6a00]/10 transition-colors"
                    >
                      <Pencil className="w-3 h-3" />
                      Editar slides
                    </button>
                  </div>
                  <div className="flex gap-3 overflow-x-auto pb-2">
                    {progress.slides.map((slide, i) => (
                      <div key={i} className="flex-shrink-0 w-[150px] h-[200px] rounded-xl overflow-hidden border border-[rgba(255,255,255,0.08)] bg-[#141414]">
                        {slide.type === "image" ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={slide.url} alt={slide.name} className="w-full h-full object-cover" />
                        ) : (
                          <iframe
                            src={slide.url}
                            className="w-[1080px] h-[1440px] border-0"
                            style={{ transform: "scale(0.139)", transformOrigin: "top left", pointerEvents: "none" }}
                            sandbox="allow-same-origin"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Content preview panel (legacy - show only if no progress data) */}
      <AnimatePresence>
        {carouselContent && flowPhase === "done" && !progress?.stages.copy && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="max-w-7xl mx-auto px-6 pb-8"
          >
            <div className="rounded-[20px] border border-[rgba(255,255,255,0.06)] bg-[#0d0d0d] overflow-hidden">
              {/* Toggle header */}
              <button
                onClick={() => setContentOpen((v) => !v)}
                className="w-full flex items-center justify-between px-6 py-4 border-b border-[rgba(255,255,255,0.06)] hover:bg-[#111] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-[#ff6a00]" />
                  <span className="font-bold text-sm tracking-[-0.02em]">
                    Ver conteudo gerado
                  </span>
                  <span className="text-xs text-[#626262]">
                    {carouselContent.slides.length} slides
                  </span>
                </div>
                <motion.div
                  animate={{ rotate: contentOpen ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-4 h-4 text-[#626262]" />
                </motion.div>
              </button>

              {/* Collapsible content */}
              {contentOpen && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="px-6 py-5"
                >
                  {/* Carousel slide previews */}
                  <div className="mb-6">
                    <div className="flex items-center gap-2 mb-3">
                      <ImageIcon className="w-3.5 h-3.5 text-[#ff6a00]" />
                      <span className="text-[11px] uppercase tracking-[0.06em] font-medium text-[#8e8e8e]">
                        Preview dos slides
                      </span>
                    </div>
                    <div className="flex gap-3 overflow-x-auto pb-3 -mx-1 px-1">
                      {carouselContent.slides.map((slide, i) => {
                        const bgColor = slide.background === "claro"
                          ? "#f8f8f8"
                          : slide.background === "acento"
                            ? "#ff6a00"
                            : "#0a0a0a";
                        const textColor = slide.background === "claro" ? "#0a0a0a" : "#fff";
                        const subtextColor = slide.background === "claro"
                          ? "rgba(0,0,0,0.6)"
                          : slide.background === "acento"
                            ? "rgba(255,255,255,0.85)"
                            : "rgba(255,255,255,0.6)";

                        return (
                          <div
                            key={slide.number}
                            className="flex-shrink-0 w-[200px] h-[267px] rounded-xl overflow-hidden border border-[rgba(255,255,255,0.08)] relative flex flex-col justify-between p-4"
                            style={{ backgroundColor: bgColor }}
                          >
                            <div className="flex items-center justify-between">
                              <span
                                className="text-[9px] uppercase tracking-[0.08em] font-bold opacity-50"
                                style={{ color: textColor }}
                              >
                                {slide.label || `Slide ${slide.number}`}
                              </span>
                              <span className="text-[9px] font-bold text-[#ff6a00]">
                                {slide.number}/{carouselContent.slides.length}
                              </span>
                            </div>

                            <div className="flex-1 flex flex-col justify-center py-2">
                              <p
                                className="font-black text-[13px] leading-tight tracking-[-0.03em] mb-1.5"
                                style={{ color: textColor }}
                              >
                                {slide.title || slide.headline}
                              </p>
                              {slide.supportingText && (
                                <p
                                  className="text-[8px] leading-relaxed line-clamp-5"
                                  style={{ color: subtextColor }}
                                >
                                  {slide.supportingText}
                                </p>
                              )}
                            </div>

                            <div className="flex items-center justify-between">
                              {slide.branding ? (
                                <span className="text-[8px] font-bold" style={{ color: textColor, opacity: 0.5 }}>
                                  {slide.branding}
                                </span>
                              ) : (
                                <span />
                              )}
                              {slide.accentKeywords && (
                                <div className="flex gap-0.5">
                                  {slide.accentKeywords.split(",").slice(0, 2).map((kw, ki) => (
                                    <span
                                      key={ki}
                                      className="text-[7px] px-1 py-0.5 rounded bg-[#ff6a00]/20 text-[#ff6a00] font-bold"
                                    >
                                      {kw.trim()}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Slides text grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
                    {carouselContent.slides.map((slide) => (
                      <div
                        key={slide.number}
                        className="p-4 rounded-[15px] bg-[#141414] border border-[rgba(255,255,255,0.04)] hover:border-[rgba(255,255,255,0.1)] transition-colors"
                      >
                        <div className="flex items-center gap-2 mb-2.5">
                          <span className="w-5 h-5 rounded-full bg-[#ff6a00] flex items-center justify-center text-[10px] font-bold text-black">
                            {slide.number}
                          </span>
                          <span className="text-[10px] uppercase tracking-[0.06em] font-medium text-[#8e8e8e]">
                            {slide.label}
                          </span>
                        </div>
                        <p className="font-bold text-sm tracking-[-0.04em] text-white leading-snug mb-1.5">
                          {slide.title || slide.headline}
                        </p>
                        {slide.supportingText && (
                          <p className="text-[12px] leading-relaxed text-[rgba(255,255,255,0.55)] line-clamp-4">
                            {slide.supportingText}
                          </p>
                        )}
                        {slide.accentKeywords && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {slide.accentKeywords.split(",").map((kw, ki) => (
                              <span
                                key={ki}
                                className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#ff6a00]/10 text-[#ff6a00] font-medium"
                              >
                                {kw.trim()}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Caption */}
                  {carouselContent.caption && (
                    <div className="rounded-[15px] bg-[#141414] border border-[rgba(255,255,255,0.04)] p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <Newspaper className="w-3.5 h-3.5 text-[#ff6a00]" />
                        <span className="text-[11px] uppercase tracking-[0.06em] font-medium text-[#8e8e8e]">
                          Caption
                        </span>
                      </div>
                      <p className="text-[13px] leading-relaxed text-[rgba(255,255,255,0.55)] whitespace-pre-line">
                        {carouselContent.caption}
                      </p>
                      {carouselContent.hashtags && (
                        <p className="text-[11px] text-[#ff6a00]/60 mt-3">
                          {carouselContent.hashtags}
                        </p>
                      )}
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Recent carousels */}
      <section className="border-t border-[rgba(255,255,255,0.04)]">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-2xl font-bold tracking-[-0.03em]">
              Carrosseis recentes
            </h2>
            <button className="text-sm text-[#8e8e8e] hover:text-neon transition-colors flex items-center gap-1">
              <Clock className="w-4 h-4" />
              Ver todos
            </button>
          </div>
          <p className="text-[#737373] text-sm mb-4">
            Scroll para explorar seus ultimos carrosseis
          </p>
        </div>
        <CarouselShowcase
          refreshKey={carouselRefreshKey}
          onEdit={(id) => { setEditorRunId(id); setEditorOpen(true); }}
        />
      </section>

      {/* Profile info */}
      {profile && (
        <section className="max-w-7xl mx-auto px-6 py-16 border-t border-[rgba(255,255,255,0.04)]">
          <h2 className="text-xl font-bold tracking-[-0.03em] mb-6">Seu perfil</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)]">
              <p className="text-[11px] text-[#8e8e8e] uppercase tracking-[0.06em] font-medium mb-2">
                Instagram
              </p>
              <p className="font-bold text-neon">@{profile.instagramHandle}</p>
            </div>
            <div className="p-5 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)]">
              <p className="text-[11px] text-[#8e8e8e] uppercase tracking-[0.06em] font-medium mb-2">
                Nicho
              </p>
              <p className="font-bold">{profile.niche || "Nao definido"}</p>
            </div>
            <div className="p-5 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)]">
              <p className="text-[11px] text-[#8e8e8e] uppercase tracking-[0.06em] font-medium mb-2">
                Referencias
              </p>
              <div className="flex flex-wrap gap-1.5">
                {profile.referenceProfiles.length > 0 ? (
                  profile.referenceProfiles.map((ref) => (
                    <span
                      key={ref}
                      className="text-sm px-2 py-0.5 rounded-full bg-[#141414] border border-[#262626]"
                    >
                      @{ref}
                    </span>
                  ))
                ) : (
                  <span className="text-[#626262] text-sm">Nenhuma</span>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Slide Editor (full screen) */}
      {editorOpen && (
        <SlideEditor
          runId={editorRunId}
          onClose={() => setEditorOpen(false)}
          onSaved={(newSlides) => {
            setProgress((prev) =>
              prev ? { ...prev, slides: newSlides } : prev
            );
          }}
        />
      )}
    </div>
  );
}
