"""
Detect Speakers Operation
Active speaker detection via correlacao audio-visual usando MediaPipe Face Landmarker.
Para cada clipe, detecta a posicao do rosto que esta falando ao longo do tempo.

Output JSON:
  {
    "samples": [{"t": 0.2, "x": 0.5, "y": 0.3, "h": 0.3}, ...],
    "meanFaces": 1.2
  }
  - x, y: centro do rosto ativo (0-1, normalizado)
  - h: altura do rosto (0-1)
  - mean_faces: media de rostos por frame (heuristica de single-vs-multi-speaker)

Requisitos:
  - mediapipe + opencv-python
  - python/models/face_landmarker.task (download em
    https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task)

Input:
  - input_path: video file
  - params:
      model_path: caminho do face_landmarker.task (default: app/workers/models/face_landmarker.task)
      sample_fps: amostragem (default 5.0)

Output:
  - output_path (.json): {samples, meanFaces}
"""

from app.workers.operations.base import BaseOperation
from typing import Dict, Any, List, Optional, Tuple
import json
import os
import shutil
import subprocess


SAMPLE_FPS = 5.0
AUDIO_SR = 16000
AUDIO_WIN_MS = 100
SMOOTH_K = 7

UPPER_INNER, LOWER_INNER, LEFT_CORNER, RIGHT_CORNER = 13, 14, 61, 291

DEFAULT_MODEL_PATH = os.environ.get(
    "FACE_LANDMARKER_MODEL_PATH",
    "/app/app/workers/models/face_landmarker.task",
)


class DetectSpeakersOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        try:
            import cv2  # noqa: F401
            import numpy as np  # noqa: F401
            import mediapipe as mp  # noqa: F401
        except ImportError as e:
            raise RuntimeError(
                f"detect_speakers requires mediapipe + opencv-python: {e}. "
                "pip install mediapipe opencv-python"
            )

        model_path = params.get("model_path") or DEFAULT_MODEL_PATH
        if not os.path.exists(model_path):
            raise RuntimeError(
                f"detect_speakers: face_landmarker.task not found at {model_path}. "
                "Download em https://storage.googleapis.com/mediapipe-models/"
                "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            )

        sample_fps = float(params.get("sample_fps", SAMPLE_FPS))
        result = _process_video(input_path, model_path, sample_fps)

        # output JSON sidecar + passthrough do video
        if not output_path.endswith(".json"):
            shutil.copy2(input_path, output_path)
            json_path = output_path + ".speakers.json"
        else:
            json_path = output_path

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        n = len(result.get("samples", []))
        mf = result.get("meanFaces", 0)
        print(f"[DetectSpeakers] {n} samples, avg {mf:.1f} faces/frame -> {json_path}")


def _process_video(video_path: str, model_path: str, sample_fps: float) -> Dict[str, Any]:
    import numpy as np

    times, frames, dur = _detect_faces(video_path, model_path, sample_fps)
    if not times:
        return {"samples": [], "meanFaces": 0}
    rms = _extract_audio_rms(video_path, times)
    xyh = _active_speaker_xyh(times, frames, rms)
    xs = _smooth([p[0] for p in xyh])
    ys = _smooth([p[1] for p in xyh])
    hs = _smooth([p[2] for p in xyh])
    face_counts = [len(f) for f in frames]
    mean_faces = float(np.mean(face_counts)) if face_counts else 0.0
    samples = [
        {"t": round(t, 3), "x": round(float(x), 4), "y": round(float(y), 4), "h": round(float(h), 4)}
        for t, x, y, h in zip(times, xs, ys, hs)
    ]
    return {"samples": samples, "meanFaces": round(mean_faces, 2), "duration": round(dur, 2)}


def _extract_audio_rms(video_path: str, sample_times: List[float]):
    import numpy as np
    cmd = [
        "ffmpeg", "-v", "error", "-i", video_path,
        "-ac", "1", "-ar", str(AUDIO_SR), "-f", "s16le", "-",
    ]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    win = int(AUDIO_SR * AUDIO_WIN_MS / 1000)
    rms = np.zeros(len(sample_times))
    for i, t in enumerate(sample_times):
        s = max(0, int(t * AUDIO_SR - win // 2))
        e = min(len(pcm), s + win)
        if e > s:
            rms[i] = float(np.sqrt(np.mean(pcm[s:e] ** 2)))
    return rms


def _detect_faces(video_path: str, model_path: str, sample_fps: float):
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total / fps if fps > 0 else 0
    stride = max(1, int(fps / sample_fps))

    options = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_path),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=3,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    sample_times: List[float] = []
    frames_data: List[List[Dict[str, float]]] = []
    with vision.FaceLandmarker.create_from_options(options) as lm:
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % stride == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                ts_ms = int((idx / fps) * 1000) if fps > 0 else idx
                res = lm.detect_for_video(mp_img, ts_ms)
                faces = []
                if res.face_landmarks:
                    for lms in res.face_landmarks:
                        xs = [pt.x for pt in lms]
                        ys = [pt.y for pt in lms]
                        cx = (min(xs) + max(xs)) / 2
                        cy = (min(ys) + max(ys)) / 2
                        fw = max(xs) - min(xs)
                        fh = max(ys) - min(ys)
                        ui, li_ = lms[UPPER_INNER], lms[LOWER_INNER]
                        lc, rc = lms[LEFT_CORNER], lms[RIGHT_CORNER]
                        mouth_w = abs(lc.x - rc.x) or 1e-6
                        mouth_open = abs(ui.y - li_.y) / mouth_w
                        faces.append({"cx": cx, "cy": cy, "w": fw, "h": fh, "mo": mouth_open})
                sample_times.append(idx / fps if fps > 0 else float(idx))
                frames_data.append(faces)
            idx += 1
    cap.release()
    return sample_times, frames_data, duration


def _iou(a, b):
    ax1, ay1 = a["cx"] - a["w"] / 2, a["cy"] - a["h"] / 2
    ax2, ay2 = a["cx"] + a["w"] / 2, a["cy"] + a["h"] / 2
    bx1, by1 = b["cx"] - b["w"] / 2, b["cy"] - b["h"] / 2
    bx2, by2 = b["cx"] + b["w"] / 2, b["cy"] + b["h"] / 2
    iw = max(0, min(ax2, bx2) - max(ax1, bx1))
    ih = max(0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    u = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / u if u > 0 else 0


def _track_faces(frames_data):
    tracks = []
    active: Dict[int, Dict[str, float]] = {}
    for fi, faces in enumerate(frames_data):
        used = set()
        for face in faces:
            best_id, best_score = None, 0.3
            for tid, last in active.items():
                if tid in used:
                    continue
                s = _iou(last, face)
                if s > best_score:
                    best_score, best_id = s, tid
            if best_id is None:
                best_id = len(tracks)
                tracks.append({"id": best_id, "samples": []})
            tracks[best_id]["samples"].append((fi, face))
            active[best_id] = face
            used.add(best_id)
    return tracks


def _ffill(a):
    import numpy as np
    a = a.copy()
    last = np.nan
    for i in range(len(a)):
        if np.isnan(a[i]):
            a[i] = last
        else:
            last = a[i]
    last = np.nan
    for i in range(len(a) - 1, -1, -1):
        if np.isnan(a[i]):
            a[i] = last
        else:
            last = a[i]
    return a


def _active_speaker_xyh(sample_times, frames_data, audio_rms):
    import numpy as np

    n = len(sample_times)
    tracks = _track_faces(frames_data)

    if not tracks:
        return [(0.5, 0.3, 0.3)] * n

    if len(tracks) == 1:
        xs = np.full(n, np.nan)
        ys = np.full(n, np.nan)
        hs = np.full(n, np.nan)
        for fi, f in tracks[0]["samples"]:
            xs[fi] = f["cx"]
            ys[fi] = f["cy"] - f["h"] / 2
            hs[fi] = f["h"]
        xs = _ffill(xs); ys = _ffill(ys); hs = _ffill(hs)
        xs = np.where(np.isnan(xs), 0.5, xs)
        ys = np.where(np.isnan(ys), 0.3, ys)
        hs = np.where(np.isnan(hs), 0.3, hs)
        return list(zip(xs.tolist(), ys.tolist(), hs.tolist()))

    track_mouth: Dict[int, Any] = {}
    track_xyh: Dict[int, Tuple[Any, Any, Any]] = {}
    for t in tracks:
        mo = np.full(n, np.nan)
        cx = np.full(n, np.nan); cy = np.full(n, np.nan); ch = np.full(n, np.nan)
        for fi, f in t["samples"]:
            mo[fi] = f["mo"]; cx[fi] = f["cx"]; cy[fi] = f["cy"] - f["h"] / 2; ch[fi] = f["h"]
        track_mouth[t["id"]] = mo
        track_xyh[t["id"]] = (_ffill(cx), _ffill(cy), _ffill(ch))

    win = max(3, int(SAMPLE_FPS * 1.5))
    out = []
    last_id = None
    for i in range(n):
        s, e = max(0, i - win // 2), min(n, i + win // 2 + 1)
        audio_seg = audio_rms[s:e]
        best_id, best_score = None, -2.0
        for tid, mo in track_mouth.items():
            seg = mo[s:e]
            mask = ~np.isnan(seg)
            if mask.sum() < 3:
                continue
            m, a = seg[mask], audio_seg[mask]
            if m.std() < 1e-4 or a.std() < 1e-4:
                score = 0.0
            else:
                score = float(np.corrcoef(m, a)[0, 1])
            if score > best_score:
                best_score, best_id = score, tid
        if best_id is None or best_score < 0.1:
            best_id = last_id
        if best_id is None:
            for tid in track_mouth:
                if not np.isnan(track_mouth[tid][i]):
                    best_id = tid
                    break
        if best_id is None:
            out.append((0.5, 0.3, 0.3))
        else:
            cx, cy, ch = track_xyh[best_id]
            fx = float(cx[i]) if not np.isnan(cx[i]) else 0.5
            fy = float(cy[i]) if not np.isnan(cy[i]) else 0.3
            fh = float(ch[i]) if not np.isnan(ch[i]) else 0.3
            out.append((fx, fy, fh))
            last_id = best_id
    return out


def _smooth(xs, k=SMOOTH_K):
    import numpy as np
    if len(xs) < k:
        return xs
    arr = np.array(xs, dtype=np.float32)
    pad = k // 2
    padded = np.pad(arr, pad, mode="edge")
    kernel = np.ones(k, dtype=np.float32) / k
    return np.convolve(padded, kernel, mode="valid").tolist()
