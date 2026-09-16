import { useEffect, useRef } from "react";
import { useSquadStore } from "@/store/useSquadStore";
import type { WsMessage } from "@/types/state";

const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30000;

/** Build WebSocket URL — supports SaaS mode via URL params */
function getWsUrl(): string {
  // Check URL params first (SaaS mode via iframe)
  const params = new URLSearchParams(window.location.search);
  const wsParam = params.get("ws");
  if (wsParam) return wsParam;

  const tenantId = params.get("tenant");
  if (tenantId) {
    // Connect to ws-gateway on port 3001 with tenant
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsPort = params.get("wsPort") || "3001";
    return `${protocol}//${window.location.hostname}:${wsPort}/ws/office/${tenantId}`;
  }

  // Default: same host (dev mode with Vite plugin)
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/__squads_ws`;
}

export function useSquadSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectDelayRef = useRef(RECONNECT_BASE_MS);

  const {
    setConnected,
    setSnapshot,
    setSquadActive,
    updateSquadState,
    setSquadInactive,
  } = useSquadStore();

  useEffect(() => {
    let disposed = false;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      if (disposed) return;

      const url = getWsUrl();
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectDelayRef.current = RECONNECT_BASE_MS;
      };

      ws.onmessage = (event) => {
        try {
          const msg: WsMessage = JSON.parse(event.data);
          switch (msg.type) {
            case "SNAPSHOT":
              setSnapshot(msg.squads, msg.activeStates);
              break;
            case "SQUAD_ACTIVE":
              setSquadActive(msg.squad, msg.state);
              break;
            case "SQUAD_UPDATE":
              updateSquadState(msg.squad, msg.state);
              break;
            case "SQUAD_INACTIVE":
              setSquadInactive(msg.squad);
              break;
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (!disposed) {
          reconnectTimer = setTimeout(() => {
            reconnectDelayRef.current = Math.min(
              reconnectDelayRef.current * 2,
              RECONNECT_MAX_MS
            );
            connect();
          }, reconnectDelayRef.current);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    // Listen for parent iframe messages (SaaS connect)
    function handleMessage(e: MessageEvent) {
      if (e.data?.type === "saas-connect" && e.data.wsUrl) {
        // Reconnect with the provided URL
        wsRef.current?.close();
        const url = e.data.wsUrl;
        const ws = new WebSocket(url);
        wsRef.current = ws;
        ws.onopen = () => setConnected(true);
        ws.onmessage = (event) => {
          try {
            const msg: WsMessage = JSON.parse(event.data);
            switch (msg.type) {
              case "SNAPSHOT": setSnapshot(msg.squads, msg.activeStates); break;
              case "SQUAD_ACTIVE": setSquadActive(msg.squad, msg.state); break;
              case "SQUAD_UPDATE": updateSquadState(msg.squad, msg.state); break;
              case "SQUAD_INACTIVE": setSquadInactive(msg.squad); break;
            }
          } catch {}
        };
        ws.onclose = () => setConnected(false);
      }
    }
    window.addEventListener("message", handleMessage);

    connect();

    return () => {
      disposed = true;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
      window.removeEventListener("message", handleMessage);
    };
  }, [setConnected, setSnapshot, setSquadActive, updateSquadState, setSquadInactive]);
}
