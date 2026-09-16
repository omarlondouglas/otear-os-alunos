import os
import httpx
import json
import time
import sys
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÃO
# Pega a URL do arquivo .env ou usa o valor padrão se não encontrar
BASE_URL = os.getenv("VIDEO_EDITOR_API_URL", "http://localhost:8001")
VIDEO_URL = "https://teste-minio.qc7qit.easypanel.host/stories/teste_jump.mp4" 

def test_video_edit():
    print(f"--- INICIANDO TESTE DE EDIÇÃO DE VÍDEO ---")
    print(f"Alvo: {BASE_URL}")
    print(f"Vídeo: {VIDEO_URL}")
    
    # 1. CRIAR PEDIDO
    print("\n1. Enviando solicitação de edição...")
    
    payload = {
        "video_url": VIDEO_URL,
        "operations": [
            {
                "type": "add_text_overlay",
                "params": {
                    "text": "TESTE MANUAL",
                    "position": "top",
                    "font_size": 40,
                    "color": "#FFFFFF",
                    "background_color": "#00000080"
                }
            }
        ],
        "output_format": "mp4"
    }
    
    # API Key para autenticação (se necessário)
    API_KEY = os.getenv("VIDEO_EDITOR_API_KEY")
    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY
        print(f"🔑 Usando API Key: {API_KEY[:4]}***")

    try:
        # Importante: O serviço espera um campo 'request' num Form Data, contendo o JSON
        response = httpx.post(
            f"{BASE_URL}/api/v1/videos/edit",
            data={"request": json.dumps(payload)},
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code != 200:
            print(f"❌ ERRO AO CRIAR JOB: {response.status_code}")
            print(response.text)
            return

        data = response.json()
        job_id = data.get("id")
        print(f"✅ Job Criado com Sucesso! ID: {job_id}")
        print(f"Status Inicial: {data.get('status')}")
        
    except Exception as e:
        print(f"❌ EXCEÇÃO AO CONECTAR: {e}")
        return

    # 2. MONITORAR STATUS
    print(f"\n2. Monitorando progresso do Job {job_id}...")
    
    print(f"\n2. Monitorando progresso do Job {job_id}...")
    print("⏳ O sistema verificará o status a cada 5 MINUTOS...")
    
    start_time = time.time()
    # 6 tentativas * 5 minutos = 30 minutos de timeout total
    max_retries = 6 
    
    for i in range(max_retries):
        # Espera 5 minutos ANTES de checar (garante a primeira checagem em 5 min)
        print(f"⏳ Aguardando 5 minutos... (Tentativa {i+1}/{max_retries})")
        time.sleep(300) 
        
        try:
            status_resp = httpx.get(f"{BASE_URL}/api/v1/videos/status/{job_id}", headers=headers, timeout=30.0)
            if status_resp.status_code == 200:
                job_data = status_resp.json()
                status = job_data.get("status")
                progress = job_data.get("progress", 0)
                
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Status: {status} | Progresso: {progress}%")
                
                if status == "completed":
                    print("\n✅ VÍDEO PROCESSADO COM SUCESSO!")
                    download_url = job_data.get("download_url")
                    
                    # Se vier URL relativa, corrigir para visualização
                    if download_url and download_url.startswith("/"):
                        download_url = f"{BASE_URL}{download_url}"
                        
                    print(f"URL DO VÍDEO: {download_url}")
                    print(f"Caminho interno: {job_data.get('output_video_path')}")
                    break
                
                elif status == "failed":
                    print("\n❌ FALHA NO PROCESSAMENTO")
                    print(f"Erro: {job_data.get('error_message')}")
                    break
            
            else:
                print(f"⚠️ Erro ao checar status: {status_resp.status_code}")
                
        except Exception as e:
            print(f"⚠️ Erro de conexão no polling: {e}")
            
    else:
        # Se o loop terminar sem break
        print("\n❌ TIMEOUT: O vídeo não concluiu após todas as tentativas (30 min).")

if __name__ == "__main__":
    test_video_edit()
