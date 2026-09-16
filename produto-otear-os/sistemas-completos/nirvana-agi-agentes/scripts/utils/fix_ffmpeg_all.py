import os
import re

directory = r'd:\agi-criar agentes\agi-videos\app\workers\operations'

replace_patterns = [
    (r"ffmpeg\.output\(v_out, a_out, output_path\)", 
     r"ffmpeg.output(v_out, a_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')"),
     
    (r"ffmpeg\.output\(v_out, output_path\)", 
     r"ffmpeg.output(v_out, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')"),
     
    (r"ffmpeg\.output\(\s*stream, main_video\.audio, output_path\s*\)", 
     r"ffmpeg.output(stream, main_video.audio, output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart')"),
     
    (r"ffmpeg\.output\(\n\s*video_output,\n\s*audio_output,\n\s*output_path\n\s*\)", 
     r"ffmpeg.output(\n                video_output,\n                audio_output,\n                output_path,\n                vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart'\n            )"),

    (r"ffmpeg\.output\(\n\s*video_output,\n\s*output_path\n\s*\)", 
     r"ffmpeg.output(\n                video_output,\n                output_path,\n                vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart'\n            )"),
     
    (r"output = ffmpeg\.output\(\n\s*video,\n\s*mixed_audio,\n\s*output_path,\n\s*vcodec='libx264',\n\s*acodec='aac',\n\s*strict='experimental',\n\s*audio_bitrate='192k'\n\s*\)", 
     r"output = ffmpeg.output(\n            video,\n            mixed_audio,\n            output_path,\n            vcodec='libx264',\n            acodec='aac',\n            strict='experimental',\n            audio_bitrate='192k',\n            pix_fmt='yuv420p',\n            movflags='+faststart'\n        )"),

    (r"output = ffmpeg\.output\(\n\s*video_stream,\n\s*audio,\n\s*output_path,\n\s*vcodec='libx264',\n\s*acodec='aac',\n\s*strict='experimental'\n\s*\)", 
     r"output = ffmpeg.output(\n            video_stream,\n            audio,\n            output_path,\n            vcodec='libx264',\n            acodec='aac',\n            strict='experimental',\n            pix_fmt='yuv420p',\n            movflags='+faststart'\n        )"),
]

for file in os.listdir(directory):
    if not file.endswith('.py'): continue
    filepath = os.path.join(directory, file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    for pat, rep in replace_patterns:
        if re.search(pat, content):
            content = re.sub(pat, rep, content)
            modified = True
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filepath}')
