import shutil
from pathlib import Path
from fastapi import UploadFile
import os
import aiofiles

STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "/app/storage"))
UPLOADS_PATH = Path(os.getenv("UPLOADS_PATH", "/app/uploads"))

# Garantir que diretórios existem
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
UPLOADS_PATH.mkdir(parents=True, exist_ok=True)

async def save_upload(file: UploadFile, filename: str) -> str:
    """Salva um upload no disco local e retorna o caminho absoluto"""
    file_path = UPLOADS_PATH / filename
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    return str(file_path.absolute())

def get_file_path(filename: str) -> str:
    return str((UPLOADS_PATH / filename).absolute())

def save_processed_file(source_path: str, filename: str) -> str:
    """Move um arquivo processado para o storage final, junto com sidecars (.json, .srt)"""
    dest_path = STORAGE_PATH / filename
    shutil.move(source_path, dest_path)
    
    # Mover arquivos auxiliares que estÃo no mesmo prefixo
    for ext in ['.json', '.srt', '.vtt']:
        sidecar_source = source_path + ext
        if os.path.exists(sidecar_source):
            sidecar_dest = str(dest_path) + ext
            shutil.move(sidecar_source, sidecar_dest)
            
    return str(dest_path.absolute())
