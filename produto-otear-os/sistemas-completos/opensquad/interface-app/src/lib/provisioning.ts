import fs from "fs";
import path from "path";
import { tenantRoot, tenantSquadDir, tenantMemoryDir } from "./tenant";
import { supabase } from "./supabase";

const OPENSQUAD_ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");

/** Template squad source directory */
const TEMPLATE_SQUAD = path.join(OPENSQUAD_ROOT, "squads", "noticias-carrossel-ia");

/** Core opensquad files to copy */
const OPENSQUAD_CORE = path.join(OPENSQUAD_ROOT, "_opensquad");

interface ProvisionInput {
  tenantId: string;
  agencyName: string;
  niche: string;
  instagramHandle?: string;
  website?: string;
  referenceProfiles?: string[];
}

/** Copy a directory recursively, skipping output/ dirs */
function copyDirSync(src: string, dest: string, skipDirs: string[] = []) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    if (skipDirs.includes(entry.name)) continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath, skipDirs);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/** Provision a new tenant: create directory structure, clone squad template, init memory */
export async function provisionTenant(input: ProvisionInput): Promise<void> {
  const root = tenantRoot(input.tenantId);

  // 1. Create directory structure
  const dirs = [
    root,
    path.join(root, "squads"),
    path.join(root, "_opensquad", "_memory"),
    path.join(root, "_opensquad", "core"),
  ];
  dirs.forEach((d) => fs.mkdirSync(d, { recursive: true }));

  // 2. Clone squad template (skip output/ and _investigations/)
  const squadDest = tenantSquadDir(input.tenantId, "carousel");
  if (fs.existsSync(TEMPLATE_SQUAD)) {
    copyDirSync(TEMPLATE_SQUAD, squadDest, ["output", "_investigations"]);
    // Create empty output dir
    fs.mkdirSync(path.join(squadDest, "output"), { recursive: true });
  }

  // 3. Copy core opensquad files (runner, best-practices, skills engine)
  const coreSrc = path.join(OPENSQUAD_CORE, "core");
  const coreDest = path.join(root, "_opensquad", "core");
  if (fs.existsSync(coreSrc)) {
    copyDirSync(coreSrc, coreDest);
  }

  // 4. Copy skills directory
  const skillsSrc = path.join(OPENSQUAD_ROOT, "skills");
  const skillsDest = path.join(root, "skills");
  if (fs.existsSync(skillsSrc)) {
    copyDirSync(skillsSrc, skillsDest);
  }

  // 5. Initialize company.md with tenant brand info
  const memoryDir = tenantMemoryDir(input.tenantId);
  fs.mkdirSync(memoryDir, { recursive: true });
  const companyMd = `# Perfil da Empresa

## Nome
${input.agencyName}

## Nicho
${input.niche}

## Instagram
${input.instagramHandle || "(nao configurado)"}

## Website
${input.website || "(nao configurado)"}

## Tom de Voz
Profissional, acessivel, sem jargao tecnico. Adaptar ao nicho ${input.niche}.
`;
  fs.writeFileSync(path.join(memoryDir, "company.md"), companyMd, "utf-8");

  // 6. Initialize preferences
const prefsMd = `# Preferencias
- Idioma: pt-BR
- Formato padrao: instagram-feed
`;
  fs.writeFileSync(path.join(memoryDir, "preferences.md"), prefsMd, "utf-8");

  // 7. Save brand info to Supabase
  await supabase.client.from("tenant_brands").upsert(
    {
      tenant_id: input.tenantId,
      agency_name: input.agencyName,
      instagram_handle: input.instagramHandle || null,
      website: input.website || null,
      niche: input.niche,
      reference_profiles: input.referenceProfiles || [],
    },
    { onConflict: "tenant_id" }
  );
}

/** Create a new tenant in Supabase and provision filesystem */
export async function createTenant(
  userId: string,
  agencyName: string,
  niche: string,
  brand?: {
    instagramHandle?: string;
    website?: string;
    referenceProfiles?: string[];
  }
): Promise<string> {
  // 1. Create slug from agency name
  const slug = agencyName
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);

  // 2. Create tenant
  const { data: tenant, error: tenantErr } = await supabase.client
    .from("tenants")
    .insert({ name: agencyName, slug, plan: "free", runs_limit: 5 })
    .select()
    .single();

  if (tenantErr) throw new Error(`Failed to create tenant: ${tenantErr.message}`);

  // 3. Link user as owner
  await supabase.client.from("tenant_members").insert({
    tenant_id: tenant.id,
    user_id: userId,
    role: "owner",
  });

  // 4. Provision filesystem
  await provisionTenant({
    tenantId: tenant.id,
    agencyName,
    niche,
    instagramHandle: brand?.instagramHandle,
    website: brand?.website,
    referenceProfiles: brand?.referenceProfiles,
  });

  return tenant.id;
}
