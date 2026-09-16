import httpx
import json

VIDEO_SERVICE_URL = "https://otear-otear-editavideos.qc7qit.easypanel.host"
VIDEO_SERVICE_KEY = os.getenv("VIDEO_EDITOR_API_KEY", "test-key")

def add_subtitles():
    video_url = "https://teste-minio.qc7qit.easypanel.host/videos/maquina.mp4"
    
    operations = [
        {
            "type": "auto_subtitle",
            "params": {
                "language": "pt",
                "model": "base",
                "burn_in": True,
                "style": {
                    "font_size": 20,
                    "color": "#FFFFFF",
                    "position": "bottom",
                    "animation": "word-by-word"
                }
            }
        }
    ]
    
    payload = {
        "video_url": video_url,
        "operations": operations,
        "output_format": "mp4"
    }
    
    headers = {
        "x-api-key": VIDEO_SERVICE_KEY
    }
    
    print(f"Sending request to {VIDEO_SERVICE_URL}/api/v1/videos/edit...")
    response = httpx.post(
        f"{VIDEO_SERVICE_URL}/api/v1/videos/edit",
        data={"request": json.dumps(payload)},
        headers=headers,
        timeout=120.0
    )
    
    print(f"Status: {response.status_code}")
    try:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        if "task_id" in result:
            print(f"Status URL: {VIDEO_SERVICE_URL}/api/v1/videos/status/{result['task_id']}")
    except Exception as e:
        print(f"Failed to parse response: {response.text}")

if __name__ == "__main__":
    add_subtitles()
