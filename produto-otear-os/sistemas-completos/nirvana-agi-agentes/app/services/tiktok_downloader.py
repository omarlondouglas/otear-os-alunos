"""
TikTok Downloader (via ssstik.io)
Baixa videos do TikTok contornando o anti-bot do yt-dlp.

Uso:
    from app.services.tiktok_downloader import download_tiktok_video
    path = download_tiktok_video("https://tiktok.com/@x/video/123", Path("/tmp"))
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

BASE_URL = "https://ssstik.io"
HOME_URL = f"{BASE_URL}/pt"
API_URL = f"{BASE_URL}/abc?url=dl"

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/18.5 Mobile/15E148 Safari/604.1"
)

DEFAULT_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 60


class SSStikError(Exception):
    """Erro ao interagir com o ssstik.io."""


def is_tiktok_url(url: str) -> bool:
    """Detecta URLs de TikTok (suporta tiktok.com, vm.tiktok.com, vt.tiktok.com)."""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return "tiktok.com" in host


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": USER_AGENT,
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    })
    return s


def get_tt_token(session: requests.Session) -> str:
    """Carrega a home do ssstik e extrai o token anti-bot 'tt'."""
    r = session.get(HOME_URL, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    m = (
        re.search(r'name=["\']tt["\'][^>]*value=["\']([^"\']+)["\']', r.text)
        or re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']tt["\']', r.text)
    )
    if not m:
        raise SSStikError("Token 'tt' nao encontrado na home do ssstik.io.")
    return m.group(1)


def request_download_link(
    session: requests.Session, tiktok_url: str, tt: str
) -> str:
    """POST em /abc?url=dl e devolve a URL do .mp4 em tikcdn.io."""
    data = {"id": tiktok_url, "locale": "pt", "tt": tt}
    headers = {
        "HX-Request": "true",
        "HX-Target": "target",
        "HX-Current-URL": HOME_URL,
        "Origin": BASE_URL,
        "Referer": HOME_URL,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = session.post(API_URL, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    m = re.search(r'href=["\'](https://tikcdn\.io/[^"\']+)["\']', r.text)
    if not m:
        preview = re.sub(r"\s+", " ", r.text).strip()[:300]
        raise SSStikError(f"Link de download nao encontrado. Resposta: {preview}")
    return m.group(1)


def _sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    return name.strip()[:150] or "video"


def default_filename(tiktok_url: str) -> str:
    """Monta '@usuario_idvideo.mp4' a partir da URL do TikTok."""
    try:
        parts = [p for p in urlparse(tiktok_url).path.split("/") if p]
        user = next((p for p in parts if p.startswith("@")), "tiktok")
        vid = next((p for p in parts if p.isdigit()), None)
        if vid:
            return _sanitize_filename(f"{user}_{vid}.mp4")
    except Exception:
        pass
    return "tiktok_video.mp4"


def _download_file(
    session: requests.Session, url: str, out_path: Path,
    on_progress=None,
) -> None:
    headers = {"Referer": BASE_URL + "/"}
    with session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT, headers=headers) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if on_progress:
                    on_progress(downloaded, total)


def download_tiktok_video(
    tiktok_url: str,
    output_dir: Path,
    filename: Optional[str] = None,
    session: Optional[requests.Session] = None,
    on_progress=None,
) -> Path:
    """Pipeline completo: token -> link -> download. Retorna Path do .mp4 salvo.

    Args:
        tiktok_url: URL do video TikTok (qualquer formato suportado pelo ssstik.io).
        output_dir: Pasta destino (criada se nao existir).
        filename: Nome do arquivo. Se None, deriva da URL.
        session: requests.Session reaproveitavel. Cria nova se None.
        on_progress: callback(downloaded_bytes, total_bytes) para reportar progresso.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sess = session or make_session()
    if session is None:
        try:
            sess.get(HOME_URL, timeout=DEFAULT_TIMEOUT)
        except requests.RequestException:
            pass  # warm-up best-effort

    tt = get_tt_token(sess)
    video_url = request_download_link(sess, tiktok_url, tt)
    out_path = output_dir / (filename or default_filename(tiktok_url))
    _download_file(sess, video_url, out_path, on_progress=on_progress)
    return out_path
