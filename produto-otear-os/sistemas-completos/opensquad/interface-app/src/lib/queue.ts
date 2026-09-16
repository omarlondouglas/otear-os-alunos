import { Queue, Worker, Job } from "bullmq";
import IORedis from "ioredis";

// ============================================================
// Redis Connection
// ============================================================

const REDIS_URL = process.env.REDIS_URL || "";

let _connection: IORedis | null = null;
let _redisAvailable: boolean | null = null;

export function getRedisConnection(): IORedis {
  if (!_connection) {
    if (!REDIS_URL) throw new Error("REDIS_URL not configured");
    _connection = new IORedis(REDIS_URL, { maxRetriesPerRequest: null, lazyConnect: true });
  }
  return _connection;
}

/** Check if Redis is reachable (cached after first check) */
export async function isRedisAvailable(): Promise<boolean> {
  if (_redisAvailable !== null) return _redisAvailable;
  if (!REDIS_URL) { _redisAvailable = false; return false; }
  try {
    const conn = getRedisConnection();
    await conn.connect();
    await conn.ping();
    _redisAvailable = true;
  } catch {
    _redisAvailable = false;
  }
  return _redisAvailable;
}

// ============================================================
// Job Types
// ============================================================

export interface SquadJobData {
  tenantId: string;
  tenantSlug: string;
  topic: string;
  period: string;
  mode: "copy" | "images" | "full";
  imageStrategy: "ia" | "capa" | "banco" | "nenhuma";
  model: string;
  runDbId: string; // UUID from the runs table
}

export interface SquadJobResult {
  exitCode: number;
  runDir: string | null;
  slidesRendered: number;
  s3Uploaded: number;
}

// ============================================================
// Queue Constants
// ============================================================

export const SQUAD_QUEUE_NAME = "squad-runs";

// ============================================================
// Queue Instance (used by the API to add jobs)
// ============================================================

let _queue: Queue<SquadJobData, SquadJobResult> | null = null;

export function getSquadQueue(): Queue<SquadJobData, SquadJobResult> {
  if (!_queue) {
    _queue = new Queue<SquadJobData, SquadJobResult>(SQUAD_QUEUE_NAME, {
      connection: getRedisConnection(),
      defaultJobOptions: {
        attempts: 2,
        backoff: { type: "exponential", delay: 30000 },
        removeOnComplete: { count: 100 },
        removeOnFail: { count: 50 },
      },
    });
  }
  return _queue;
}

// ============================================================
// Pub/Sub Channels
// ============================================================

export function stateChannel(tenantId: string): string {
  return `tenant:${tenantId}:state`;
}

export function outputChannel(tenantId: string): string {
  return `tenant:${tenantId}:output`;
}

// ============================================================
// Publish state update via Redis
// ============================================================

export async function publishStateUpdate(
  tenantId: string,
  data: Record<string, unknown>
): Promise<void> {
  const conn = getRedisConnection();
  await conn.publish(stateChannel(tenantId), JSON.stringify(data));
}

export async function publishOutputUpdate(
  tenantId: string,
  data: Record<string, unknown>
): Promise<void> {
  const conn = getRedisConnection();
  await conn.publish(outputChannel(tenantId), JSON.stringify(data));
}
