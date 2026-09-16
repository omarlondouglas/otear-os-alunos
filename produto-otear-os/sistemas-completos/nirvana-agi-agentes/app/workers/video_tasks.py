from celery import Task
from celery.exceptions import SoftTimeLimitExceeded
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.job import VideoJob, JobStatus
from app.workers.operations import get_operation_handler
from app.core.storage import save_processed_file, get_file_path, STORAGE_PATH
import logging
import json
from datetime import datetime
import traceback
import os
from pathlib import Path

from app.services.video_presets import VideoPresets

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=1)
def process_video_task(self: Task, job_id: str):
    db = SessionLocal()
    try:
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Processing job {job_id}")
        
        # O arquivo de entrada já é um caminho absoluto salvo pelo storage
        current_video_path = job.input_video_path
        
        # Pipeline de operações
        # Expand presets if present
        all_operations = []
        for op in job.operations:
            if op['type'] == 'preset':
                preset_name = op['params'].get('name', '')
                preset_ops = VideoPresets.get_operations(preset_name)
                if preset_ops:
                    all_operations.extend(preset_ops)
                else:
                    logger.warning(f"Preset '{preset_name}' not found, skipping.")
            else:
                all_operations.append(op)

        total_ops = len(all_operations)
        
        for i, op_data in enumerate(all_operations):
            op_type = op_data['type']
            params = op_data['params']
            
            logger.info(f"Running operation {i+1}/{total_ops}: {op_type}")
            
            handler = get_operation_handler(op_type)
            
            # Arquivo temporário para o resultado desta etapa
            temp_output = f"/tmp/{job_id}_step_{i}.mp4"
            
            # Executar
            handler.execute(current_video_path, temp_output, params)
            
            # Atualizar progresso
            job.progress = int(((i + 1) / total_ops) * 100)
            db.commit()
            
            # O output desta etapa vira o input da próxima
            current_video_path = temp_output

        # Finalização
        public_url = os.getenv("PUBLIC_API_URL", "").rstrip("/")

        # Check if last operation produced special output
        last_op_type = all_operations[-1]["type"] if all_operations else ""
        is_clips_job = last_op_type == "extract_clips"
        is_plan_job = last_op_type == "plan_scenes"
        is_filmstrip_job = last_op_type == "filmstrip"
        is_transcribe_job = last_op_type == "transcribe"

        # Transcribe saves a sidecar JSON next to the passthrough video. When
        # transcription is the final operation, expose the JSON to the frontend.
        if is_transcribe_job:
            transcript_path = current_video_path + ".json"
            if os.path.exists(transcript_path):
                final_filename = f"{job_id}_transcript.json"
                final_path = str(Path(STORAGE_PATH) / final_filename)
                import shutil as shutil_transcript
                shutil_transcript.move(transcript_path, final_path)

                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.output_video_path = final_path
                if public_url:
                    job.download_url = f"{public_url}/static/{final_filename}"
                else:
                    job.download_url = f"/static/{final_filename}"
                logger.info(f"[WORKER] Transcript saved: {job.download_url}")
                db.commit()
                return
            logger.warning("[WORKER] transcribe did not produce sidecar JSON, falling through")

        # Handle plan_scenes output: save sidecar .scenes.json as the final output
        if is_plan_job:
            scenes_path = current_video_path + ".scenes.json"
            if os.path.exists(scenes_path):
                final_filename = f"{job_id}_final.json"
                final_path = str(Path(STORAGE_PATH) / final_filename)
                import shutil as shutil2
                shutil2.move(scenes_path, final_path)

                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.utcnow()
                job.output_video_path = final_path
                if public_url:
                    job.download_url = f"{public_url}/static/{final_filename}"
                else:
                    job.download_url = f"/static/{final_filename}"
                logger.info(f"[WORKER] Scene plan saved: {job.download_url}")
                db.commit()
                return
            else:
                logger.warning(f"[WORKER] plan_scenes did not produce .scenes.json, falling through")

        # Handlers que produzem JSON puro como saida final
        json_output_jobs = {
            "select_clips": ("clips.json", "clips.review.md"),
            "eval_cuts": ("eval.json", "eval.review.md"),
            "detect_fillers": ("fillers.json", "fillers.review.md"),
            "detect_speakers": ("speakers.json", None),
            "analyze_profile": ("profile_analysis.json", "profile_analysis.review.md"),
        }
        if last_op_type in json_output_jobs and os.path.exists(current_video_path):
            suffix, review_suffix = json_output_jobs[last_op_type]
            final_filename = f"{job_id}_{suffix}"
            final_path = str(Path(STORAGE_PATH) / final_filename)
            import shutil as shutil_json
            shutil_json.move(current_video_path, final_path)
            if review_suffix:
                review_src = current_video_path + ".review.md"
                if os.path.exists(review_src):
                    shutil_json.move(review_src, str(Path(STORAGE_PATH) / f"{job_id}_{review_suffix}"))
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_video_path = final_path
            if public_url:
                job.download_url = f"{public_url}/static/{final_filename}"
            else:
                job.download_url = f"/static/{final_filename}"
            logger.info(f"[WORKER] {last_op_type} JSON saved: {job.download_url}")
            db.commit()
            return

        # filmstrip: output PNG composite
        if is_filmstrip_job and os.path.exists(current_video_path):
            final_filename = f"{job_id}_filmstrip.png"
            final_path = str(Path(STORAGE_PATH) / final_filename)
            import shutil as shutil_png
            shutil_png.move(current_video_path, final_path)
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_video_path = final_path
            if public_url:
                job.download_url = f"{public_url}/static/{final_filename}"
            else:
                job.download_url = f"/static/{final_filename}"
            logger.info(f"[WORKER] Filmstrip saved: {job.download_url}")
            db.commit()
            return

        if is_clips_job:
            # Handle multi-clip output: save each clip + manifest
            try:
                with open(current_video_path, "r", encoding="utf-8") as f:
                    manifest = json.loads(f.read())
            except Exception:
                manifest = {"clips": []}

            # Move each clip file to storage and build download URLs
            for clip in manifest.get("clips", []):
                clip_source = clip.get("file_path", "")
                if clip_source and os.path.exists(clip_source):
                    clip_filename = f"{job_id}_{clip['filename']}"
                    clip_dest = save_processed_file(clip_source, clip_filename)
                    if public_url:
                        clip["download_url"] = f"{public_url}/static/{clip_filename}"
                    else:
                        clip["download_url"] = f"/static/{clip_filename}"
                    clip["file_path"] = str(clip_dest)

            # Save updated manifest as the final output
            final_filename = f"{job_id}_final.json"
            final_path = str(Path(STORAGE_PATH) / final_filename)
            with open(final_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_video_path = final_path
            if public_url:
                job.download_url = f"{public_url}/static/{final_filename}"
            else:
                job.download_url = f"/static/{final_filename}"
            logger.info(f"[WORKER] Clips job done: {manifest.get('total_clips', 0)} clips saved")
        else:
            # Standard single-file output
            final_filename = f"{job_id}_final.mp4"
            final_path = save_processed_file(current_video_path, final_filename)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_video_path = final_path
            if public_url:
                job.download_url = f"{public_url}/static/{final_filename}"
                logger.info(f"[WORKER] download_url construída via gateway: {job.download_url}")
            else:
                job.download_url = f"/static/{final_filename}"
                logger.warning(f"[WORKER] PUBLIC_API_URL não definida, usando path relativo: {job.download_url}")

        db.commit()

    except SoftTimeLimitExceeded:
        logger.error(f"Job {job_id} exceeded processing time limit (soft kill)")
        if job:
            job.status = JobStatus.FAILED
            job.error_message = "Timeout: o vídeo é muito longo ou complexo para processar dentro do limite de tempo"
            db.commit()
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        logger.error(traceback.format_exc())

        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()

        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
