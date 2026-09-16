from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from app.models.job import JobStatus

class OperationType(str, Enum):
    TRIM = "trim"
    RESIZE = "resize"
    CONVERT = "convert"
    CROP = "crop"
    ROTATE = "rotate"
    SPEED = "speed"
    EXTRACT_AUDIO = "extract_audio"
    ADD_AUDIO = "add_audio"
    ADD_SUBTITLES = "add_subtitles"
    ADD_WATERMARK = "add_watermark"
    FILTER = "filter"
    MERGE = "merge"
    TO_GIF = "to_gif"
    THUMBNAIL = "thumbnail"
    TRANSCRIBE = "transcribe"
    AUTO_SUBTITLE = "auto_subtitle"
    TRANSLATE_SUBTITLES = "translate_subtitles"
    REMOVE_SILENCE = "remove_silence"
    SMART_CUT = "smart_cut"
    ADJUST_VOLUME = "adjust_volume"
    ADD_TEXT_OVERLAY = "add_text_overlay"
    VIDEO_OVERLAY = "video_overlay"
    REMOTION_RENDER = "remotion_render"
    DETECT_HIGHLIGHTS = "detect_highlights"
    EXTRACT_CLIPS = "extract_clips"
    NORMALIZE = "normalize"
    PLAN_SCENES = "plan_scenes"
    SELECT_CLIPS = "select_clips"
    EVAL_CUTS = "eval_cuts"
    DETECT_FILLERS = "detect_fillers"
    DETECT_SPEAKERS = "detect_speakers"
    FAST_SUBTITLES = "fast_subtitles"
    FILMSTRIP = "filmstrip"
    ANALYZE_PROFILE = "analyze_profile"
    PRESET = "preset"

class Operation(BaseModel):
    type: OperationType
    params: Dict[str, Any]

class VideoEditRequest(BaseModel):
    video_url: Optional[str] = None
    operations: List[Operation]
    output_format: str = Field(default="mp4", pattern="^(mp4|avi|mov|mkv|webm)$")
    webhook_url: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)

class JobResponse(BaseModel):
    id: str
    status: JobStatus
    progress: int
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[int] = None

    class Config:
        from_attributes = True
