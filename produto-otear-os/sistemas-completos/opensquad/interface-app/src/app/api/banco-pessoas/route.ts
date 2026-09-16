import { NextRequest, NextResponse } from "next/server";
import { buscarPessoa, salvarPessoa } from "@/lib/supabase";

function slugify(nome: string): string {
  return nome
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

/**
 * GET /api/banco-pessoas?nome=Sam+Altman
 * Returns cached photo URL or null
 */
export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const nome = url.searchParams.get("nome");

  if (!nome) {
    return NextResponse.json({ error: "Parametro 'nome' obrigatorio" }, { status: 400 });
  }

  const slug = slugify(nome);
  const pessoa = await buscarPessoa(slug);

  if (pessoa) {
    return NextResponse.json({ found: true, ...pessoa });
  }

  return NextResponse.json({ found: false, slug });
}

/**
 * POST /api/banco-pessoas
 * Body: { nome: "Sam Altman" }
 * Searches Google CSE, downloads best photo, saves to Supabase Storage
 */
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { nome } = body as { nome: string };

  if (!nome) {
    return NextResponse.json({ error: "Campo 'nome' obrigatorio" }, { status: 400 });
  }

  const slug = slugify(nome);

  // Check cache first
  const cached = await buscarPessoa(slug);
  if (cached) {
    return NextResponse.json({ found: true, cached: true, ...cached });
  }

  // Search Google Custom Search
  const apiKey = process.env.GOOGLE_CSE_API_KEY;
  const cx = process.env.GOOGLE_CSE_CX;

  if (!apiKey || !cx || apiKey === "SUA_CHAVE_AQUI") {
    return NextResponse.json(
      { error: "Google CSE nao configurado (GOOGLE_CSE_API_KEY / GOOGLE_CSE_CX)" },
      { status: 503 }
    );
  }

  const query = encodeURIComponent(`${nome} portrait photo high quality`);
  const cseUrl = `https://www.googleapis.com/customsearch/v1?key=${apiKey}&cx=${cx}&q=${query}&searchType=image&imgSize=large&num=3`;

  let imageUrl: string | null = null;

  try {
    const cseRes = await fetch(cseUrl);
    const cseData = await cseRes.json();

    if (cseData.items && cseData.items.length > 0) {
      imageUrl = cseData.items[0].link;
    }
  } catch (err) {
    return NextResponse.json({ error: `Erro ao buscar Google CSE: ${err}` }, { status: 502 });
  }

  if (!imageUrl) {
    return NextResponse.json({ found: false, error: "Nenhuma imagem encontrada" }, { status: 404 });
  }

  // Download the image
  let imageBuffer: Buffer;
  try {
    const imgRes = await fetch(imageUrl, {
      headers: { "User-Agent": "Mozilla/5.0" },
      signal: AbortSignal.timeout(10000),
    });
    if (!imgRes.ok) throw new Error(`HTTP ${imgRes.status}`);
    imageBuffer = Buffer.from(await imgRes.arrayBuffer());
  } catch (err) {
    // Try second result if first fails
    try {
      const cseRes = await fetch(cseUrl);
      const cseData = await cseRes.json();
      if (cseData.items?.[1]) {
        imageUrl = cseData.items[1].link;
        const imgRes = await fetch(imageUrl!, {
          headers: { "User-Agent": "Mozilla/5.0" },
          signal: AbortSignal.timeout(10000),
        });
        imageBuffer = Buffer.from(await imgRes.arrayBuffer());
      } else {
        return NextResponse.json({ error: `Erro ao baixar imagem: ${err}` }, { status: 502 });
      }
    } catch (err2) {
      return NextResponse.json({ error: `Erro ao baixar imagem: ${err2}` }, { status: 502 });
    }
  }

  // Validate minimum size (skip tiny/broken images)
  if (imageBuffer.length < 1000) {
    return NextResponse.json(
      { found: false, error: "Imagem muito pequena/invalida" },
      { status: 422 }
    );
  }

  // Save to Supabase Storage + metadata table
  const pessoa = await salvarPessoa({
    nome,
    slug,
    imageBuffer,
    sourceUrl: imageUrl!,
  });

  if (!pessoa) {
    return NextResponse.json({ error: "Erro ao salvar no Supabase" }, { status: 500 });
  }

  return NextResponse.json({ found: true, cached: false, ...pessoa });
}
