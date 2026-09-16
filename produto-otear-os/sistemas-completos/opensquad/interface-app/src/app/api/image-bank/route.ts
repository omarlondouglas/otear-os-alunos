import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import { isS3Configured } from "@/lib/s3";

const ROOT = process.env.OPENSQUAD_ROOT || path.resolve(process.cwd(), "..");
const LOCAL_BANK_DIR = path.join(ROOT, "_opensquad", "_image-bank");

// ─── S3 helpers (only used when configured) ──────────────────

function getS3() {
  const { S3Client } = require("@aws-sdk/client-s3");
  const endpoint = process.env.S3_ENDPOINT_URL || process.env.S3_ENDPOINT;
  return new S3Client({
    region: process.env.S3_REGION || "auto",
    endpoint,
    credentials: {
      accessKeyId: (process.env.S3_ACCESS_KEY || process.env.S3_ACCESS_KEY_ID)!,
      secretAccessKey: (process.env.S3_SECRET_KEY || process.env.S3_SECRET_ACCESS_KEY)!,
    },
    ...(endpoint ? { forcePathStyle: true } : {}),
  });
}

function getBucket() {
  return (process.env.S3_BUCKET_NAME || process.env.S3_BUCKET)!;
}

function getPublicBase() {
  return process.env.S3_PUBLIC_URL || `https://${getBucket()}.s3.amazonaws.com`;
}

// ─── Upload helpers ──────────────────────────────────────────

function generateFilename(description: string, ext: string): { filename: string; slug: string; ts: number } {
  const ts = Date.now();
  const slug = description
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .slice(0, 50);
  return { filename: `${ts}-${slug}.${ext}`, slug, ts };
}

function readImageBuffer(body: { imagePath?: string; imageBase64?: string }): { buffer: Buffer; ext: string } | null {
  if (body.imageBase64) {
    const raw = body.imageBase64.replace(/^data:image\/\w+;base64,/, "");
    const ext = body.imageBase64.includes("image/png") ? "png" : "jpg";
    return { buffer: Buffer.from(raw, "base64"), ext };
  }
  if (body.imagePath) {
    const fullPath = path.isAbsolute(body.imagePath)
      ? body.imagePath
      : path.join(ROOT, body.imagePath);
    if (!fs.existsSync(fullPath)) return null;
    const ext = path.extname(fullPath).replace(".", "").replace("jpeg", "jpg") || "jpg";
    return { buffer: fs.readFileSync(fullPath), ext };
  }
  return null;
}

// ─── Local storage implementation ────────────────────────────

async function saveLocal(
  imageBuffer: Buffer,
  ext: string,
  description: string,
  tags: string[],
  categoria: string
) {
  const catDir = path.join(LOCAL_BANK_DIR, categoria);
  fs.mkdirSync(catDir, { recursive: true });

  const { filename, slug, ts } = generateFilename(description, ext);
  const imagePath = path.join(catDir, filename);
  const metaPath = path.join(catDir, `${ts}-${slug}.meta.json`);

  fs.writeFileSync(imagePath, imageBuffer);
  fs.writeFileSync(metaPath, JSON.stringify({
    description,
    tags,
    categoria,
    filename,
    savedAt: new Date().toISOString(),
  }, null, 2));

  return { filename, categoria };
}

async function listLocal(categoria: string, limit: number) {
  const images: { url: string; description: string; tags: string[]; categoria: string; filename: string }[] = [];

  const searchDirs = categoria
    ? [path.join(LOCAL_BANK_DIR, categoria)]
    : (() => {
        if (!fs.existsSync(LOCAL_BANK_DIR)) return [];
        return fs.readdirSync(LOCAL_BANK_DIR, { withFileTypes: true })
          .filter(d => d.isDirectory())
          .map(d => path.join(LOCAL_BANK_DIR, d.name));
      })();

  for (const dir of searchDirs) {
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter(f => f.endsWith(".meta.json"));

    for (const metaFile of files) {
      try {
        const meta = JSON.parse(fs.readFileSync(path.join(dir, metaFile), "utf-8"));
        const cat = meta.categoria || path.basename(dir);
        const imageFile = meta.filename || metaFile.replace(".meta.json", ".jpg");
        const imagePath = path.join(dir, imageFile);

        if (!fs.existsSync(imagePath)) continue;

        images.push({
          url: `/api/image-bank/file?path=${encodeURIComponent(`${cat}/${imageFile}`)}`,
          description: meta.description || "",
          tags: meta.tags || [],
          categoria: cat,
          filename: imageFile,
        });
      } catch { /* skip broken meta */ }
    }
  }

  // Sort by timestamp (filename starts with timestamp)
  images.sort((a, b) => b.filename.localeCompare(a.filename));
  return images.slice(0, limit);
}

// ─── R2/S3 storage implementation ────────────────────────────

async function saveToR2(
  imageBuffer: Buffer,
  ext: string,
  description: string,
  tags: string[],
  categoria: string
) {
  const { PutObjectCommand } = require("@aws-sdk/client-s3");
  const { filename, slug, ts } = generateFilename(description, ext);
  const r2Key = `image-bank/${categoria}/${filename}`;
  const metaKey = `image-bank/${categoria}/${ts}-${slug}.meta.json`;

  const client = getS3();
  const bucket = getBucket();

  await client.send(new PutObjectCommand({
    Bucket: bucket,
    Key: r2Key,
    Body: imageBuffer,
    ContentType: ext === "png" ? "image/png" : "image/jpeg",
    CacheControl: "public, max-age=31536000",
  }));

  await client.send(new PutObjectCommand({
    Bucket: bucket,
    Key: metaKey,
    Body: JSON.stringify({ description, tags, categoria, r2Key, savedAt: new Date().toISOString() }, null, 2),
    ContentType: "application/json",
  }));

  return { r2Key, urlPublica: `${getPublicBase()}/${r2Key}` };
}

async function listFromR2(categoria: string, limit: number) {
  const { ListObjectsV2Command, GetObjectCommand } = require("@aws-sdk/client-s3");
  const client = getS3();
  const bucket = getBucket();
  const publicBase = getPublicBase();
  const prefix = categoria ? `image-bank/${categoria}/` : "image-bank/";

  const res = await client.send(new ListObjectsV2Command({
    Bucket: bucket,
    Prefix: prefix,
    MaxKeys: 500,
  }));

  const images: { url: string; description: string; tags: string[]; categoria: string; r2Key: string }[] = [];

  const metaFiles = (res.Contents || [])
    .filter((o: any) => o.Key?.endsWith(".meta.json"))
    .sort((a: any, b: any) => (b.LastModified?.getTime() || 0) - (a.LastModified?.getTime() || 0))
    .slice(0, limit);

  for (const obj of metaFiles) {
    try {
      const metaRes = await client.send(new GetObjectCommand({ Bucket: bucket, Key: obj.Key! }));
      const metaBody = await metaRes.Body?.transformToString();
      if (metaBody) {
        const meta = JSON.parse(metaBody);
        images.push({
          r2Key: meta.r2Key,
          url: `${publicBase}/${meta.r2Key}`,
          description: meta.description || "",
          tags: meta.tags || [],
          categoria: meta.categoria || "",
        });
      }
    } catch { /* skip broken meta */ }
  }

  return images;
}

// ─── API Routes ──────────────────────────────────────────────

/**
 * POST /api/image-bank
 * Body: { imagePath?, imageBase64?, description, tags[], categoria }
 */
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { description, tags = [], categoria = "geral" } = body as {
    imagePath?: string;
    imageBase64?: string;
    description: string;
    tags: string[];
    categoria: string;
  };

  if (!description) {
    return NextResponse.json({ error: "Descricao obrigatoria" }, { status: 400 });
  }

  const imageData = readImageBuffer(body);
  if (!imageData) {
    return NextResponse.json({ error: "imagePath ou imageBase64 obrigatorio" }, { status: 400 });
  }

  try {
    if (isS3Configured()) {
      const result = await saveToR2(imageData.buffer, imageData.ext, description, tags, categoria);
      return NextResponse.json({ ok: true, ...result, description, tags, categoria });
    } else {
      const result = await saveLocal(imageData.buffer, imageData.ext, description, tags, categoria);
      return NextResponse.json({
        ok: true,
        url: `/api/image-bank/file?path=${encodeURIComponent(`${result.categoria}/${result.filename}`)}`,
        description, tags, categoria,
      });
    }
  } catch (err) {
    return NextResponse.json({ error: `Erro ao salvar: ${err}` }, { status: 500 });
  }
}

/**
 * GET /api/image-bank?categoria=X&limit=20
 */
export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const categoria = url.searchParams.get("categoria") || "";
  const limit = parseInt(url.searchParams.get("limit") || "30", 10);

  try {
    if (isS3Configured()) {
      const images = await listFromR2(categoria, limit);
      return NextResponse.json({ images });
    } else {
      const images = await listLocal(categoria, limit);
      return NextResponse.json({ images });
    }
  } catch (err) {
    return NextResponse.json({ images: [], error: String(err) });
  }
}
