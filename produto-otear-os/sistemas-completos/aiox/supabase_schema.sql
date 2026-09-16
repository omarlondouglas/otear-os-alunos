-- Schema para swipe files vetorizados
-- Roda no Supabase SQL Editor

-- 1. Habilitar pgvector
create extension if not exists vector;

-- 2. Tabela principal
create table if not exists public.swipes (
    id bigserial primary key,
    author text not null,
    source_file text not null,
    source_pdf text,
    page int,
    language text check (language in ('en', 'pt', 'mixed')),
    chunk_index int not null,
    chunk_total int not null,
    content text not null,
    content_tokens int,
    embedding vector(1536),
    metadata jsonb default '{}'::jsonb,
    created_at timestamptz default now(),
    unique (source_file, chunk_index)
);

-- 3. Indices para busca
create index if not exists swipes_author_idx on public.swipes (author);
create index if not exists swipes_language_idx on public.swipes (language);
create index if not exists swipes_metadata_idx on public.swipes using gin (metadata);

-- Indice vetorial HNSW (melhor que IVFFlat pra datasets crescentes)
create index if not exists swipes_embedding_idx
    on public.swipes using hnsw (embedding vector_cosine_ops);

-- 4. Funcao de busca semantica
create or replace function match_swipes(
    query_embedding vector(1536),
    match_count int default 10,
    filter_author text default null,
    filter_language text default null,
    similarity_threshold float default 0.5
)
returns table (
    id bigint,
    author text,
    source_file text,
    page int,
    language text,
    content text,
    similarity float,
    metadata jsonb
)
language plpgsql
as $$
begin
    return query
    select
        s.id,
        s.author,
        s.source_file,
        s.page,
        s.language,
        s.content,
        1 - (s.embedding <=> query_embedding) as similarity,
        s.metadata
    from public.swipes s
    where
        s.embedding is not null
        and (filter_author is null or s.author = filter_author)
        and (filter_language is null or s.language = filter_language)
        and 1 - (s.embedding <=> query_embedding) > similarity_threshold
    order by s.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- 5. Funcao auxiliar: listar autores
create or replace function list_swipe_authors()
returns table (author text, chunks bigint)
language sql
as $$
    select author, count(*) as chunks
    from public.swipes
    group by author
    order by chunks desc;
$$;
