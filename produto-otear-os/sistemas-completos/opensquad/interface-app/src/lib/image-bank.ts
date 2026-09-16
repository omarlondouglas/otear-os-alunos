import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import fs from "fs";
import path from "path";

function getS3() {
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

function isConfigured(): boolean {
  const key = process.env.S3_ACCESS_KEY || process.env.S3_ACCESS_KEY_ID;
  const secret = process.env.S3_SECRET_KEY || process.env.S3_SECRET_ACCESS_KEY;
  const bucket = process.env.S3_BUCKET_NAME || process.env.S3_BUCKET;
  return !!(bucket && key && secret);
}

/**
 * Auto-save generated AI images from a pipeline run to the R2 image bank.
 * Reads carousel-content.md to get context for description/tags.
 * Each image gets a .meta.json alongside in R2.
 */
export async function autoSaveImagesToBank(
  runDir: string,
  topic: string,
  log: (msg: string) => void
): Promise<number> {
  if (!isConfigured()) return 0;

  // Find images/ folder in the run dir (or versioned subdir)
  const imagesDir = findImagesDir(runDir);
  if (!imagesDir) return 0;

  const imageFiles = fs.readdirSync(imagesDir)
    .filter((f) => /\.(png|jpg|jpeg)$/i.test(f))
    .sort();

  if (imageFiles.length === 0) return 0;

  // Read carousel-content.md for slide descriptions
  const slideDescriptions = extractSlideDescriptions(runDir);

  const client = getS3();
  const bucket = getBucket();
  let saved = 0;

  // Derive category from topic
  const categoria = topic
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .slice(0, 30) || "geral";

  for (const file of imageFiles) {
    const filePath = path.join(imagesDir, file);
    const imageBuffer = fs.readFileSync(filePath);
    const ext = path.extname(file).replace(".", "").replace("jpeg", "jpg");
    const mime = ext === "png" ? "image/png" : "image/jpeg";

    // Match slide number from filename (e.g., img-slide-01.png → slide 1)
    const slideMatch = file.match(/(\d+)/);
    const slideNum = slideMatch ? parseInt(slideMatch[1], 10) : 0;
    const slideDesc = slideDescriptions[slideNum] || slideDescriptions[1] || topic;

    // Build description from slide content
    const description = `${topic} — ${slideDesc}`.slice(0, 200);
    const tags = extractTags(topic, slideDesc);

    const ts = Date.now();
    const slug = description
      .toLowerCase()
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .slice(0, 50);
    const r2Key = `image-bank/${categoria}/${ts}-${slug}.${ext}`;
    const metaKey = `image-bank/${categoria}/${ts}-${slug}.meta.json`;

    try {
      // Upload image
      await client.send(new PutObjectCommand({
        Bucket: bucket,
        Key: r2Key,
        Body: imageBuffer,
        ContentType: mime,
        CacheControl: "public, max-age=31536000",
      }));

      // Upload metadata
      await client.send(new PutObjectCommand({
        Bucket: bucket,
        Key: metaKey,
        Body: JSON.stringify({
          description,
          tags,
          categoria,
          r2Key,
          sourceFile: file,
          topic,
          savedAt: new Date().toISOString(),
        }, null, 2),
        ContentType: "application/json",
      }));

      saved++;
      log(`[banco] Salvo: ${file} → ${r2Key}`);
    } catch (err) {
      log(`[banco] Erro ao salvar ${file}: ${err}`);
    }
  }

  return saved;
}

function findImagesDir(runDir: string): string | null {
  // Check runDir/images, runDir/v1/images, etc.
  const direct = path.join(runDir, "images");
  if (fs.existsSync(direct)) return direct;

  const entries = fs.readdirSync(runDir, { withFileTypes: true })
    .filter((e) => e.isDirectory());

  for (const entry of entries) {
    const sub = path.join(runDir, entry.name, "images");
    if (fs.existsSync(sub)) return sub;
  }

  return null;
}

function extractSlideDescriptions(runDir: string): Record<number, string> {
  const descriptions: Record<number, string> = {};

  // Try carousel-content.md in runDir or v1/
  const candidates = [
    path.join(runDir, "carousel-content.md"),
    path.join(runDir, "v1", "carousel-content.md"),
  ];

  let content = "";
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      content = fs.readFileSync(p, "utf-8");
      break;
    }
  }

  if (!content) return descriptions;

  // Parse slide headlines from markdown
  const lines = content.split("\n");
  let currentSlide = 0;
  for (const line of lines) {
    const slideMatch = line.match(/^##\s+(?:Slide\s+)?(\d+)/i);
    if (slideMatch) {
      currentSlide = parseInt(slideMatch[1], 10);
      // Use the rest of the line as description
      const label = line.replace(/^##\s+(?:Slide\s+)?\d+[\s—:-]*/i, "").trim();
      if (label) descriptions[currentSlide] = label;
    } else if (currentSlide && !descriptions[currentSlide] && line.trim() && !line.startsWith("#")) {
      // First non-empty line after slide header
      descriptions[currentSlide] = line.replace(/^\*+\s*/, "").replace(/\*+/g, "").trim().slice(0, 100);
    }
  }

  return descriptions;
}

function extractTags(topic: string, description: string): string[] {
  const combined = `${topic} ${description}`.toLowerCase();
  const words = combined
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 3);

  // Deduplicate and take top 8
  return [...new Set(words)].slice(0, 8);
}
