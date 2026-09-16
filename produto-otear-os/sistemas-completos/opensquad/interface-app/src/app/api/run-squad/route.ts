import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import os from "os";
import fs from "fs";
import { uploadRunToS3, isS3Configured } from "@/lib/s3";
import { renderSlidesToJpg } from "@/lib/render-slides";
import { autoSaveImagesToBank } from "@/lib/image-bank";
import { getTenantContext, canStartRun, incrementRunsUsed, type TenantContext } from "@/lib/auth";
import { tenantRoot, tenantOutputDir } from "@/lib/tenant";
import { isRedisAvailable, getSquadQueue, type SquadJobData } from "@/lib/queue";
import { supabase } from "@/lib/supabase";
import { buildSquadPrompt } from "@/lib/prompt-builder";

// Legacy fallback
const LEGACY_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LEGACY_LOGS_DIR = path.join(LEGACY_ROOT, "squads", "noticias-carrossel-ia", "output");

function resolvePaths(ctx: TenantContext | null) {
  if (ctx) {
    try {
      const root = tenantRoot(ctx.tenantId);
      const logsDir = tenantOutputDir(ctx.tenantId, "carousel");
      // Check if tenant dir exists, fall back to legacy if not
      if (fs.existsSync(root)) return { root, logsDir };
    } catch { /* fall through */ }
  }
  return { root: LEGACY_ROOT, logsDir: LEGACY_LOGS_DIR };
}

// In-memory active runs for legacy mode
const activeRuns = new Map<string, { pid: number; startedAt: string; topic: string; logFile: string; status: string }>();

function ensureClaudeCredentials(): void {
  const token = process.env.CLAUDE_OAUTH_ACCESS_TOKEN;
  if (!token) return;
  const home = process.env.HOME || os.homedir();
  const claudeDir = path.join(home, ".claude");
  const credsFile = path.join(claudeDir, ".credentials.json");
  const configFile = path.join(home, ".claude.json");

  fs.mkdirSync(claudeDir, { recursive: true });

  // Write credentials
  fs.writeFileSync(credsFile, JSON.stringify({
    claudeAiOauth: {
      accessToken: token,
      refreshToken: process.env.CLAUDE_OAUTH_REFRESH_TOKEN || "",
      expiresAt: parseInt(process.env.CLAUDE_OAUTH_EXPIRES_AT || "0", 10),
      scopes: ["user:file_upload","user:inference","user:mcp_servers","user:profile","user:sessions:claude_code"],
      subscriptionType: process.env.CLAUDE_SUBSCRIPTION_TYPE || "max",
      rateLimitTier: process.env.CLAUDE_RATE_LIMIT_TIER || "default_claude_max_5x",
    },
  }), "utf-8");

  // Ensure .claude.json exists (CLI won't start without it)
  if (!fs.existsSync(configFile)) {
    // Try to restore from backup
    const backupsDir = path.join(claudeDir, "backups");
    let restored = false;
    if (fs.existsSync(backupsDir)) {
      const backups = fs.readdirSync(backupsDir)
        .filter(f => f.startsWith(".claude.json.backup."))
        .sort().reverse();
      if (backups.length > 0) {
        fs.copyFileSync(path.join(backupsDir, backups[0]), configFile);
        restored = true;
      }
    }
    if (!restored) {
      fs.writeFileSync(configFile, "{}", "utf-8");
    }
  }
}

export async function POST(req: NextRequest) {
  const ctx = await getTenantContext();

  // Check run limits for tenant users
  if (ctx && !canStartRun(ctx)) {
    return NextResponse.json(
      { error: "Limite de runs atingido. Faca upgrade do plano.", runsUsed: ctx.runsUsed, runsLimit: ctx.runsLimit },
      { status: 403 }
    );
  }

  const body = await req.json();
  const {
    topic, period = "A", model, mode = "full", imageStrategy = "nenhuma",
  } = body as {
    topic?: string; period?: string; model?: string;
    mode?: "copy" | "images" | "full";
    imageStrategy?: "ia" | "capa" | "banco" | "nenhuma";
  };

  const claudeModel = model || process.env.CLAUDE_MODEL || "claude-sonnet-4-6";

  if (!topic || typeof topic !== "string") {
    return NextResponse.json({ error: "Topic is required" }, { status: 400 });
  }

  // Try Redis queue mode first
  const redisUp = await isRedisAvailable();

  if (redisUp && ctx) {
    return handleQueueMode(ctx, topic, period, mode, imageStrategy, claudeModel);
  }

  // Fallback: legacy direct spawn mode
  return handleLegacyMode(ctx, topic, period, mode, imageStrategy, claudeModel);
}

// ── Queue Mode (BullMQ + Redis) ──────────────────────────────

async function handleQueueMode(
  ctx: TenantContext, topic: string, period: string,
  mode: string, imageStrategy: string, claudeModel: string
) {
  const queue = getSquadQueue();
  const activeJobs = await queue.getJobs(["active", "waiting"]);
  const tenantActive = activeJobs.find((j) => j.data.tenantId === ctx.tenantId);
  if (tenantActive) {
    return NextResponse.json(
      { error: "Voce ja tem um carrossel em producao.", jobId: tenantActive.id },
      { status: 409 }
    );
  }

  const { data: runRecord, error: runErr } = await supabase.client
    .from("runs")
    .insert({ tenant_id: ctx.tenantId, squad_code: "carousel", topic, status: "queued", mode, image_strategy: imageStrategy })
    .select().single();

  if (runErr || !runRecord) {
    return NextResponse.json({ error: "Failed to create run record" }, { status: 500 });
  }

  const jobData: SquadJobData = {
    tenantId: ctx.tenantId, tenantSlug: ctx.tenantSlug,
    topic, period, mode: mode as any, imageStrategy: imageStrategy as any,
    model: claudeModel, runDbId: runRecord.id,
  };

  const job = await queue.add(`carousel-${ctx.tenantSlug}`, jobData, {
    jobId: `${ctx.tenantId}-${Date.now()}`,
  });

  return NextResponse.json({
    jobId: job.id, runId: runRecord.id, status: "queued", topic, mode,
    runsUsed: ctx.runsUsed + 1, runsLimit: ctx.runsLimit,
  });
}

// ── Legacy Mode (direct spawn, no Redis) ─────────────────────

async function handleLegacyMode(
  ctx: TenantContext | null, topic: string, period: string,
  mode: string, imageStrategy: string, claudeModel: string
) {
  const { root, logsDir } = resolvePaths(ctx);
  const runKey = ctx?.tenantId || "noticias-carrossel-ia";
  const squadCode = "noticias-carrossel-ia";

  if (activeRuns.has(runKey)) {
    return NextResponse.json(
      { error: "Squad already running", run: activeRuns.get(runKey) },
      { status: 409 }
    );
  }

  ensureClaudeCredentials();

  const prompt = buildSquadPrompt({
    squadCode, topic, period,
    mode: mode as any, imageStrategy: imageStrategy as any,
  });

  if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const logFile = path.join(logsDir, `run-${ts}.log`);
  const logStream = fs.createWriteStream(logFile, { flags: "a" });
  logStream.write(`[${new Date().toISOString()}] Squad: ${squadCode}\n[${new Date().toISOString()}] Tema: ${topic}\n[${new Date().toISOString()}] Mode: ${mode}\n${"=".repeat(60)}\n`);

  const isWindows = os.platform() === "win32";
  const claudeArgs = ["-p", prompt, "--model", claudeModel, "--dangerously-skip-permissions", "--output-format", "text", "--verbose"];

  const proc = isWindows
    ? spawn("claude.cmd", claudeArgs, { cwd: root, shell: true, stdio: ["ignore", "pipe", "pipe"], detached: true, env: { ...process.env } })
    : spawn("claude", claudeArgs, { cwd: root, stdio: ["ignore", "pipe", "pipe"], detached: true, env: { ...process.env } });

  proc.stdout?.on("data", (data: Buffer) => logStream.write(data));
  proc.stderr?.on("data", (data: Buffer) => logStream.write(`[stderr] ${data}`));

  proc.on("close", async (code) => {
    logStream.write(`\n${"=".repeat(60)}\n[${new Date().toISOString()}] Exit: ${code}\n`);
    const run = activeRuns.get(runKey);
    if (run) run.status = code === 0 ? "completed" : "failed";

    if (code === 0 && ctx) {
      try { await incrementRunsUsed(ctx.tenantId); } catch { /* best effort */ }
    }

    if (code === 0) {
      try {
        const dirs = fs.readdirSync(logsDir, { withFileTypes: true })
          .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
          .map((e) => e.name).sort().reverse();
        if (dirs.length > 0) {
          const runDir = path.join(logsDir, dirs[0]);
          try { const r = await renderSlidesToJpg(runDir); logStream.write(`[sistema] ${r.length} slides JPG\n`); } catch {}
          if (isS3Configured()) {
            try { const u = await uploadRunToS3(runDir, dirs[0]); logStream.write(`[sistema] ${u.length} S3\n`); } catch {}
            try { await autoSaveImagesToBank(runDir, topic, (m) => logStream.write(`${m}\n`)); } catch {}
          }
        }
      } catch {}
    }
    logStream.end();
    setTimeout(() => activeRuns.delete(runKey), 5 * 60 * 1000);
  });

  proc.on("error", (err) => { logStream.write(`[ERROR] ${err.message}\n`); logStream.end(); });
  proc.unref();

  const newRunId = ts;
  activeRuns.set(runKey, { pid: proc.pid || 0, startedAt: new Date().toISOString(), topic, logFile, status: "running" });

  return NextResponse.json({ pid: proc.pid, startedAt: new Date().toISOString(), topic, logFile, status: "running", runId: newRunId, mode });
}

// ── GET: check status ────────────────────────────────────────

export async function GET(req: NextRequest) {
  const ctx = await getTenantContext();
  const { logsDir } = resolvePaths(ctx);
  const runKey = ctx?.tenantId || "noticias-carrossel-ia";

  const url = new URL(req.url);
  const wantLogs = url.searchParams.get("logs") === "1";
  const tailLines = parseInt(url.searchParams.get("tail") || "100", 10);

  const active = activeRuns.get(runKey) || null;

  let logs: string[] = [];
  if (wantLogs && active?.logFile && fs.existsSync(active.logFile)) {
    const content = fs.readFileSync(active.logFile, "utf-8");
    logs = content.split("\n").slice(-tailLines);
  }

  if (wantLogs && !active) {
    try {
      const files = fs.readdirSync(logsDir).filter((f) => f.startsWith("run-")).sort().reverse();
      if (files.length > 0) {
        const content = fs.readFileSync(path.join(logsDir, files[0]), "utf-8");
        logs = content.split("\n").slice(-tailLines);
      }
    } catch { /* ignore */ }
  }

  return NextResponse.json({ isRunning: active?.status === "running", run: active, logs });
}

// ── DELETE: stop run ─────────────────────────────────────────

export async function DELETE() {
  const ctx = await getTenantContext();
  const runKey = ctx?.tenantId || "noticias-carrossel-ia";

  const run = activeRuns.get(runKey);
  if (run?.pid) {
    try { process.kill(run.pid, "SIGTERM"); } catch { /* already dead */ }
  }
  activeRuns.delete(runKey);
  return NextResponse.json({ status: "stopped" });
}
