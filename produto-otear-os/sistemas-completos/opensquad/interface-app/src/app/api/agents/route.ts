import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const SQUADS_DIR = path.join(ROOT, "squads");

interface AgentData {
  id: string;
  name: string;
  displayName: string;
  squad: string;
  role: "ceo" | "manager" | "ic";
  description: string;
  filePath: string | null;
  active: boolean;
  reportsTo: string | null;
  lastMessage: string;
  task: string;
}

/**
 * GET /api/agents
 * Scans squads directory for agents and reads state.json for live status.
 * Used by the 3D office dashboard.
 */
export async function GET() {
  const agents: AgentData[] = [];

  // CEO node
  agents.push({
    id: "ceo",
    name: "CEO",
    displayName: "Orchestrator",
    squad: "core",
    role: "ceo",
    description: "Pipeline Runner — Orquestra todos os agentes",
    filePath: null,
    active: false,
    reportsTo: null,
    lastMessage: "",
    task: "",
  });

  if (!fs.existsSync(SQUADS_DIR)) {
    return NextResponse.json(agents, { headers: corsHeaders() });
  }

  // Read all squads
  const squadDirs = fs.readdirSync(SQUADS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory());

  // Collect live state from all state.json files
  const liveAgents = new Map<string, { status: string; stepLabel: string }>();
  let anyRunning = false;

  for (const squadDir of squadDirs) {
    const squadName = squadDir.name;
    const agentsDir = path.join(SQUADS_DIR, squadName, "agents");
    const statePath = path.join(SQUADS_DIR, squadName, "state.json");

    // Read live state — only trust it if recently updated (< 5 min)
    if (fs.existsSync(statePath)) {
      try {
        const stat = fs.statSync(statePath);
        const ageMs = Date.now() - stat.mtimeMs;
        const isStale = ageMs > 5 * 60 * 1000; // 5 minutes

        const state = JSON.parse(fs.readFileSync(statePath, "utf-8"));

        // Only consider running if state was recently updated
        if (state.status === "running" && !isStale) {
          anyRunning = true;

          if (state.agents && Array.isArray(state.agents)) {
            for (const a of state.agents) {
              liveAgents.set(a.id || a.name, {
                status: a.status || "idle",
                stepLabel: state.step?.label || "",
              });
            }
          }
        }
        // If state says completed/checkpoint, or is stale, agents stay idle
      } catch { /* skip bad state */ }
    }

    // Scan agent .md files
    if (!fs.existsSync(agentsDir)) continue;

    const mdFiles = fs.readdirSync(agentsDir)
      .filter(f => f.endsWith(".md") && !f.startsWith("README"));

    for (const file of mdFiles) {
      const filePath = path.join(agentsDir, file);
      let name = file.replace(/\.agent\.md$/, "").replace(/\.md$/, "");

      // Extract display name from first heading
      let displayName = name;
      let description = "";
      try {
        const content = fs.readFileSync(filePath, "utf-8");
        const headingMatch = content.match(/^#\s+(.+)/m);
        if (headingMatch) {
          const h = headingMatch[1].replace(/[*_`]/g, "").trim();
          if (h.length <= 40) displayName = h;
        }
        // First non-heading, non-empty line as description
        for (const line of content.split("\n")) {
          const t = line.trim();
          if (t.length > 15 && !t.startsWith("#") && !t.startsWith("---") && !t.startsWith(">")) {
            description = t.replace(/^[-*>\s]+/, "").substring(0, 120);
            break;
          }
        }
      } catch { /* ignore */ }

      const live = liveAgents.get(name);
      const isActive = live ? (live.status === "working" || live.status === "delivering" || live.status === "checkpoint") : false;

      agents.push({
        id: `${squadName}/${name}`,
        name,
        displayName,
        squad: squadName,
        role: detectRole(name),
        description,
        filePath: filePath.replace(/\\/g, "/"),
        active: isActive,
        reportsTo: "ceo",
        lastMessage: live ? (live.status === "working" ? `Trabalhando — ${live.stepLabel}` : live.status) : "",
        task: live?.stepLabel || "",
      });
    }
  }

  // Mark CEO as active if any squad is running
  if (anyRunning) {
    agents[0].active = true;
    agents[0].lastMessage = "Orquestrando pipeline...";
  }

  return NextResponse.json(agents, { headers: corsHeaders() });
}

function detectRole(name: string): "ceo" | "manager" | "ic" {
  const n = name.toLowerCase();
  if (n.includes("lead") || n.includes("director") || n.includes("manager") || n.includes("chief")) {
    return "manager";
  }
  return "ic";
}

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": "no-store",
  };
}
