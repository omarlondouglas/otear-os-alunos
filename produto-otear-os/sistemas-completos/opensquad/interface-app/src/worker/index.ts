/**
 * OpenSquad SaaS Worker
 *
 * Standalone process that consumes the BullMQ squad-runs queue.
 * Each job spawns a Claude CLI process, watches state.json for
 * progress updates, and publishes events via Redis pub/sub.
 *
 * Run: npx tsx src/worker/index.ts
 */

import { Worker, Job } from "bullmq";
import { spawn } from "child_process";
import path from "path";
import os from "os";
import fs from "fs";
import IORedis from "ioredis";
import {
  SQUAD_QUEUE_NAME,
  type SquadJobData,
  type SquadJobResult,
  publishStateUpdate,
  publishOutputUpdate,
} from "../lib/queue";
import { tenantRoot, tenantOutputDir, tenantStatePath } from "../lib/tenant";
import { buildSquadPrompt } from "../lib/prompt-builder";

// ============================================================
// Config
// ============================================================

const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
const CONCURRENCY = parseInt(process.env.WORKER_CONCURRENCY || "1", 10);

// Supabase service client for updating runs table
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

// ============================================================
// Claude Credentials
// ============================================================

function ensureClaudeCredentials(): void {
  const token = process.env.CLAUDE_OAUTH_ACCESS_TOKEN;
  if (!token) return;

  const home = process.env.HOME || os.homedir();
  const claudeDir = path.join(home, ".claude");
  const credsFile = path.join(claudeDir, ".credentials.json");

  fs.mkdirSync(claudeDir, { recursive: true });
  const creds = JSON.stringify({
    claudeAiOauth: {
      accessToken: token,
      refreshToken: process.env.CLAUDE_OAUTH_REFRESH_TOKEN || "",
      expiresAt: parseInt(process.env.CLAUDE_OAUTH_EXPIRES_AT || "0", 10),
      scopes: [
        "user:file_upload",
        "user:inference",
        "user:mcp_servers",
        "user:profile",
        "user:sessions:claude_code",
      ],
      subscriptionType: process.env.CLAUDE_SUBSCRIPTION_TYPE || "max",
      rateLimitTier: process.env.CLAUDE_RATE_LIMIT_TIER || "default_claude_max_5x",
    },
  });
  fs.writeFileSync(credsFile, creds, "utf-8");
}

// ============================================================
// State Watcher
// ============================================================

function watchState(
  tenantId: string,
  squadCode: string,
  signal: AbortSignal
): void {
  const statePath = tenantStatePath(tenantId, squadCode);
  let lastMtime = 0;

  const interval = setInterval(async () => {
    if (signal.aborted) {
      clearInterval(interval);
      return;
    }
    try {
      if (!fs.existsSync(statePath)) return;
      const stat = fs.statSync(statePath);
      if (stat.mtimeMs <= lastMtime) return;
      lastMtime = stat.mtimeMs;

      const raw = fs.readFileSync(statePath, "utf-8");
      const state = JSON.parse(raw);
      await publishStateUpdate(tenantId, { type: "state", state });
    } catch {
      // file may be mid-write
    }
  }, 2000);

  signal.addEventListener("abort", () => clearInterval(interval));
}

// ============================================================
// Output Watcher
// ============================================================

function watchOutput(
  tenantId: string,
  squadCode: string,
  signal: AbortSignal
): void {
  const outputDir = tenantOutputDir(tenantId, squadCode);
  const seen = new Set<string>();

  const interval = setInterval(async () => {
    if (signal.aborted) {
      clearInterval(interval);
      return;
    }
    try {
      if (!fs.existsSync(outputDir)) return;

      // Find latest run dir
      const dirs = fs.readdirSync(outputDir, { withFileTypes: true })
        .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
        .map((e) => e.name).sort().reverse();

      if (dirs.length === 0) return;
      const runDir = path.join(outputDir, dirs[0]);

      // Check for key output files
      const candidates = [
        "carousel-content.md",
        "slides-data.json",
        "strategy-brief.md",
        "research-brief.md",
      ];

      // Also check versioned subdirs
      const searchDirs = [runDir];
      const versions = fs.readdirSync(runDir, { withFileTypes: true })
        .filter((e) => e.isDirectory() && /^v\d+$/i.test(e.name));
      for (const v of versions) {
        searchDirs.push(path.join(runDir, v.name));
      }

      for (const dir of searchDirs) {
        for (const file of candidates) {
          const filePath = path.join(dir, file);
          const key = filePath;
          if (seen.has(key)) continue;
          if (!fs.existsSync(filePath)) continue;

          seen.add(key);
          await publishOutputUpdate(tenantId, {
            type: "output-file",
            file,
            path: filePath,
            runId: dirs[0],
          });
        }

        // Check for images
        const imagesDir = path.join(dir, "images");
        if (fs.existsSync(imagesDir)) {
          const images = fs.readdirSync(imagesDir).filter((f) => /\.(png|jpg|jpeg)$/i.test(f));
          for (const img of images) {
            const key = path.join(imagesDir, img);
            if (seen.has(key)) continue;
            seen.add(key);
            await publishOutputUpdate(tenantId, {
              type: "output-image",
              file: img,
              runId: dirs[0],
            });
          }
        }
      }
    } catch {
      // ignore
    }
  }, 3000);

  signal.addEventListener("abort", () => clearInterval(interval));
}

// ============================================================
// Job Processor
// ============================================================

async function processSquadJob(job: Job<SquadJobData>): Promise<SquadJobResult> {
  const { tenantId, tenantSlug, topic, period, mode, imageStrategy, model, runDbId } = job.data;

  console.log(`[worker] Processing job ${job.id} for tenant ${tenantSlug}: "${topic}"`);

  // Update run status in DB
  if (supabase) {
    await supabase.from("runs").update({ status: "running", started_at: new Date().toISOString() }).eq("id", runDbId);
  }

  await publishStateUpdate(tenantId, { type: "job-started", jobId: job.id, topic });

  // Ensure credentials
  ensureClaudeCredentials();

  // Build prompt
  const squadCode = "noticias-carrossel-ia";
  const prompt = buildSquadPrompt({ squadCode, topic, period, mode, imageStrategy });

  // Resolve paths
  const root = tenantRoot(tenantId);
  const logsDir = tenantOutputDir(tenantId, "carousel");
  fs.mkdirSync(logsDir, { recursive: true });

  // Create log file
  const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
  const logFile = path.join(logsDir, `run-${ts}.log`);
  const logStream = fs.createWriteStream(logFile, { flags: "a" });
  logStream.write(`[${new Date().toISOString()}] Job: ${job.id}\n`);
  logStream.write(`[${new Date().toISOString()}] Tenant: ${tenantId} (${tenantSlug})\n`);
  logStream.write(`[${new Date().toISOString()}] Tema: ${topic}\n`);
  logStream.write(`[${new Date().toISOString()}] Mode: ${mode}\n`);
  logStream.write(`${"=".repeat(60)}\n`);

  // Start state and output watchers
  const ac = new AbortController();
  watchState(tenantId, "carousel", ac.signal);
  watchOutput(tenantId, "carousel", ac.signal);

  // Spawn Claude CLI
  const isWindows = os.platform() === "win32";
  const claudeArgs = [
    "-p", prompt,
    "--model", model,
    "--dangerously-skip-permissions",
    "--output-format", "text",
    "--verbose",
  ];

  const proc = isWindows
    ? spawn("claude.cmd", claudeArgs, {
        cwd: root,
        shell: true,
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env },
      })
    : spawn("claude", claudeArgs, {
        cwd: root,
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env },
      });

  // Pipe output to log
  proc.stdout?.on("data", (data: Buffer) => {
    logStream.write(data);
  });
  proc.stderr?.on("data", (data: Buffer) => {
    logStream.write(`[stderr] ${data}`);
  });

  // Wait for process to complete
  const exitCode = await new Promise<number>((resolve) => {
    proc.on("close", (code) => resolve(code ?? 1));
    proc.on("error", (err) => {
      logStream.write(`[ERROR] ${err.message}\n`);
      resolve(1);
    });
  });

  // Stop watchers
  ac.abort();

  logStream.write(`\n${"=".repeat(60)}\n[${new Date().toISOString()}] Exit code: ${exitCode}\n`);

  // Post-processing
  let slidesRendered = 0;
  let s3Uploaded = 0;
  let runDir: string | null = null;

  if (exitCode === 0) {
    try {
      const dirs = fs.readdirSync(logsDir, { withFileTypes: true })
        .filter((e) => e.isDirectory() && /^\d{4}-\d{2}-\d{2}/.test(e.name))
        .map((e) => e.name).sort().reverse();

      if (dirs.length > 0) {
        runDir = path.join(logsDir, dirs[0]);

        // Render slides
        try {
          const { renderSlidesToJpg } = await import("../lib/render-slides");
          const rendered = await renderSlidesToJpg(runDir);
          slidesRendered = rendered.length;
          logStream.write(`[sistema] ${slidesRendered} slides renderizados\n`);
        } catch (err) {
          logStream.write(`[sistema] Erro render: ${err}\n`);
        }

        // Upload to S3
        try {
          const { uploadRunToS3, isS3Configured } = await import("../lib/s3");
          if (isS3Configured()) {
            const uploaded = await uploadRunToS3(runDir, dirs[0]);
            s3Uploaded = uploaded.length;
            logStream.write(`[sistema] ${s3Uploaded} arquivos S3\n`);
          }
        } catch (err) {
          logStream.write(`[sistema] Erro S3: ${err}\n`);
        }

        // Auto-save images to bank
        try {
          const { autoSaveImagesToBank } = await import("../lib/image-bank");
          await autoSaveImagesToBank(runDir, topic, (msg) => logStream.write(`${msg}\n`));
        } catch (err) {
          logStream.write(`[sistema] Erro bank: ${err}\n`);
        }
      }
    } catch (err) {
      logStream.write(`[sistema] Erro pos-proc: ${err}\n`);
    }

    // Increment runs_used
    if (supabase) {
      await supabase.rpc("increment_runs_used", { p_tenant_id: tenantId });
    }
  }

  // Update run status in DB
  const finalStatus = exitCode === 0 ? "completed" : "failed";
  if (supabase) {
    await supabase.from("runs").update({
      status: finalStatus,
      completed_at: new Date().toISOString(),
      output_path: runDir,
    }).eq("id", runDbId);
  }

  logStream.end();

  await publishStateUpdate(tenantId, {
    type: "job-completed",
    jobId: job.id,
    status: finalStatus,
    slidesRendered,
  });

  console.log(`[worker] Job ${job.id} ${finalStatus} (exit: ${exitCode}, slides: ${slidesRendered})`);

  return { exitCode, runDir, slidesRendered, s3Uploaded };
}

// ============================================================
// Start Worker
// ============================================================

console.log(`[worker] Starting with concurrency=${CONCURRENCY}, redis=${REDIS_URL}`);

const connection = new IORedis(REDIS_URL, { maxRetriesPerRequest: null });

const worker = new Worker<SquadJobData, SquadJobResult>(
  SQUAD_QUEUE_NAME,
  processSquadJob,
  {
    connection,
    concurrency: CONCURRENCY,
    // Per-tenant: max 1 concurrent job (uses job.data.tenantId as group key)
    limiter: {
      max: 1,
      duration: 1000,
    },
  }
);

worker.on("completed", (job) => {
  console.log(`[worker] Job ${job?.id} completed`);
});

worker.on("failed", (job, err) => {
  console.error(`[worker] Job ${job?.id} failed: ${err.message}`);
});

worker.on("error", (err) => {
  console.error(`[worker] Worker error: ${err.message}`);
});

// Graceful shutdown
process.on("SIGTERM", async () => {
  console.log("[worker] SIGTERM received, closing...");
  await worker.close();
  connection.disconnect();
  process.exit(0);
});

process.on("SIGINT", async () => {
  console.log("[worker] SIGINT received, closing...");
  await worker.close();
  connection.disconnect();
  process.exit(0);
});

console.log("[worker] Ready, waiting for jobs...");
