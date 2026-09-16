import {
  S3Client,
  PutObjectCommand,
  ListObjectsV2Command,
  GetObjectCommand,
} from "@aws-sdk/client-s3";
import fs from "fs";
import path from "path";

function getClient(): S3Client {
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

function getBucket(): string {
  return (process.env.S3_BUCKET_NAME || process.env.S3_BUCKET)!;
}

export function getPublicBaseUrl(): string {
  return getPublicBase();
}

function getPublicBase(): string {
  const bucket = getBucket();
  return process.env.S3_PUBLIC_URL || `https://${bucket}.s3.amazonaws.com`;
}

export function isS3Configured(): boolean {
  const key = process.env.S3_ACCESS_KEY || process.env.S3_ACCESS_KEY_ID;
  const secret = process.env.S3_SECRET_KEY || process.env.S3_SECRET_ACCESS_KEY;
  const bucket = process.env.S3_BUCKET_NAME || process.env.S3_BUCKET;
  return !!(bucket && key && secret);
}

const MIME: Record<string, string> = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".html": "text/html",
  ".json": "application/json",
  ".md": "text/markdown",
};

/** Find all uploadable files recursively */
function findFiles(dir: string, exts: string[]): string[] {
  const results: string[] = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...findFiles(full, exts));
    } else {
      const ext = path.extname(entry.name).toLowerCase();
      if (exts.includes(ext)) results.push(full);
    }
  }
  return results;
}

/** Upload all relevant files from a run directory to S3 */
export async function uploadRunToS3(
  runDir: string,
  runId: string
): Promise<{ key: string; url: string }[]> {
  if (!isS3Configured()) return [];

  const bucket = getBucket();
  const publicBase = getPublicBase();
  const client = getClient();
  const uploaded: { key: string; url: string }[] = [];

  // Upload slides (HTML + images), carousel-content.md, and generated images
  const files = findFiles(runDir, [".jpg", ".jpeg", ".png", ".html", ".md"]);

  for (const filePath of files) {
    const relative = path.relative(runDir, filePath).replace(/\\/g, "/");
    const key = `noticias-carrossel-ia/${runId}/${relative}`;
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME[ext] || "application/octet-stream";

    const buffer = fs.readFileSync(filePath);
    await client.send(
      new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: buffer,
        ContentType: contentType,
        CacheControl: ext === ".md" ? "no-cache" : "public, max-age=31536000",
      })
    );

    uploaded.push({ key, url: `${publicBase}/${key}` });
  }

  // Also upload a manifest.json with structured content data
  const contentFile = findCarouselContentFile(runDir);
  if (contentFile) {
    const raw = fs.readFileSync(contentFile, "utf-8");
    const parsed = parseCarouselContent(raw);
    const manifestKey = `noticias-carrossel-ia/${runId}/manifest.json`;
    await client.send(
      new PutObjectCommand({
        Bucket: bucket,
        Key: manifestKey,
        Body: JSON.stringify({ ...parsed, runId, uploadedAt: new Date().toISOString() }),
        ContentType: "application/json",
        CacheControl: "no-cache",
      })
    );
    uploaded.push({ key: manifestKey, url: `${publicBase}/${manifestKey}` });
  }

  return uploaded;
}

function findCarouselContentFile(dir: string): string | null {
  // Check dir/carousel-content.md and dir/v*/carousel-content.md
  const direct = path.join(dir, "carousel-content.md");
  if (fs.existsSync(direct)) return direct;
  const entries = fs.readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && /^v\d+$/i.test(e.name))
    .map((e) => e.name).sort().reverse();
  for (const v of entries) {
    const p = path.join(dir, v, "carousel-content.md");
    if (fs.existsSync(p)) return p;
  }
  return null;
}

function parseCarouselContent(raw: string) {
  const slides: Record<string, string>[] = [];
  let caption = "";
  let hashtags = "";

  const slidesMatch = raw.match(/=== SLIDES ===([\s\S]*?)(?:=== CAPTION ===|$)/);
  if (slidesMatch) {
    const slideBlocks = slidesMatch[1].split(/\nSlide \d+/).filter(Boolean);
    for (const block of slideBlocks) {
      const labelMatch = block.match(/^\s*\(([^)]+)\)/);
      const slide: Record<string, string> = {};
      if (labelMatch) slide.label = labelMatch[1];
      const fieldRegex = /^\s{2}(\w[\w\s]*?):\s*(.+)$/gm;
      let m;
      while ((m = fieldRegex.exec(block)) !== null) {
        const key = m[1].trim().toLowerCase().replace(/\s+/g, "_");
        slide[key] = m[2].trim();
      }
      if (Object.keys(slide).length > 0) slides.push(slide);
    }
  }

  const captionMatch = raw.match(/=== CAPTION ===([\s\S]*?)(?:=== HASHTAGS ===|$)/);
  if (captionMatch) caption = captionMatch[1].trim();

  const hashtagsMatch = raw.match(/=== HASHTAGS ===([\s\S]*?)$/);
  if (hashtagsMatch) hashtags = hashtagsMatch[1].trim();

  return { slides, caption, hashtags };
}

/** List carousels from S3 — prefer manifest.json for structured data */
export async function listCarouselsFromS3(): Promise<
  { id: string; version: string; date: string; topic: string; slides: string[]; slideType: "image" | "html"; content?: Record<string, string>[] }[]
> {
  if (!isS3Configured()) return [];

  const bucket = getBucket();
  const publicBase = getPublicBase();
  const client = getClient();

  const res = await client.send(
    new ListObjectsV2Command({
      Bucket: bucket,
      Prefix: "noticias-carrossel-ia/",
    })
  );

  // Group files by runId
  const runs = new Map<string, { htmlSlides: string[]; jpgSlides: string[]; images: string[]; hasManifest: boolean }>();

  for (const obj of res.Contents || []) {
    const key = obj.Key!;
    const parts = key.split("/");
    if (parts.length < 3) continue;
    const runId = parts[1];

    if (!runs.has(runId)) runs.set(runId, { htmlSlides: [], jpgSlides: [], images: [], hasManifest: false });
    const run = runs.get(runId)!;

    const filename = parts[parts.length - 1];
    if (filename === "manifest.json") {
      run.hasManifest = true;
    } else if (/^slide-\d+\.html$/i.test(filename)) {
      run.htmlSlides.push(`${publicBase}/${key}`);
    } else if (/^slide-\d+\.(jpg|jpeg|png)$/i.test(filename)) {
      run.jpgSlides.push(`${publicBase}/${key}`);
    } else if (/^img-slide-\d+\.(jpg|jpeg|png)$/i.test(filename)) {
      run.images.push(`${publicBase}/${key}`);
    }
  }

  const carousels = [];

  for (const [runId, run] of Array.from(runs.entries()).sort((a, b) => b[0].localeCompare(a[0]))) {
    // Prefer rendered JPGs > HTML slides > raw images
    let slides: string[];
    let slideType: "image" | "html";

    if (run.jpgSlides.length > 0) {
      slides = run.jpgSlides.sort();
      slideType = "image";
    } else if (run.htmlSlides.length > 0) {
      slides = run.htmlSlides.sort();
      slideType = "html";
    } else if (run.images.length > 0) {
      slides = run.images.sort();
      slideType = "image";
    } else {
      continue;
    }

    // Try to load manifest for topic
    let topic = "";
    let content: Record<string, string>[] | undefined;
    if (run.hasManifest) {
      try {
        const manifestRes = await client.send(
          new GetObjectCommand({ Bucket: bucket, Key: `noticias-carrossel-ia/${runId}/manifest.json` })
        );
        const body = await manifestRes.Body?.transformToString();
        if (body) {
          const manifest = JSON.parse(body);
          content = manifest.slides;
          if (manifest.slides?.[0]?.title) topic = manifest.slides[0].title;
        }
      } catch { /* ignore */ }
    }

    carousels.push({
      id: runId,
      version: "",
      date: runId,
      topic,
      slides,
      slideType,
      content,
    });
  }

  return carousels;
}

/** Fetch slides-data.json from S3 for a given runId */
export async function fetchSlidesJsonFromS3(runId: string): Promise<{ slides: unknown[] } | null> {
  if (!isS3Configured()) return null;

  const client = getClient();
  const bucket = getBucket();

  // Try common paths
  const candidates = [
    `noticias-carrossel-ia/${runId}/slides-data.json`,
    `noticias-carrossel-ia/${runId}/v1/slides-data.json`,
  ];

  for (const key of candidates) {
    try {
      const res = await client.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
      const body = await res.Body?.transformToString();
      if (body) return JSON.parse(body);
    } catch { /* not found, try next */ }
  }

  return null;
}

/** Save slides-data.json back to S3 */
export async function saveSlidesJsonToS3(runId: string, data: unknown): Promise<boolean> {
  if (!isS3Configured()) return false;

  const client = getClient();
  const bucket = getBucket();

  // Try to find existing path first
  const candidates = [
    `noticias-carrossel-ia/${runId}/v1/slides-data.json`,
    `noticias-carrossel-ia/${runId}/slides-data.json`,
  ];

  for (const key of candidates) {
    try {
      // Check if exists
      await client.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
      // Overwrite
      await client.send(new PutObjectCommand({
        Bucket: bucket,
        Key: key,
        Body: JSON.stringify(data, null, 2),
        ContentType: "application/json",
      }));
      return true;
    } catch { /* try next */ }
  }

  // Default: save to runId root
  try {
    await client.send(new PutObjectCommand({
      Bucket: bucket,
      Key: candidates[0],
      Body: JSON.stringify(data, null, 2),
      ContentType: "application/json",
    }));
    return true;
  } catch {
    return false;
  }
}
