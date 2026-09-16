from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import httpx
import time
import os
import json
import logging
import shutil
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

REMOTION_SERVICE_URL = os.getenv("REMOTION_SERVICE_URL", "http://localhost:8003")
POLL_INTERVAL = 5  # seconds
MAX_WAIT = 600  # 10 minutes
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "/app/storage")).resolve()


def is_remotion_available() -> bool:
    """Check if the Remotion service is reachable."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(f"{REMOTION_SERVICE_URL}/health")
            return resp.status_code == 200
    except Exception:
        return False


class RemotionRenderOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'mode' not in params:
            raise ValueError("remotion_render requires 'mode' (viral, aula, custom, pro)")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        RemotionRenderOperation.validate_params(params)

        # Check if Remotion is available, fallback to FFmpeg copy if not
        if not is_remotion_available():
            logger.warning(
                f"Remotion service not available at {REMOTION_SERVICE_URL}. "
                f"Falling back to passthrough (video will use FFmpeg operations only)."
            )
            # Just copy the input to output — the previous operations in the pipeline
            # (smart_cut, remove_silence, auto_subtitle) already ran via FFmpeg
            shutil.copy2(input_path, output_path)
            return

        mode = params.get('mode', 'viral')
        video_url = _ensure_public_video_url(input_path)

        # Build render request for Remotion service
        render_request = {
            'videoUrl': video_url,
            'mode': mode,
        }

        # Load scene plan from sidecar JSON if it exists (from plan_scenes operation)
        scenes_path = input_path + ".scenes.json"
        if os.path.exists(scenes_path):
            try:
                with open(scenes_path, "r", encoding="utf-8") as f:
                    scene_plan = json.load(f)
                if scene_plan.get("scenes"):
                    render_request["scenes"] = scene_plan["scenes"]
                    logger.info(f"Loaded {len(scene_plan['scenes'])} scenes from plan")
                if scene_plan.get("palette"):
                    render_request["palette"] = scene_plan["palette"]
                if scene_plan.get("words") and "words" not in params:
                    render_request["words"] = scene_plan["words"]
            except Exception as e:
                logger.warning(f"Could not load scene plan: {e}")

        # Pass through optional Remotion-specific params
        optional_fields = [
            'segments', 'words', 'transition', 'subtitles', 'zoom',
            'textOverlays', 'lowerThirds', 'bRolls', 'hookVisuals',
            'branding', 'progressBar', 'template', 'quality',
            'scenes', 'palette',
        ]
        for field in optional_fields:
            if field in params:
                render_request[field] = params[field]

        logger.info(f"Remotion render: mode={mode}, sending to {REMOTION_SERVICE_URL}")

        # Submit render job
        with httpx.Client(timeout=30) as client:
            resp = client.post(f"{REMOTION_SERVICE_URL}/render", json=render_request)
            resp.raise_for_status()
            job_data = resp.json()
            job_id = job_data['id']
            logger.info(f"Remotion job submitted: {job_id}")

        # Poll for completion
        elapsed = 0
        with httpx.Client(timeout=30) as client:
            while elapsed < MAX_WAIT:
                time.sleep(POLL_INTERVAL)
                elapsed += POLL_INTERVAL

                resp = client.get(f"{REMOTION_SERVICE_URL}/status/{job_id}")
                resp.raise_for_status()
                status = resp.json()

                logger.info(f"Remotion job {job_id}: {status['status']} ({status.get('progress', 0)}%)")

                if status['status'] == 'completed':
                    output_url = status.get('outputUrl', '')
                    download_url = f"{REMOTION_SERVICE_URL}{output_url}"

                    logger.info(f"Downloading rendered video from {download_url}")
                    with httpx.Client(timeout=120) as dl_client:
                        dl_resp = dl_client.get(download_url)
                        dl_resp.raise_for_status()
                        with open(output_path, 'wb') as f:
                            f.write(dl_resp.content)

                    logger.info(f"Remotion render complete: {output_path}")
                    return

                if status['status'] == 'failed':
                    error = status.get('error', 'Unknown error')
                    raise RuntimeError(f"Remotion render failed: {error}")

        raise RuntimeError(f"Remotion render timed out after {MAX_WAIT}s")


def _public_api_base_url() -> str:
    base = os.getenv("PUBLIC_API_URL") or os.getenv("API_BASE_URL") or "http://gateway:8000"
    return base.rstrip("/")


def _ensure_public_video_url(input_path: str) -> str:
    if input_path.startswith(("http://", "https://")):
        return input_path

    source_path = Path(input_path).resolve()
    if source_path.is_relative_to(STORAGE_PATH):
        return f"{_public_api_base_url()}/static/{source_path.name}"

    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    public_name = f"remotion_source_{uuid.uuid4().hex[:12]}_{source_path.name}"
    public_path = STORAGE_PATH / public_name
    shutil.copy2(source_path, public_path)
    logger.info("Published Remotion source video to %s", public_path)
    return f"{_public_api_base_url()}/static/{public_name}"
