from app.workers.operations.base import BaseOperation
from app.services.whisper_service import WhisperService
from typing import Dict, Any
import json
import shutil

class TranscribeOperation(BaseOperation):
    @staticmethod
    def validate_params(params: Dict[str, Any]):
        pass # Parâmetros opcionais (language, model)

    @staticmethod
    def execute(input_path: str, output_path: str, params: Dict[str, Any]):
        # Extrair áudio primeiro (mais rápido que passar vídeo direto pro whisper as vezes)
        # Mas faster-whisper aceita vídeo direto via ffmpeg interno.
        
        model_size = params.get('model', 'base')
        language = params.get('language') # None = auto
        
        service = WhisperService(model_size=model_size)
        result = service.transcribe(input_path, language=language)
        
        # Salvar JSON da transcrição
        # output_path aqui é esperado ser o vídeo de saída pelo pipeline
        # Vamos copiar o vídeo de entrada para saída (bypass) e salvar o JSON separado
        
        shutil.copy2(input_path, output_path)
        
        # Salvar JSON "sidecar"
        json_path = output_path + ".json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"Transcription saved to {json_path}")
