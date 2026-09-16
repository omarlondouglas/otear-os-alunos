"use client";

import * as React from "react";
import { createClient } from "@/lib/supabase-browser";
import { Check, Zap, ArrowLeft } from "lucide-react";
import Link from "next/link";

const PLANS = [
  {
    id: "free",
    name: "Free",
    price: "Gratis",
    runs: "5 runs/mes",
    features: [
      "1 squad de carrossel",
      "5 carrosseis por mes",
      "Escritorio virtual",
      "Preview em tempo real",
    ],
    cta: "Plano atual",
    disabled: true,
  },
  {
    id: "starter",
    name: "Starter",
    price: "R$149",
    period: "/mes",
    runs: "50 runs/mes",
    features: [
      "Tudo do Free",
      "50 carrosseis por mes",
      "Imagens IA incluidas",
      "Suporte por email",
    ],
    cta: "Fazer upgrade",
    highlight: true,
  },
  {
    id: "pro",
    name: "Pro",
    price: "R$449",
    period: "/mes",
    runs: "Ilimitado",
    features: [
      "Tudo do Starter",
      "Carrosseis ilimitados",
      "Prioridade na fila",
      "Suporte prioritario",
      "Squads customizados (em breve)",
    ],
    cta: "Fazer upgrade",
  },
];

export default function UpgradePage() {
  const [currentPlan, setCurrentPlan] = React.useState("free");

  React.useEffect(() => {
    async function load() {
      const supabase = createClient();
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: membership } = await supabase
        .from("tenant_members")
        .select("tenants(plan)")
        .eq("user_id", user.id)
        .limit(1)
        .maybeSingle();

      if (membership?.tenants) {
        setCurrentPlan((membership.tenants as any).plan);
      }
    }
    load();
  }, []);

  return (
    <div className="min-h-dvh flex flex-col items-center px-4 py-12">
      <Link
        href="/"
        className="self-start flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition mb-8"
      >
        <ArrowLeft className="w-4 h-4" />
        Voltar ao dashboard
      </Link>

      <div className="text-center mb-12">
        <h1 className="text-3xl font-black tracking-tight mb-3">
          Escolha seu plano
        </h1>
        <p className="text-muted-foreground">
          Escale sua producao de conteudo com mais carrosseis por mes
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4 w-full max-w-3xl">
        {PLANS.map((plan) => {
          const isCurrent = plan.id === currentPlan;
          return (
            <div
              key={plan.id}
              className={`relative rounded-xl p-6 border transition ${
                plan.highlight
                  ? "border-neon bg-neon/5 shadow-[0_0_30px_rgba(255,106,0,0.1)]"
                  : "border-surface-border bg-card"
              }`}
            >
              {plan.highlight && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-neon text-black text-xs font-bold">
                  Popular
                </div>
              )}

              <h3 className="text-lg font-bold mb-1">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-2xl font-black">{plan.price}</span>
                {plan.period && (
                  <span className="text-sm text-muted-foreground">{plan.period}</span>
                )}
              </div>
              <p className="text-xs text-muted-foreground mb-5">{plan.runs}</p>

              <ul className="space-y-2.5 mb-6">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-neon shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>

              <button
                disabled={isCurrent || plan.disabled}
                className={`w-full h-10 rounded-lg text-sm font-semibold transition ${
                  isCurrent
                    ? "bg-surface border border-surface-border text-muted-foreground cursor-default"
                    : plan.highlight
                    ? "bg-neon text-black hover:brightness-110"
                    : "bg-surface border border-surface-border text-foreground hover:border-neon/50"
                } disabled:opacity-50`}
              >
                {isCurrent ? (
                  "Plano atual"
                ) : (
                  <span className="flex items-center justify-center gap-1.5">
                    <Zap className="w-3.5 h-3.5" />
                    {plan.cta}
                  </span>
                )}
              </button>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-muted-foreground mt-8 text-center max-w-md">
        Integracao com Stripe em breve. Entre em contato para ativar seu plano manualmente.
      </p>
    </div>
  );
}
