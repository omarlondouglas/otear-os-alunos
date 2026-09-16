"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase-browser";
import Link from "next/link";

const NICHES = [
  "Marketing Digital",
  "E-commerce",
  "Saude e Bem-estar",
  "Educacao",
  "Tecnologia",
  "Financas",
  "Alimentacao",
  "Moda e Beleza",
  "Imobiliario",
  "Servicos Profissionais",
  "Outro",
];

export default function SignupPage() {
  const [step, setStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [agencyName, setAgencyName] = useState("");
  const [niche, setNiche] = useState("");
  const [instagram, setInstagram] = useState("");
  const [website, setWebsite] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleStep1(e: React.FormEvent) {
    e.preventDefault();
    if (password.length < 6) {
      setError("Senha deve ter pelo menos 6 caracteres");
      return;
    }
    setError("");
    setStep(2);
  }

  async function handleStep2(e: React.FormEvent) {
    e.preventDefault();
    if (!agencyName.trim() || !niche) {
      setError("Nome da agencia e nicho sao obrigatorios");
      return;
    }
    setError("");
    setLoading(true);

    const supabase = createClient();

    // 1. Sign up
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          agency_name: agencyName,
          niche,
          instagram_handle: instagram,
          website,
        },
      },
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    // 2. Provision tenant via API
    if (authData.user) {
      const res = await fetch("/api/provision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agencyName,
          niche,
          instagramHandle: instagram || undefined,
          website: website || undefined,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        setError(data.error || "Erro ao configurar conta");
        setLoading(false);
        return;
      }
    }

    window.location.href = "/";
  }

  return (
    <div className="min-h-dvh flex items-center justify-center px-4">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-neon rounded-xl mx-auto flex items-center justify-center">
            <span className="text-2xl font-black text-black">O</span>
          </div>
          <h1 className="text-2xl font-bold">Criar conta</h1>
          <p className="text-muted-foreground text-sm">
            {step === 1
              ? "Comece com seus dados de acesso"
              : "Configure sua equipe de IA"}
          </p>
          <div className="flex gap-2 justify-center pt-2">
            <div className={`w-8 h-1 rounded-full ${step >= 1 ? "bg-neon" : "bg-surface-border"}`} />
            <div className={`w-8 h-1 rounded-full ${step >= 2 ? "bg-neon" : "bg-surface-border"}`} />
          </div>
        </div>

        {step === 1 ? (
          <form onSubmit={handleStep1} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
                placeholder="seu@email.com"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
                placeholder="Min. 6 caracteres"
              />
            </div>

            {error && <p className="text-destructive text-sm">{error}</p>}

            <button
              type="submit"
              className="w-full h-11 rounded-lg bg-neon text-black font-semibold text-sm hover:brightness-110 transition"
            >
              Continuar
            </button>
          </form>
        ) : (
          <form onSubmit={handleStep2} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="agency" className="text-sm font-medium">
                Nome da agencia
              </label>
              <input
                id="agency"
                type="text"
                value={agencyName}
                onChange={(e) => setAgencyName(e.target.value)}
                required
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
                placeholder="Minha Agencia"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="niche" className="text-sm font-medium">
                Nicho
              </label>
              <select
                id="niche"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                required
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
              >
                <option value="">Selecione...</option>
                {NICHES.map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label htmlFor="instagram" className="text-sm font-medium">
                Instagram <span className="text-muted-foreground">(opcional)</span>
              </label>
              <input
                id="instagram"
                type="text"
                value={instagram}
                onChange={(e) => setInstagram(e.target.value)}
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
                placeholder="@suaagencia"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="website" className="text-sm font-medium">
                Website <span className="text-muted-foreground">(opcional)</span>
              </label>
              <input
                id="website"
                type="url"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                className="w-full h-11 px-3 rounded-lg bg-surface border border-surface-border text-sm focus:outline-none focus:ring-2 focus:ring-neon/50"
                placeholder="https://suaagencia.com"
              />
            </div>

            {error && <p className="text-destructive text-sm">{error}</p>}

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="h-11 px-4 rounded-lg border border-surface-border text-sm font-medium hover:bg-surface transition"
              >
                Voltar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 h-11 rounded-lg bg-neon text-black font-semibold text-sm hover:brightness-110 transition disabled:opacity-50"
              >
                {loading ? "Criando..." : "Criar equipe de IA"}
              </button>
            </div>
          </form>
        )}

        <p className="text-center text-sm text-muted-foreground">
          Ja tem conta?{" "}
          <Link href="/login" className="text-neon hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
