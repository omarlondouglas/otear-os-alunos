import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

/**
 * POST /api/collect-news
 * Collects news from web search and saves to Supabase.
 * Body: { query?: string, categorias?: string[] }
 *
 * Can be called manually from the UI or via cron/scheduler.
 */

const NICHOS = [
  { query: "agentes de IA novidades 2026", categoria: "ia", tags: ["agentes", "ia", "automacao"] },
  { query: "inteligência artificial empresas automação", categoria: "ia", tags: ["ia", "empresas", "automacao"] },
  { query: "marketing digital IA tendências", categoria: "marketing", tags: ["marketing", "ia", "tendencias"] },
  { query: "agências digitais ferramentas IA", categoria: "negocios", tags: ["agencias", "ia", "ferramentas"] },
  { query: "empreendedorismo digital startups IA", categoria: "empreendedorismo", tags: ["startups", "ia", "empreendedorismo"] },
  { query: "OpenAI Google Anthropic novidades", categoria: "tecnologia", tags: ["openai", "google", "anthropic"] },
  { query: "no-code low-code automação agências", categoria: "tecnologia", tags: ["nocode", "lowcode", "automacao"] },
  { query: "produtividade IA trabalho futuro", categoria: "negocios", tags: ["produtividade", "ia", "futuro"] },
];

function getSupabase() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required");
  return createClient(url, key);
}

interface NewsItem {
  titulo: string;
  resumo: string;
  url: string;
  categoria: string;
  tags: string[];
  fonte: string;
  publicado_em: string;
}

async function searchNews(query: string): Promise<NewsItem[]> {
  // Use the web search via fetch to a search API
  // We'll use a simple approach: call a search endpoint
  const searchUrl = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5&freshness=pw`;
  const apiKey = process.env.BRAVE_SEARCH_API_KEY;

  if (!apiKey) {
    // Fallback: use Google News RSS
    return searchGoogleNewsRSS(query);
  }

  try {
    const res = await fetch(searchUrl, {
      headers: { "Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": apiKey },
    });
    if (!res.ok) return searchGoogleNewsRSS(query);

    const data = await res.json();
    const results = data.web?.results || [];

    return results.slice(0, 5).map((r: { title: string; description: string; url: string; age?: string }) => ({
      titulo: r.title,
      resumo: r.description || r.title,
      url: r.url,
      categoria: "",  // filled by caller
      tags: [],       // filled by caller
      fonte: new URL(r.url).hostname.replace("www.", ""),
      publicado_em: new Date().toISOString(),
    }));
  } catch {
    return searchGoogleNewsRSS(query);
  }
}

async function searchGoogleNewsRSS(query: string): Promise<NewsItem[]> {
  try {
    const rssUrl = `https://news.google.com/rss/search?q=${encodeURIComponent(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419`;
    const res = await fetch(rssUrl);
    if (!res.ok) return [];

    const xml = await res.text();

    // Simple XML parsing for RSS items
    const items: NewsItem[] = [];
    const itemRegex = /<item>([\s\S]*?)<\/item>/g;
    let match;

    while ((match = itemRegex.exec(xml)) !== null && items.length < 5) {
      const itemXml = match[1];
      const title = itemXml.match(/<title>(.*?)<\/title>/)?.[1]?.replace(/<!\[CDATA\[(.*?)\]\]>/, "$1") || "";
      const link = itemXml.match(/<link>(.*?)<\/link>/)?.[1] || "";
      const pubDate = itemXml.match(/<pubDate>(.*?)<\/pubDate>/)?.[1] || "";
      const source = itemXml.match(/<source.*?>(.*?)<\/source>/)?.[1]?.replace(/<!\[CDATA\[(.*?)\]\]>/, "$1") || "";

      if (title && link) {
        items.push({
          titulo: title,
          resumo: title, // RSS doesn't always have description
          url: link,
          categoria: "",
          tags: [],
          fonte: source || "Google News",
          publicado_em: pubDate ? new Date(pubDate).toISOString() : new Date().toISOString(),
        });
      }
    }

    return items;
  } catch {
    return [];
  }
}

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const { categorias } = body as { categorias?: string[] };

  const nichos = categorias
    ? NICHOS.filter((n) => categorias.includes(n.categoria))
    : NICHOS;

  const supabase = getSupabase();
  let totalSaved = 0;
  const errors: string[] = [];

  for (const nicho of nichos) {
    try {
      const news = await searchNews(nicho.query);

      for (const item of news) {
        // Check if URL already exists
        const { data: existing } = await supabase
          .from("noticias")
          .select("id")
          .eq("url", item.url)
          .limit(1);

        if (existing && existing.length > 0) continue;

        // Merge tags
        const allTags = [...new Set([...nicho.tags, ...item.tags])];

        const { error } = await supabase
          .from("noticias")
          .insert({
            titulo: item.titulo,
            resumo: item.resumo,
            url: item.url,
            categoria: nicho.categoria,
            tags: allTags,
            fonte: item.fonte,
            publicado_em: item.publicado_em,
          });

        if (!error) totalSaved++;
        else errors.push(`${item.titulo}: ${error.message}`);
      }
    } catch (err) {
      errors.push(`${nicho.query}: ${err}`);
    }
  }

  return NextResponse.json({
    ok: true,
    saved: totalSaved,
    nichos: nichos.length,
    errors: errors.length > 0 ? errors : undefined,
  });
}

/**
 * GET /api/collect-news — stats about the news bank
 */
export async function GET() {
  try {
    const supabase = getSupabase();

    const { count: total } = await supabase
      .from("noticias")
      .select("*", { count: "exact", head: true })
      .eq("ativo", true);

    const { count: unused } = await supabase
      .from("noticias")
      .select("*", { count: "exact", head: true })
      .eq("ativo", true)
      .eq("usado", false);

    const { data: recentes } = await supabase
      .from("noticias")
      .select("titulo, categoria, publicado_em, fonte")
      .eq("ativo", true)
      .order("publicado_em", { ascending: false })
      .limit(5);

    const { data: categorias } = await supabase
      .rpc("count_by_categoria");

    return NextResponse.json({
      total: total || 0,
      unused: unused || 0,
      recentes: recentes || [],
      categorias: categorias || [],
    });
  } catch (err) {
    return NextResponse.json({ total: 0, error: String(err) });
  }
}
