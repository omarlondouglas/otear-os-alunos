"use client";

import * as React from "react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { saveOnboardingData } from "@/lib/store";
import {
  Instagram,
  Globe,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Plus,
  X,
  Target,
} from "lucide-react";

interface OnboardingProps {
  onComplete: () => void;
}

const STEPS = [
  {
    id: "welcome",
    title: "Bem-vindo ao Tear",
    subtitle: "Vamos configurar seu perfil para criar carrosseis incriveis",
  },
  {
    id: "profile",
    title: "Qual seu perfil no Instagram?",
    subtitle: "Usamos para personalizar o estilo do conteudo",
  },
  {
    id: "niche",
    title: "Qual seu nicho?",
    subtitle: "Sobre o que voce cria conteudo?",
  },
  {
    id: "references",
    title: "Tem perfis que te inspiram?",
    subtitle: "Vamos analisar o estilo deles para criar algo unico pra voce",
  },
  {
    id: "website",
    title: "Tem um site?",
    subtitle: "Podemos extrair contexto sobre seu negocio",
  },
];

export function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = React.useState(0);
  const [instagram, setInstagram] = React.useState("");
  const [niche, setNiche] = React.useState("");
  const [references, setReferences] = React.useState<string[]>([]);
  const [refInput, setRefInput] = React.useState("");
  const [website, setWebsite] = React.useState("");
  const [extracting, setExtracting] = React.useState(false);
  const [extractedDs, setExtractedDs] = React.useState<null | { primary: string; background: string; text: string; font: string }>(null);
  const [extractError, setExtractError] = React.useState(false);
  const [analyzingProfiles, setAnalyzingProfiles] = React.useState(false);
  const [profileAnalysis, setProfileAnalysis] = React.useState<null | { fonts: string[]; primaryColors: string[]; style: string }>(null);
  const [profileAnalysisError, setProfileAnalysisError] = React.useState(false);

  const addReference = () => {
    const handle = refInput.trim().replace(/^@/, "");
    if (handle && !references.includes(handle)) {
      setReferences([...references, handle]);
      setRefInput("");
    }
  };

  const removeReference = (handle: string) => {
    setReferences(references.filter((r) => r !== handle));
  };

  const handleAnalyzeProfiles = async () => {
    if (references.length === 0) return;
    setAnalyzingProfiles(true);
    setProfileAnalysisError(false);
    setProfileAnalysis(null);

    // Analyze first reference profile (most important one)
    try {
      const res = await fetch("/api/analyze-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ handle: references[0] }),
      });
      const data = await res.json() as { ok: boolean; analysis?: { fonts: string[]; primaryColors: string[]; style: string } };
      if (data.ok && data.analysis) {
        setProfileAnalysis({
          fonts: data.analysis.fonts || [],
          primaryColors: data.analysis.primaryColors || [],
          style: data.analysis.style || "",
        });
      } else {
        setProfileAnalysisError(true);
      }
    } catch {
      setProfileAnalysisError(true);
    } finally {
      setAnalyzingProfiles(false);
    }
  };

  const handleExtractDesignSystem = async () => {
    if (!website || website.length <= 5) return;
    setExtracting(true);
    setExtractError(false);
    setExtractedDs(null);
    try {
      const res = await fetch("/api/extract-design-system", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: website }),
      });
      const data = await res.json() as { ok: boolean; designSystem?: { primary: string; background: string; text: string; font: string }; error?: string };
      if (data.ok && data.designSystem) {
        setExtractedDs({
          primary: data.designSystem.primary,
          background: data.designSystem.background,
          text: data.designSystem.text,
          font: data.designSystem.font,
        });
      } else {
        setExtractError(true);
      }
    } catch {
      setExtractError(true);
    } finally {
      setExtracting(false);
    }
  };

  const [provisioning, setProvisioning] = React.useState(false);
  const [provisionError, setProvisionError] = React.useState("");

  const handleFinish = async () => {
    setProvisioning(true);
    setProvisionError("");

    // Save locally (backward compat)
    saveOnboardingData({
      instagramHandle: instagram.replace(/^@/, ""),
      referenceProfiles: references,
      website,
      niche,
    });

    // Provision tenant via API
    try {
      const res = await fetch("/api/provision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agencyName: instagram.replace(/^@/, "") || niche,
          niche,
          instagramHandle: instagram.replace(/^@/, "") || undefined,
          website: website || undefined,
          referenceProfiles: references.length > 0 ? references : undefined,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        // 401 means not authenticated yet (signup flow handles this)
        if (res.status !== 401) {
          setProvisionError(data.error || "Erro ao configurar conta");
          setProvisioning(false);
          return;
        }
      }
    } catch {
      // Non-critical: tenant may have been created during signup
    }

    setProvisioning(false);
    onComplete();
  };

  const canAdvance = () => {
    if (currentStep.id === "profile") return instagram.trim().length > 0;
    if (currentStep.id === "niche") return niche.trim().length > 0;
    return true;
  };

  const currentStep = STEPS[step];

  return (
    <div className="min-h-dvh flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-[120px] pointer-events-none" style={{ background: "rgba(255, 106, 0, 0.06)" }} />

      <div className="w-full max-w-lg relative z-10">
        {/* Progress */}
        <div className="flex gap-2 mb-12">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-1 flex-1 rounded-full transition-all duration-500",
                i <= step ? "bg-neon" : "bg-[#262626]"
              )}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Step Header */}
            <h1 className="text-3xl font-black tracking-[-0.04em] leading-[1em] mb-3">
              {currentStep.title}
            </h1>
            <p className="text-[#8e8e8e] mb-10 text-[15px]">
              {currentStep.subtitle}
            </p>

            {/* Step Content */}
            {step === 0 && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  {[
                    {
                      icon: Sparkles,
                      label: "Pesquisa noticias",
                      desc: "IA busca as noticias mais relevantes",
                    },
                    {
                      icon: Target,
                      label: "Estrategia editorial",
                      desc: "Cria angulo unico pro seu nicho",
                    },
                    {
                      icon: Instagram,
                      label: "Design automatico",
                      desc: "Gera carrossel pronto pra postar",
                    },
                    {
                      icon: Globe,
                      label: "Publicacao",
                      desc: "Publica direto no Instagram",
                    },
                  ].map((item) => (
                    <div
                      key={item.label}
                      className="p-5 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,106,0,0.3)] transition-colors"
                    >
                      <item.icon className="w-5 h-5 text-neon mb-3" />
                      <h3 className="font-bold text-sm mb-1 tracking-[-0.02em]">
                        {item.label}
                      </h3>
                      <p className="text-xs text-[#737373]">
                        {item.desc}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-4">
                <div className="relative">
                  <Instagram className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#626262]" />
                  <Input
                    placeholder="@seuperfil"
                    value={instagram}
                    onChange={(e) => setInstagram(e.target.value)}
                    className="pl-12 h-14 rounded-[15px] bg-[#0d0d0d] border-[rgba(255,255,255,0.06)] focus:ring-neon/40 focus:border-neon/60"
                    autoFocus
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {[
                    "IA & Tecnologia",
                    "Marketing Digital",
                    "Negocios & SaaS",
                    "Empreendedorismo",
                    "Produtividade",
                    "Design",
                    "Financas",
                    "Educacao",
                  ].map((n) => (
                    <button
                      key={n}
                      onClick={() => setNiche(n)}
                      className={cn(
                        "px-4 py-2.5 rounded-full text-sm font-medium border transition-all",
                        niche === n
                          ? "bg-neon text-[#050505] border-neon font-bold"
                          : "bg-[#0d0d0d] border-[rgba(255,255,255,0.06)] text-foreground hover:border-[rgba(255,106,0,0.4)]"
                      )}
                    >
                      {n}
                    </button>
                  ))}
                </div>
                <Input
                  placeholder="Ou digite seu nicho..."
                  value={
                    [
                      "IA & Tecnologia",
                      "Marketing Digital",
                      "Negocios & SaaS",
                      "Empreendedorismo",
                      "Produtividade",
                      "Design",
                      "Financas",
                      "Educacao",
                    ].includes(niche)
                      ? ""
                      : niche
                  }
                  onChange={(e) => setNiche(e.target.value)}
                  className="h-14 rounded-[15px] bg-[#0d0d0d] border-[rgba(255,255,255,0.06)]"
                />
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Instagram className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#626262]" />
                    <Input
                      placeholder="@perfil_referencia"
                      value={refInput}
                      onChange={(e) => setRefInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && addReference()}
                      className="pl-12 h-14 rounded-[15px] bg-[#0d0d0d] border-[rgba(255,255,255,0.06)]"
                      autoFocus
                    />
                  </div>
                  <button
                    onClick={addReference}
                    className="h-14 w-14 rounded-[15px] bg-neon text-[#050505] flex items-center justify-center hover:bg-neon-dark transition-colors"
                  >
                    <Plus className="w-5 h-5" />
                  </button>
                </div>
                {references.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {references.map((ref) => (
                      <div
                        key={ref}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)] text-sm"
                      >
                        <span className="text-neon">@</span>
                        {ref}
                        <button
                          onClick={() => removeReference(ref)}
                          className="text-[#626262] hover:text-destructive transition-colors"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                {references.length > 0 && !profileAnalysis && (
                  <button
                    onClick={handleAnalyzeProfiles}
                    disabled={analyzingProfiles}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-[12px] border border-[rgba(255,255,255,0.1)] text-sm font-semibold hover:bg-[#141414] transition-colors disabled:opacity-50"
                  >
                    {analyzingProfiles ? (
                      <><Sparkles className="w-4 h-4 animate-spin" /> Analisando @{references[0]}...</>
                    ) : (
                      <><Sparkles className="w-4 h-4 text-neon" /> Analisar estilo visual</>
                    )}
                  </button>
                )}

                {profileAnalysis && (
                  <div className="p-4 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)] space-y-3">
                    <div className="flex items-center gap-2 text-xs text-green-400 font-semibold">
                      <Target className="w-3.5 h-3.5" /> Design extraido de @{references[0]}
                    </div>
                    {profileAnalysis.fonts.length > 0 && (
                      <div>
                        <p className="text-[10px] text-[#626262] uppercase tracking-wider mb-1">Fontes</p>
                        <p className="text-sm font-medium">{profileAnalysis.fonts.join(", ")}</p>
                      </div>
                    )}
                    {profileAnalysis.primaryColors.length > 0 && (
                      <div>
                        <p className="text-[10px] text-[#626262] uppercase tracking-wider mb-1">Cores</p>
                        <div className="flex gap-2">
                          {profileAnalysis.primaryColors.slice(0, 5).map((c, i) => (
                            <div key={i} className="flex items-center gap-1.5">
                              <div className="w-5 h-5 rounded-[4px] border border-[rgba(255,255,255,0.15)]" style={{ backgroundColor: c }} />
                              <span className="text-xs text-[#8e8e8e] font-mono">{c}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {profileAnalysis.style && (
                      <p className="text-xs text-[#8e8e8e]">{profileAnalysis.style}</p>
                    )}
                  </div>
                )}

                {profileAnalysisError && (
                  <p className="text-xs text-[#626262]">
                    Nao foi possivel analisar o perfil agora. Continue assim mesmo.
                  </p>
                )}

                {!profileAnalysis && !profileAnalysisError && (
                  <p className="text-xs text-[#626262]">
                    Opcional. Vamos analisar o estilo de conteudo desses perfis.
                  </p>
                )}
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4">
                <div className="relative">
                  <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#626262]" />
                  <Input
                    placeholder="https://seusite.com.br"
                    value={website}
                    onChange={(e) => {
                      setWebsite(e.target.value);
                      setExtractedDs(null);
                      setExtractError(false);
                    }}
                    className="pl-12 h-14 rounded-[15px] bg-[#0d0d0d] border-[rgba(255,255,255,0.06)]"
                    autoFocus
                  />
                </div>

                {website.length > 5 && !extractedDs && (
                  <button
                    onClick={handleExtractDesignSystem}
                    disabled={extracting}
                    className={cn(
                      "w-full flex items-center justify-center gap-2 h-12 rounded-[15px] border text-sm font-medium transition-all",
                      extracting
                        ? "border-[rgba(255,255,255,0.06)] text-[#626262] cursor-not-allowed"
                        : "border-neon/40 text-neon hover:bg-neon/5"
                    )}
                  >
                    {extracting ? (
                      <>
                        <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Analisando...
                      </>
                    ) : (
                      <>
                        <span>✦</span>
                        Extrair cores e fontes
                      </>
                    )}
                  </button>
                )}

                {extractedDs && (
                  <div className="p-4 rounded-[15px] bg-[#0d0d0d] border border-[rgba(255,255,255,0.06)]">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-green-400 text-sm">&#10003;</span>
                      <span className="text-sm text-[#8e8e8e]">Design system extraido! Seus slides usarao essas cores.</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex gap-2">
                        <div
                          className="w-7 h-7 rounded-full border border-[rgba(255,255,255,0.1)] flex-shrink-0"
                          style={{ background: extractedDs.primary }}
                          title={`Primary: ${extractedDs.primary}`}
                        />
                        <div
                          className="w-7 h-7 rounded-full border border-[rgba(255,255,255,0.1)] flex-shrink-0"
                          style={{ background: extractedDs.background }}
                          title={`Background: ${extractedDs.background}`}
                        />
                        <div
                          className="w-7 h-7 rounded-full border border-[rgba(255,255,255,0.1)] flex-shrink-0"
                          style={{ background: extractedDs.text }}
                          title={`Text: ${extractedDs.text}`}
                        />
                      </div>
                      {extractedDs.font && (
                        <span className="text-xs text-[#626262] truncate">
                          {extractedDs.font}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {extractError && (
                  <p className="text-xs text-[#8e8e8e]">
                    Nao foi possivel extrair. Continue assim mesmo.
                  </p>
                )}

                <p className="text-xs text-[#626262]">
                  Opcional. Extraimos contexto do seu negocio pra deixar o
                  conteudo mais relevante.
                </p>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-12">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-medium text-[#8e8e8e] hover:text-foreground transition-colors",
              step === 0 && "invisible"
            )}
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </button>

          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              disabled={!canAdvance()}
              className="flex items-center gap-2 px-7 py-3.5 rounded-[21px] bg-neon text-[#050505] font-bold text-sm hover:bg-neon-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_8px_20px_rgba(255,106,0,0.25)]"
            >
              Continuar
              <ArrowRight className="w-4 h-4" />
            </button>
          ) : (
            <div className="flex flex-col items-end gap-2">
              {provisionError && (
                <p className="text-xs text-destructive">{provisionError}</p>
              )}
              <button
                onClick={handleFinish}
                disabled={provisioning}
                className="flex items-center gap-2 px-7 py-3.5 rounded-[21px] bg-neon text-[#050505] font-bold text-sm hover:bg-neon-dark transition-colors shadow-[0_8px_20px_rgba(255,106,0,0.25)] disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {provisioning ? "Configurando..." : "Comecar a criar"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
