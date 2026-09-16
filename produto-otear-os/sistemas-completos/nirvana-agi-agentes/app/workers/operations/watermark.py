from app.workers.operations.base import BaseOperation
from typing import Dict, Any
import ffmpeg
import httpx
import os
import uuid

class AddWatermarkOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        if 'image_url' not in params:
            raise ValueError("Missing 'image_url' for watermark operation")

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        AddWatermarkOperation.validate_params(params)
        
        image_url = params['image_url']
        position = params.get('position', 'top-right')
        opacity = params.get('opacity', 1.0) # 0.0 to 1.0 (requires format=rgba filter usually)
        scale = params.get('scale', 0.2) # Relative scale to video width? Or fixed
        
        # Determine Overlay coordinates
        # FFmpeg overlay: x=...:y=...
        # W, H = video dims
        # w, h = watermark dims
        
        # Parding/Margin
        margin = 20
        
        pos_expr = {
            'top-left': f"x={margin}:y={margin}",
            'top-right': f"x=W-w-{margin}:y={margin}",
            'bottom-left': f"x={margin}:y=H-h-{margin}",
            'bottom-right': f"x=W-w-{margin}:y=H-h-{margin}",
            'center': f"x=(W-w)/2:y=(H-h)/2"
        }
        
        overlay_xy = pos_expr.get(position, f"x=W-w-{margin}:y={margin}")
        
        temp_image = f"/tmp/{uuid.uuid4()}_watermark.png"
        
        print(f"Downloading watermark image: {image_url}")
        
        try:
             # Download Sync
            with open(temp_image, 'wb') as f:
                with httpx.stream('GET', image_url) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"Failed to download image: {response.status_code}")
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            
            # Process
            main_video = ffmpeg.input(input_path)
            watermark = ffmpeg.input(temp_image)
            
            # Scale watermark if needed (simple scaling)
            # scale=iw*0.2:-1
            # Note: We need to apply scaling to the watermark input *before* overlay
            # But params['scale'] is float (e.g. 0.2 relative to ITSELF? or Video?).
            # Usually users want "make logo 20% of video width".
            # For simplicity: scale=iw*scale:-1 (relative to logo original size) 
            # OR advanced: scale2ref can be used to scale relative to main video.
            
            # Let's simple-scale the watermark by factor
            watermark_scaled = watermark.filter('scale', f"iw*{scale}", "-1")
            
            # Opacity?
            # format=rgba,colorchannelmixer=aa=0.5
            if opacity < 1.0:
                 watermark_scaled = watermark_scaled.filter('format', 'rgba').filter('colorchannelmixer', aa=opacity)
            
            # Overlay
            # [0][1]overlay=...
            stream = ffmpeg.filter([main_video, watermark_scaled], 'overlay', overlay_xy)
            
            # Output
            # We map audio from main_video (overlay consumes video streams)
            # ffmpeg-python overlay usually outputs video only stream
            # We need to map audio from input 0 explicitly?
            # Actually filter([...]) returns a node. We output node + main_video.audio
            
            stream = ffmpeg.output(stream, main_video.audio, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')
            ffmpeg.run(stream, overwrite_output=True)
            
        except httpx.RequestError as e:
            raise RuntimeError(f"Network error downloading image: {str(e)}")
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg watermark failed: {e.stderr.decode() if e.stderr else str(e)}")
        finally:
            if os.path.exists(temp_image):
                os.remove(temp_image)
