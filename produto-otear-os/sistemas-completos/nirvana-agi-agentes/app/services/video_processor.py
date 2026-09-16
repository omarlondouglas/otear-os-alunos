from sqlalchemy.orm import Session
from app.models.job import VideoJob, JobStatus
from app.schemas.video import VideoEditRequest
from app.core.storage import save_upload, UPLOADS_PATH
from app.services.tiktok_downloader import download_tiktok_video, is_tiktok_url
from fastapi import UploadFile, HTTPException
from pathlib import Path
from urllib.parse import urlparse
import asyncio
import shutil
import subprocess
import uuid
import httpx
import aiofiles
import os

MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "2048"))
_DOWNLOAD_TIMEOUT = httpx.Timeout(connect=30.0, read=1800.0, write=60.0, pool=30.0)
_YTDLP_TIMEOUT_SECONDS = int(os.getenv("YTDLP_TIMEOUT_SECONDS", "900"))
_SOCIAL_VIDEO_HOSTS = (
    "youtube.com",
    "youtu.be",
)


def _is_social_video_url(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
    except Exception:
        return False
    host = host.lower()
    return any(host == allowed or host.endswith(f".{allowed}") for allowed in _SOCIAL_VIDEO_HOSTS)


class VideoProcessor:
    def __init__(self, db: Session):
        self.db = db

    async def create_job(self, request: VideoEditRequest, video: UploadFile = None) -> VideoJob:
        job_id = str(uuid.uuid4())
        
        if video:
            input_path = await save_upload(video, f"{job_id}_input_{video.filename}")
        elif request.video_url:
            input_path = await self._download_file(request.video_url, f"{job_id}_input_download.mp4")
        else:
            raise HTTPException(400, "Must provide 'video' file or 'video_url'")
        
        db_job = VideoJob(
            id=job_id,
            status=JobStatus.QUEUED,
            input_video_path=input_path,
            operations=[op.model_dump() for op in request.operations],
            webhook_url=request.webhook_url
        )
        
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        
        return db_job

    async def _download_file(self, url: str, filename: str) -> str:
        if is_tiktok_url(url):
            return await asyncio.to_thread(self._download_tiktok, url, filename)

        if _is_social_video_url(url):
            return await asyncio.to_thread(self._download_with_ytdlp, url, filename)

        file_path = UPLOADS_PATH / filename
        max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
        downloaded = 0
        async with httpx.AsyncClient(timeout=_DOWNLOAD_TIMEOUT, follow_redirects=True) as client:
            async with client.stream('GET', url) as response:
                if response.status_code != 200:
                    raise HTTPException(400, f"Failed to download video from URL: {response.status_code}")
                content_length = int(response.headers.get("content-length", 0))
                if content_length > max_bytes:
                    raise HTTPException(413, f"Video too large: {content_length // (1024*1024)}MB exceeds {MAX_VIDEO_SIZE_MB}MB limit")
                async with aiofiles.open(file_path, 'wb') as out_file:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        downloaded += len(chunk)
                        if downloaded > max_bytes:
                            raise HTTPException(413, f"Video exceeds {MAX_VIDEO_SIZE_MB}MB size limit")
                        await out_file.write(chunk)
        return str(file_path.absolute())

    def _download_tiktok(self, url: str, filename: str) -> str:
        try:
            downloaded_path = download_tiktok_video(
                url,
                UPLOADS_PATH,
                filename=Path(filename).with_suffix(".mp4").name,
            )
        except Exception as exc:
            try:
                return self._download_with_ytdlp(url, filename)
            except HTTPException as ytdlp_exc:
                raise HTTPException(
                    400,
                    f"Failed to download TikTok video: {exc}; fallback yt-dlp: {ytdlp_exc.detail}",
                ) from exc

        max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
        if downloaded_path.stat().st_size > max_bytes:
            downloaded_path.unlink(missing_ok=True)
            raise HTTPException(413, f"Video exceeds {MAX_VIDEO_SIZE_MB}MB size limit")

        return str(downloaded_path.absolute())

    def _download_with_ytdlp(self, url: str, filename: str) -> str:
        if not shutil.which("yt-dlp"):
            raise HTTPException(
                400,
                "Formato de URL requer yt-dlp, mas yt-dlp nao esta instalado no ambiente",
            )

        file_path = UPLOADS_PATH / filename
        output_template = str(file_path.with_suffix(".%(ext)s"))
        max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--restrict-filenames",
            "--max-filesize",
            f"{MAX_VIDEO_SIZE_MB}M",
            "-f",
            "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
            "--merge-output-format",
            "mp4",
            "-o",
            output_template,
            url,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=_YTDLP_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            error = (result.stderr or result.stdout or "").strip()[-500:]
            raise HTTPException(400, f"Failed to download video with yt-dlp: {error}")

        candidates = sorted(Path(UPLOADS_PATH).glob(f"{file_path.stem}.*"))
        downloaded_path = next((path for path in candidates if path.is_file()), None)
        if not downloaded_path:
            raise HTTPException(400, "yt-dlp did not create a video file")

        if downloaded_path.stat().st_size > max_bytes:
            downloaded_path.unlink(missing_ok=True)
            raise HTTPException(413, f"Video exceeds {MAX_VIDEO_SIZE_MB}MB size limit")

        return str(downloaded_path.absolute())

    def get_job(self, job_id: str) -> VideoJob:
        return self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
