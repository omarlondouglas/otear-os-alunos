from app.workers.operations.trim import TrimOperation
from app.workers.operations.resize import ResizeOperation
from app.workers.operations.transcribe import TranscribeOperation
from app.workers.operations.auto_subtitle import AutoSubtitleOperation
from app.workers.operations.remove_silence import RemoveSilenceOperation
from app.workers.operations.smart_cut import SmartCutOperation
from app.workers.operations.merge import MergeOperation
from app.workers.operations.watermark import AddWatermarkOperation
from app.workers.operations.adjust_volume import AdjustVolumeOperation
from app.workers.operations.add_text_overlay import AddTextOverlayOperation
from app.workers.operations.add_audio import AddAudioOperation
from app.workers.operations.video_overlay import VideoOverlayOperation
from app.workers.operations.remotion_render import RemotionRenderOperation
from app.workers.operations.detect_highlights import DetectHighlightsOperation
from app.workers.operations.extract_clips import ExtractClipsOperation
from app.workers.operations.normalize import NormalizeOperation
from app.workers.operations.plan_scenes import PlanScenesOperation
from app.workers.operations.select_clips import SelectClipsOperation
from app.workers.operations.eval_cuts import EvalCutsOperation
from app.workers.operations.detect_fillers import DetectFillersOperation
from app.workers.operations.detect_speakers import DetectSpeakersOperation
from app.workers.operations.fast_subtitles import FastSubtitlesOperation
from app.workers.operations.filmstrip import FilmstripOperation
from app.workers.operations.analyze_profile import AnalyzeProfileOperation
from app.schemas.video import OperationType

def get_operation_handler(op_type: str):
    handlers = {
        OperationType.TRIM: TrimOperation,
        OperationType.RESIZE: ResizeOperation,
        OperationType.TRANSCRIBE: TranscribeOperation,
        OperationType.AUTO_SUBTITLE: AutoSubtitleOperation,
        OperationType.REMOVE_SILENCE: RemoveSilenceOperation,
        OperationType.SMART_CUT: SmartCutOperation,
        OperationType.MERGE: MergeOperation,
        OperationType.ADD_WATERMARK: AddWatermarkOperation,
        OperationType.ADJUST_VOLUME: AdjustVolumeOperation,
        OperationType.ADD_TEXT_OVERLAY: AddTextOverlayOperation,
        OperationType.ADD_AUDIO: AddAudioOperation,
        OperationType.VIDEO_OVERLAY: VideoOverlayOperation,
        OperationType.REMOTION_RENDER: RemotionRenderOperation,
        OperationType.DETECT_HIGHLIGHTS: DetectHighlightsOperation,
        OperationType.EXTRACT_CLIPS: ExtractClipsOperation,
        OperationType.NORMALIZE: NormalizeOperation,
        OperationType.PLAN_SCENES: PlanScenesOperation,
        OperationType.SELECT_CLIPS: SelectClipsOperation,
        OperationType.EVAL_CUTS: EvalCutsOperation,
        OperationType.DETECT_FILLERS: DetectFillersOperation,
        OperationType.DETECT_SPEAKERS: DetectSpeakersOperation,
        OperationType.FAST_SUBTITLES: FastSubtitlesOperation,
        OperationType.FILMSTRIP: FilmstripOperation,
        OperationType.ANALYZE_PROFILE: AnalyzeProfileOperation,
    }
    
    handler = handlers.get(op_type)
    if not handler:
        raise NotImplementedError(f"Operation {op_type} not implemented yet")
        
    return handler
