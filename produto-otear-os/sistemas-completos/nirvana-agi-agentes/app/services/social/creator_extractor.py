"""
Creator Profile Extractor — orquestra o pipeline completo:

  list_recent_posts() ->  download audio  ->  Whisper transcribe
                                                       |
                                                       v
                                            LLM extract patterns
                                                       |
                                                       v
                                       write _profile.md + posts/*.md
                                       + _meta.json (progresso)

Single entrypoint: extract_creator_profile(handle, platform, kind)
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
import tempfile
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from app.services.social.types import (
    CreatorAnalysis, ExtractionMeta, PostScriptAnalysis, SocialPost,
)
from app.services.social.markdown_writer import (
    get_creator_dir, write_meta, write_post, write_profile,
)
from app.services.llm_cascade import call_llm

logger = logging.getLogger(__name__)

DEFAULT_POSTS_PER_CREATOR = int(os.getenv("CREATOR_EXTRACTION_POSTS", "10"))


def extract_video_reference(
    url: str,
    label: str = "",
    platform: str = "unknown",
    kind: str = "inspiration",
    job_id: Optional[str] = None,
) -> ExtractionMeta:
    """Extrai estilo de um video avulso e salva como referencia de 1 post."""
    job_id = job_id or str(uuid.uuid4())[:8]
    post = _post_from_url(url=url, label=label, platform=platform)
    started = datetime.now(timezone.utc).isoformat()

    meta = ExtractionMeta(
        handle=post.handle,
        platform=post.platform,
        kind=kind,
        status="extracting",
        posts_total=1,
        posts_done=0,
        started_at=started,
        job_id=job_id,
    )
    write_meta(meta)
    logger.info(f"[extract-video:{job_id}] starting {post.url} as {post.handle}")

    try:
        from app.services.whisper_service import WhisperService
        whisper_service = WhisperService(model_size=os.getenv("CREATOR_WHISPER_MODEL_SIZE", "base"))

        transcript = _download_and_transcribe(post, whisper_service)
        post_analysis = _analyze_post_script(post, transcript)
        write_post(post, transcript, post_analysis)
        meta.posts_done = 1
        write_meta(meta)

        analysis = _analyze_creator(post.handle, post.platform, [post], [transcript])
        write_profile(post.handle, post.platform, kind, 1 if transcript.strip() else 0, analysis)

        meta.status = "done"
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        write_meta(meta)
        logger.info(f"[extract-video:{job_id}] OK {post.handle}")
        return meta

    except Exception as e:
        logger.exception(f"[extract-video:{job_id}] failed: {e}")
        meta.status = "failed"
        meta.last_error = str(e)[:500]
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        write_meta(meta)
        return meta


def extract_creator_profile(
    handle: str,
    platform: str,
    kind: str = "inspiration",
    posts_count: int = DEFAULT_POSTS_PER_CREATOR,
    job_id: Optional[str] = None,
) -> ExtractionMeta:
    """Pipeline completo. Atualiza _meta.json a cada etapa para o frontend ver progresso."""
    job_id = job_id or str(uuid.uuid4())[:8]
    started = datetime.now(timezone.utc).isoformat()

    meta = ExtractionMeta(
        handle=handle, platform=platform, kind=kind,
        status="extracting", posts_total=posts_count, posts_done=0,
        started_at=started, job_id=job_id,
    )
    write_meta(meta)
    logger.info(f"[extract:{job_id}] starting {platform} @{handle.lstrip('@')} ({kind})")

    try:
        posts = _list_posts(handle, platform, posts_count)
        if not posts:
            meta.status = "failed"
            meta.last_error = f"Nenhum post listado para {platform} @{handle.lstrip('@')}"
            meta.finished_at = datetime.now(timezone.utc).isoformat()
            write_meta(meta)
            return meta

        meta.posts_total = len(posts)
        write_meta(meta)

        from app.services.whisper_service import WhisperService
        whisper_service = WhisperService(model_size=os.getenv("CREATOR_WHISPER_MODEL_SIZE", "base"))

        # Transcreve cada post (com retry leve)
        transcripts: List[str] = []
        for i, post in enumerate(posts, 1):
            transcript = _download_and_transcribe(post, whisper_service)
            transcripts.append(transcript)
            post_analysis = _analyze_post_script(post, transcript)
            write_post(post, transcript, post_analysis)
            meta.posts_done = i
            write_meta(meta)
            logger.info(f"[extract:{job_id}] {i}/{len(posts)} done")

        # Analise agregada via LLM
        analysis = _analyze_creator(handle, platform, posts, transcripts)
        write_profile(handle, platform, kind, len(posts), analysis)

        meta.status = "done"
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        write_meta(meta)
        logger.info(f"[extract:{job_id}] OK {handle} ({len(posts)} posts)")
        return meta

    except Exception as e:
        logger.exception(f"[extract:{job_id}] failed: {e}")
        meta.status = "failed"
        meta.last_error = str(e)[:500]
        meta.finished_at = datetime.now(timezone.utc).isoformat()
        write_meta(meta)
        return meta


def _list_posts(handle: str, platform: str, count: int) -> List[SocialPost]:
    if platform == "tiktok":
        from app.services.social.tiktok_lister import list_recent_posts
        return list_recent_posts(handle, count=count)
    if platform == "instagram":
        from app.services.social.instagram_lister import list_recent_posts
        return list_recent_posts(handle, count=count)
    if platform == "unknown":
        # Tenta TikTok primeiro, Instagram depois
        from app.services.social.tiktok_lister import list_recent_posts as tt_list
        from app.services.social.instagram_lister import list_recent_posts as ig_list
        posts = tt_list(handle, count=count)
        if posts:
            return posts
        return ig_list(handle, count=count)
    logger.warning(f"[extract] platform desconhecida: {platform}")
    return []


def _post_from_url(url: str, label: str, platform: str) -> SocialPost:
    clean_url = (url or "").strip()
    if not clean_url.startswith(("http://", "https://")):
        raise ValueError("URL de video invalida")

    detected = _detect_platform(clean_url, platform)
    digest = hashlib.sha1(clean_url.encode("utf-8")).hexdigest()[:10]
    parsed = urlparse(clean_url)
    label_slug = _slugify(label) if label else ""
    handle = f"@video_{label_slug}_{digest}" if label_slug else f"@video_{digest}"

    return SocialPost(
        post_id=digest,
        platform=detected,
        handle=handle,
        url=clean_url,
        play_url=None,
        cover_url=None,
        title=label or f"Video avulso de {parsed.netloc}",
        duration=0.0,
        posted_at=datetime.now(timezone.utc).isoformat(),
    )


def _detect_platform(url: str, platform: str) -> str:
    if platform and platform != "unknown":
        return platform
    host = urlparse(url).netloc.lower()
    if "tiktok" in host:
        return "tiktok"
    if "instagram" in host:
        return "instagram"
    if "youtube" in host or "youtu.be" in host:
        return "youtube"
    return "video"


def _slugify(value: str) -> str:
    value = value.strip().lower().replace("@", "")
    out = []
    for c in value:
        if c.isalnum():
            out.append(c)
        elif c in (" ", "-", "_", "."):
            out.append("_")
    return "".join(out).strip("_")[:32]


def _download_and_transcribe(post: SocialPost, whisper_service) -> str:
    """Baixa audio e transcreve. Retorna string vazia em falha (nao lanca)."""
    tmpdir = Path(tempfile.gettempdir()) / "creator_extract"
    tmpdir.mkdir(parents=True, exist_ok=True)

    try:
        audio_path = _download_audio(post, tmpdir)
        if not audio_path or not audio_path.exists():
            logger.warning(f"[extract] download falhou para {post.url}")
            return ""

        result = whisper_service.transcribe(str(audio_path))
        text = result.get("text", "").strip()
        return text
    except Exception as e:
        logger.warning(f"[extract] transcribe falhou para {post.url}: {e}")
        return ""
    finally:
        # Limpeza best-effort do audio
        try:
            if 'audio_path' in locals() and audio_path and audio_path.exists():
                audio_path.unlink()
        except Exception:
            pass


def _download_audio(post: SocialPost, tmpdir: Path) -> Optional[Path]:
    """Baixa audio do post. Estrategia depende da plataforma."""
    target = tmpdir / f"{post.platform}_{post.post_id}.mp4"

    if post.platform == "tiktok":
        # Se o lister devolveu play_url, usamos direto; senao tentamos yt-dlp
        # primeiro, que hoje esta mais estavel que o downloader via ssstik.
        if post.play_url:
            return _download_direct(post.play_url, target)
        ytdlp_path = _ytdlp_media(post.url, target)
        if ytdlp_path:
            return ytdlp_path
        from app.services.tiktok_downloader import download_tiktok_video
        try:
            return download_tiktok_video(post.url, tmpdir, filename=target.name)
        except Exception as e:
            logger.warning(f"[extract] tiktok_downloader falhou: {e}")
            return None

    if post.platform == "instagram":
        if post.play_url:
            return _download_direct(post.play_url, target)
        # fallback yt-dlp para Instagram tambem
        return _ytdlp_media(post.url, target)

    if post.platform in ("youtube", "video"):
        return _ytdlp_media(post.url, target)

    return None


def _download_direct(url: str, target: Path) -> Optional[Path]:
    import requests
    try:
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(target, "wb") as f:
                for chunk in r.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        f.write(chunk)
        return target
    except Exception as e:
        logger.warning(f"[extract] direct download falhou {url}: {e}")
        return None


def _ytdlp_media(url: str, target: Path) -> Optional[Path]:
    out_template = str(target.with_suffix(".%(ext)s"))
    cmd = [
        "yt-dlp",
        "-o", out_template,
        "--no-warnings",
        "--quiet",
        "--restrict-filenames",
        url,
    ]
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".out", delete=False) as out_file, \
         tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".err", delete=False) as err_file:
        out_path = out_file.name
        err_path = err_file.name

    try:
        with open(out_path, "w", encoding="utf-8") as out_handle, open(err_path, "w", encoding="utf-8") as err_handle:
            r = subprocess.run(cmd, stdout=out_handle, stderr=err_handle, timeout=300, text=True)
        if r.returncode != 0:
            try:
                err_preview = Path(err_path).read_text(encoding="utf-8")[-300:]
            except OSError:
                err_preview = ""
            logger.warning(f"[extract] yt-dlp exit={r.returncode} {url}: {err_preview}")
            return None
        # yt-dlp pode ter mudado a extensao
        for p in target.parent.glob(target.stem + ".*"):
            return p
    except Exception as e:
        logger.warning(f"[extract] yt-dlp falhou {url}: {e}")
    finally:
        for temp_path in (out_path, err_path):
            try:
                Path(temp_path).unlink()
            except OSError:
                pass
    return None


def _analyze_creator(
    handle: str, platform: str,
    posts: List[SocialPost], transcripts: List[str],
) -> CreatorAnalysis:
    """LLM extrai padroes agregados. Cascata Anthropic -> OpenAI -> Gemini."""
    valid_pairs = [(p, t) for p, t in zip(posts, transcripts) if t.strip()]
    if not valid_pairs:
        return CreatorAnalysis(
            handle=handle, platform=platform, posts_analyzed=0,
            summary="Nao foi possivel transcrever nenhum post.",
        )

    prompt = _build_analysis_prompt(handle, platform, valid_pairs)
    text = _call_llm_cascade(prompt)
    if not text:
        return CreatorAnalysis(
            handle=handle, platform=platform, posts_analyzed=len(valid_pairs),
            summary="LLM indisponivel; analise nao foi feita.",
        )

    return _parse_analysis_response(text, handle, platform, len(valid_pairs))


def _analyze_post_script(post: SocialPost, transcript: str) -> Optional[PostScriptAnalysis]:
    """Analisa um post individual frase/paragrafo por frase/paragrafo."""
    clean_transcript = (transcript or "").strip()
    if not clean_transcript:
        return None

    prompt = _build_post_script_analysis_prompt(post, clean_transcript)
    text = _call_llm_cascade(prompt)
    if not text:
        return None
    return _parse_post_script_analysis_response(text)


def _build_post_script_analysis_prompt(post: SocialPost, transcript: str) -> str:
    caption = (post.title or "").strip()[:800]
    return (
        "Voce e um analista senior de roteiro curto e retencao para Reels/TikTok/Shorts/YouTube.\n"
        "Analise o video abaixo em detalhes. O objetivo e marcar exatamente o que foi usado no roteiro.\n\n"
        f"Plataforma: {post.platform}\n"
        f"URL: {post.url}\n"
        f"Caption: {caption}\n"
        f"Transcricao:\n{transcript[:4500]}\n\n"
        "Retorne APENAS JSON valido com este esquema:\n"
        "{\n"
        '  "hook_literal": "copie literalmente a primeira frase/trecho que funciona como hook",\n'
        '  "hook_type": "curiosidade | controversia | identificacao | promessa | noticia | medo | autoridade | outro",\n'
        '  "script_breakdown_markdown": "tabela markdown com colunas: Trecho | Funcao | Recurso usado | Gatilho | Por que funciona | Como reutilizar",\n'
        '  "reusable_patterns": ["padrao especifico 1", "padrao especifico 2"]\n'
        "}\n\n"
        "Regras da analise:\n"
        "- Quebre por frase curta ou paragrafo natural, nao resuma o video inteiro em um bloco.\n"
        "- Em 'Trecho', preserve o texto original o maximo possivel.\n"
        "- Marque funcoes como hook, setup, contexto, prova, exemplo, tensao, virada, payoff, CTA.\n"
        "- Identifique recursos como contraste, pergunta retorica, lista, especificidade, autoridade, historia, repeticao, quebra de expectativa.\n"
        "- Seja pratico: explique como o usuario pode copiar o padrao sem copiar o conteudo.\n"
        "- Nao invente falas que nao aparecem na transcricao.\n"
    )


def _parse_post_script_analysis_response(text: str) -> Optional[PostScriptAnalysis]:
    import json

    candidate = None
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        candidate = m.group(1)
    else:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            candidate = m.group(0)
    if not candidate:
        return PostScriptAnalysis(script_breakdown_markdown=text.strip()[:4000])

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return PostScriptAnalysis(script_breakdown_markdown=text.strip()[:4000])

    return PostScriptAnalysis(
        hook_literal=str(data.get("hook_literal") or "").strip(),
        hook_type=str(data.get("hook_type") or "").strip(),
        script_breakdown_markdown=str(data.get("script_breakdown_markdown") or "").strip(),
        reusable_patterns=_as_list(data.get("reusable_patterns")),
    )


def _build_analysis_prompt(
    handle: str, platform: str, pairs: List[tuple]
) -> str:
    blocks = []
    for i, (p, t) in enumerate(pairs, 1):
        caption = (p.title or "").strip()[:200]
        blocks.append(
            f"### Post {i} ({p.duration:.0f}s)\n"
            f"Caption: {caption}\n"
            f"Transcript: {t[:1500]}"
        )

    return (
        f"Voce eh um analista de creators virais. Abaixo estao {len(pairs)} posts de "
        f"{platform} @{handle.lstrip('@')}.\n\n"
        "Sua tarefa: extrair PADROES recorrentes (nao analise um post de cada vez — "
        "agregue o estilo do criador atraves de todos).\n\n"
        + "\n\n".join(blocks) + "\n\n"
        "Retorne APENAS JSON valido com o esquema abaixo. Use frases curtas, em pt-BR.\n"
        "```json\n"
        "{\n"
        '  "hook_patterns": ["padrao 1 (Nx)", "padrao 2 (Mx)"],\n'
        '  "narrative_arc": "Setup -> Problema -> Insight -> CTA",\n'
        '  "vocabulary": ["palavra1", "palavra2", "..."],\n'
        '  "emotional_triggers": ["FOMO", "Curiosidade", "..."],\n'
        '  "cta_style": "exemplo literal de CTA recorrente",\n'
        '  "tone": "descricao curta do tom",\n'
        '  "pacing": "ritmo da fala/cortes",\n'
        '  "visual_format": "talking head, B-roll, etc.",\n'
        '  "summary": "2-3 frases descrevendo o estilo geral"\n'
        "}\n"
        "```"
    )


def _call_llm_cascade(prompt: str) -> Optional[str]:
    try:
        return call_llm(prompt, max_tokens=2000)
    except Exception as e:
        logger.warning(f"[extract] llm_cascade falhou: {e}")
        return None


def _parse_analysis_response(
    text: str, handle: str, platform: str, posts_count: int
) -> CreatorAnalysis:
    import json
    import re
    candidate = None
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        candidate = m.group(1)
    else:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            candidate = m.group(0)
    if not candidate:
        return CreatorAnalysis(
            handle=handle, platform=platform, posts_analyzed=posts_count,
            hook_patterns=_extract_string_list(text, "hook_patterns"),
            vocabulary=_extract_string_list(text, "vocabulary"),
            emotional_triggers=_extract_string_list(text, "emotional_triggers"),
            summary=f"LLM retornou texto nao-JSON: {text[:200]}",
        )

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return CreatorAnalysis(
            handle=handle, platform=platform, posts_analyzed=posts_count,
            hook_patterns=_extract_string_list(text, "hook_patterns"),
            vocabulary=_extract_string_list(text, "vocabulary"),
            emotional_triggers=_extract_string_list(text, "emotional_triggers"),
            summary="LLM retornou JSON invalido.",
        )

    return CreatorAnalysis(
        handle=handle, platform=platform, posts_analyzed=posts_count,
        hook_patterns=_as_list(data.get("hook_patterns")),
        narrative_arc=str(data.get("narrative_arc") or "").strip(),
        vocabulary=_as_list(data.get("vocabulary")),
        emotional_triggers=_as_list(data.get("emotional_triggers")),
        cta_style=str(data.get("cta_style") or "").strip(),
        tone=str(data.get("tone") or "").strip(),
        pacing=str(data.get("pacing") or "").strip(),
        visual_format=str(data.get("visual_format") or "").strip(),
        summary=str(data.get("summary") or "").strip(),
    )


def _as_list(v) -> List[str]:
    if not v:
        return []
    if isinstance(v, str):
        return [s.strip() for s in v.split(",") if s.strip()]
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return []


def _extract_string_list(text: str, key: str) -> List[str]:
    if not text:
        return []
    pattern = rf'"{re.escape(key)}"\s*:\s*\[(.*?)\]'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return []
    return [
        item.strip()
        for item in re.findall(r'"([^"]+)"', match.group(1))
        if item.strip()
    ]
