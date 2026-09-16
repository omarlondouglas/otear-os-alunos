import os

def fix_ffmpeg_output(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'): continue
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            # Check single quotes
            if "vcodec='libx264', acodec='aac'" in content:
                content = content.replace("vcodec='libx264', acodec='aac'", "vcodec='libx264', acodec='aac', pix_fmt='yuv420p', movflags='+faststart'")
                modified = True
            
            # Check double quotes
            if 'vcodec=\"libx264\", acodec=\"aac\"' in content:
                content = content.replace('vcodec=\"libx264\", acodec=\"aac\"', 'vcodec=\"libx264\", acodec=\"aac\", pix_fmt=\"yuv420p\", movflags=\"+faststart\"')
                modified = True
                
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Fixed {filepath}')

if __name__ == '__main__':
    fix_ffmpeg_output(r'd:\agi-criar agentes\agi-videos\app\workers\operations')
