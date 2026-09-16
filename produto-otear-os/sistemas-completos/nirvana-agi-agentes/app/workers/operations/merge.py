from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import ffmpeg
import httpx
import os
import shutil
import uuid

class MergeOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'secondary_url' not in params:
            raise ValueError("Missing 'secondary_url' for merge operation")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        MergeOperation.validate_params(params)
        
        secondary_url = params['secondary_url']
        temp_secondary = f"/tmp/{uuid.uuid4()}_secondary.mp4"
        
        print(f"Downloading secondary video for merge: {secondary_url}")
        
        try:
            # Download Sync
            with open(temp_secondary, 'wb') as f:
                with httpx.stream('GET', secondary_url) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"Failed to download secondary video: {response.status_code}")
                    for chunk in response.iter_bytes():
                        f.write(chunk)
                        
            print("Merging videos...")
            
            # Complex Filter: [0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]
            # Assumes both have audio. If not, this is tricky.
            # To be safer, we just use ffmpeg-python concat which handles streams relatively well
            # but verifying streams existence is better.
            
            # Simple approach: Re-encode concat
            
            input1 = ffmpeg.input(input_path)
            input2 = ffmpeg.input(temp_secondary)
            
            # We force aspect ratio / resolution standardizing on the first video?
            # Ideally yes, but let's rely on FFmpeg's concat filter resilience or failures
            
            # [0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]
            
            # Check if input1 has audio
            probe1 = ffmpeg.probe(input_path)
            has_audio1 = any(s['codec_type'] == 'audio' for s in probe1['streams'])
            
            probe2 = ffmpeg.probe(temp_secondary)
            has_audio2 = any(s['codec_type'] == 'audio' for s in probe2['streams'])
            
            if has_audio1 and has_audio2:
                 joined = ffmpeg.concat(input1, input2, v=1, a=1).node
                 v_out, a_out = joined[0], joined[1]
                 stream = ffmpeg.output(v_out, a_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')
            else:
                # Fallback: Video only concat if one lacks audio (or ignore audio)
                print("Warning: One of the videos lacks audio. Merging video streams only.")
                joined = ffmpeg.concat(input1.video, input2.video, v=1, a=0).node
                v_out = joined[0]
                stream = ffmpeg.output(v_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')

            ffmpeg.run(stream, overwrite_output=True)
            
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error downloading video: {str(e)}")
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg merge failed: {e.stderr.decode() if e.stderr else str(e)}")
        finally:
            if os.path.exists(temp_secondary):
                os.remove(temp_secondary)
