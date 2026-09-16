import { createClient, SupabaseClient } from "@supabase/supabase-js";

let _client: SupabaseClient | null = null;

function getClient(): SupabaseClient {
  if (!_client) {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required");
    _client = createClient(url, key);
  }
  return _client;
}

export const supabase = { get client() { return getClient(); } };

export interface Noticia {
  id: string;
  titulo: string;
  resumo: string;
  conteudo?: string;
  url?: string;
  categoria: string;
  tags: string[];
  fonte?: string;
  publicado_em: string;
}

export interface ImagemBanco {
  id: string;
  r2_key: string;
  url_publica: string;
  categoria: string;
  tags: string[];
  descricao?: string;
}

export async function buscarNoticias(tema: string, horas = 72, limite = 10): Promise<Noticia[]> {
  const client = getClient();
  const { data, error } = await client.rpc("buscar_noticias", {
    p_tema: tema,
    p_limite: limite,
    p_horas: horas,
  });

  if (error) {
    const { data: fallback } = await client
      .from("noticias")
      .select("*")
      .eq("ativo", true)
      .gte("publicado_em", new Date(Date.now() - horas * 3600000).toISOString())
      .order("publicado_em", { ascending: false })
      .limit(limite);
    return fallback || [];
  }

  return data || [];
}

export async function buscarImagens(categoria: string, tags: string[] = [], limite = 20): Promise<ImagemBanco[]> {
  const client = getClient();
  let query = client
    .from("imagens_banco")
    .select("*")
    .eq("ativo", true)
    .order("criado_em", { ascending: false })
    .limit(limite);

  if (categoria) {
    query = query.eq("categoria", categoria);
  }

  const { data } = await query;
  return data || [];
}

export interface PessoaCache {
  id: string;
  nome: string;
  slug: string;
  storage_path: string;
  url_publica: string;
  source_url?: string;
}

export async function buscarPessoa(slug: string): Promise<PessoaCache | null> {
  const client = getClient();
  const { data } = await client
    .from("banco_pessoas")
    .select("*")
    .eq("slug", slug)
    .single();
  return data || null;
}

export async function salvarPessoa(pessoa: {
  nome: string;
  slug: string;
  imageBuffer: Buffer;
  sourceUrl: string;
}): Promise<PessoaCache | null> {
  const client = getClient();
  const storagePath = `${pessoa.slug}/reference.jpg`;

  // Upload to Supabase Storage
  const { error: uploadErr } = await client.storage
    .from("banco-pessoas")
    .upload(storagePath, pessoa.imageBuffer, {
      contentType: "image/jpeg",
      upsert: true,
    });

  if (uploadErr) {
    console.error("Erro upload storage:", uploadErr);
    return null;
  }

  // Get public URL
  const { data: urlData } = client.storage
    .from("banco-pessoas")
    .getPublicUrl(storagePath);

  const urlPublica = urlData.publicUrl;

  // Upsert metadata
  const { data, error } = await client
    .from("banco_pessoas")
    .upsert(
      {
        nome: pessoa.nome,
        slug: pessoa.slug,
        storage_path: storagePath,
        url_publica: urlPublica,
        source_url: pessoa.sourceUrl,
        atualizado_em: new Date().toISOString(),
      },
      { onConflict: "slug" }
    )
    .select()
    .single();

  if (error) {
    console.error("Erro upsert banco_pessoas:", error);
    return null;
  }

  return data;
}

export async function marcarNoticiaUsada(id: string) {
  const client = getClient();
  await client
    .from("noticias")
    .update({ usado: true, usado_em: new Date().toISOString() })
    .eq("id", id);
}
