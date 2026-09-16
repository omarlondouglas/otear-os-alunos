/**
 * WebSocket Gateway for tenant-scoped real-time updates.
 *
 * Speaks the dashboard protocol (SNAPSHOT, SQUAD_UPDATE, etc.)
 * so the PixiJS dashboard can connect directly.
 *
 * Also accepts connections on /__squads_ws (dashboard default path)
 * and /ws/office/{tenantId} (SaaS path).
 */

import { WebSocketServer, WebSocket } from "ws";
import IORedis from "ioredis";
import { createServer, type IncomingMessage } from "http";
import { parse } from "url";

const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";
const WS_PORT = parseInt(process.env.WS_PORT || "3001", 10);

// ── Tenant Connection Map ────────────────────────────────────

const tenantClients = new Map<string, Set<WebSocket>>();

function addClient(tenantId: string, ws: WebSocket): void {
  if (!tenantClients.has(tenantId)) {
    tenantClients.set(tenantId, new Set());
  }
  tenantClients.get(tenantId)!.add(ws);
}

function removeClient(tenantId: string, ws: WebSocket): void {
  const clients = tenantClients.get(tenantId);
  if (clients) {
    clients.delete(ws);
    if (clients.size === 0) {
      tenantClients.delete(tenantId);
    }
  }
}

function broadcast(tenantId: string, data: string): void {
  const clients = tenantClients.get(tenantId);
  if (!clients) return;
  for (const ws of clients) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  }
}

// ── Redis Subscriber ─────────────────────────────────────────

let sub: IORedis | null = null;

try {
  sub = new IORedis(REDIS_URL, { maxRetriesPerRequest: null, lazyConnect: true });
  sub.connect().then(() => {
    sub!.psubscribe("tenant:*:state", "tenant:*:output");
    console.log("[ws-gateway] Redis connected");
  }).catch(() => {
    console.log("[ws-gateway] Redis not available, running without pub/sub");
    sub = null;
  });
} catch {
  console.log("[ws-gateway] Redis not configured");
}

if (sub) {
  sub.on("pmessage", (_pattern, channel, message) => {
    const parts = channel.split(":");
    if (parts.length < 3) return;
    const tenantId = parts[1];

    try {
      const msg = JSON.parse(message);

      // Translate worker messages to dashboard protocol
      if (msg.type === "state" && msg.state) {
        const dashMsg = JSON.stringify({
          type: "SQUAD_UPDATE",
          squad: msg.state.squad || "carousel",
          state: msg.state,
        });
        broadcast(tenantId, dashMsg);
      } else if (msg.type === "job-started") {
        broadcast(tenantId, JSON.stringify({
          type: "SQUAD_ACTIVE",
          squad: "carousel",
          state: {
            squad: "carousel",
            status: "running",
            step: { current: 0, total: 10, label: "Iniciando..." },
            agents: [],
            handoff: null,
            startedAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        }));
      } else if (msg.type === "job-completed") {
        broadcast(tenantId, JSON.stringify({
          type: "SQUAD_INACTIVE",
          squad: "carousel",
        }));
      } else {
        // Forward as-is for other consumers
        broadcast(tenantId, message);
      }
    } catch {
      broadcast(tenantId, message);
    }
  });
}

// ── WebSocket Server ─────────────────────────────────────────

function extractTenantId(req: IncomingMessage): string | null {
  const url = parse(req.url || "", true);
  const pathname = url.pathname || "";

  // SaaS path: /ws/office/{tenantId}
  const saasMatch = pathname.match(/^\/ws\/office\/([a-f0-9-]+)$/i);
  if (saasMatch) return saasMatch[1];

  // Dashboard path: /__squads_ws?tenant={tenantId}
  if (pathname === "/__squads_ws" || pathname === "/") {
    return (url.query?.tenant as string) || "default";
  }

  return "default";
}

const server = createServer((_req, res) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "ok", connections: tenantClients.size }));
});

const wss = new WebSocketServer({ server });

wss.on("connection", (ws, req) => {
  const tenantId = extractTenantId(req) || "default";

  console.log(`[ws-gateway] Client connected (tenant: ${tenantId})`);
  addClient(tenantId, ws);

  // Send initial SNAPSHOT (empty squads, dashboard will populate from state updates)
  ws.send(JSON.stringify({
    type: "SNAPSHOT",
    squads: [{
      code: "carousel",
      name: "Carrossel de Noticias",
      description: "Cria carrosseis de noticias com IA",
      icon: "📰",
      agents: [],
    }],
    activeStates: {},
  }));

  ws.on("close", () => {
    removeClient(tenantId, ws);
  });

  ws.on("error", (err) => {
    console.error(`[ws-gateway] Error (tenant: ${tenantId}):`, err.message);
    removeClient(tenantId, ws);
  });
});

// ── Start ────────────────────────────────────────────────────

if (require.main === module || process.argv[1]?.includes("ws-gateway")) {
  server.listen(WS_PORT, () => {
    console.log(`[ws-gateway] Listening on port ${WS_PORT}`);
  });
}

export { server, wss };
