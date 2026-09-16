import { NextRequest, NextResponse } from "next/server";
import { buscarNoticias, buscarImagens, marcarNoticiaUsada } from "@/lib/supabase";

// GET /api/news?tema=ia&horas=72&limite=10
export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const tema = url.searchParams.get("tema") || "";
  const horas = parseInt(url.searchParams.get("horas") || "72", 10);
  const limite = parseInt(url.searchParams.get("limite") || "10", 10);
  const tipo = url.searchParams.get("tipo") || "noticias"; // noticias | imagens

  if (tipo === "imagens") {
    const categoria = url.searchParams.get("categoria") || tema;
    const tags = url.searchParams.get("tags")?.split(",") || [];
    const imagens = await buscarImagens(categoria, tags, limite);
    return NextResponse.json({ imagens, total: imagens.length });
  }

  const noticias = await buscarNoticias(tema, horas, limite);
  return NextResponse.json({ noticias, total: noticias.length });
}

// POST /api/news/used — marca notícia como usada
export async function POST(req: NextRequest) {
  const { id } = await req.json();
  if (!id) return NextResponse.json({ error: "id required" }, { status: 400 });
  await marcarNoticiaUsada(id);
  return NextResponse.json({ ok: true });
}
