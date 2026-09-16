import path from "path";

const DATA_ROOT = process.env.DATA_ROOT || path.resolve(process.cwd(), "..", "data");

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Returns the root directory for a tenant's data. Validates tenantId to prevent path traversal. */
export function tenantRoot(tenantId: string): string {
  if (!UUID_RE.test(tenantId)) {
    throw new Error(`Invalid tenant ID: ${tenantId}`);
  }
  const resolved = path.resolve(DATA_ROOT, tenantId);
  // Double-check resolved path is inside DATA_ROOT
  if (!resolved.startsWith(path.resolve(DATA_ROOT))) {
    throw new Error("Path traversal detected");
  }
  return resolved;
}

/** Returns the squads directory for a tenant */
export function tenantSquadsDir(tenantId: string): string {
  return path.join(tenantRoot(tenantId), "squads");
}

/** Returns the path for a specific squad within a tenant */
export function tenantSquadDir(tenantId: string, squadCode: string): string {
  // Sanitize squadCode
  const safe = squadCode.replace(/[^a-z0-9-]/gi, "");
  return path.join(tenantSquadsDir(tenantId), safe);
}

/** Returns the output directory for a squad run */
export function tenantOutputDir(tenantId: string, squadCode: string): string {
  return path.join(tenantSquadDir(tenantId, squadCode), "output");
}

/** Returns the state.json path for a squad */
export function tenantStatePath(tenantId: string, squadCode: string): string {
  return path.join(tenantSquadDir(tenantId, squadCode), "state.json");
}

/** Returns the memory directory for a tenant */
export function tenantMemoryDir(tenantId: string): string {
  return path.join(tenantRoot(tenantId), "_opensquad", "_memory");
}

export { DATA_ROOT };
