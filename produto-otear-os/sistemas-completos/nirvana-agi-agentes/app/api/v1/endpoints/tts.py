from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import io
import os

router = APIRouter()

# ElevenLabs config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

class TTSRequest(BaseModel):
    text: str
    voice_id: str | None = None

@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using ElevenLabs API.
    Returns audio stream (mp3).
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs API key not configured. Add ELEVENLABS_API_KEY to environment."
        )
    
    voice_id = request.voice_id or ELEVENLABS_VOICE_ID
    
    url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": request.text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ElevenLabs error: {response.text}"
                )
            
            # Return audio as streaming response
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=speech.mp3"}
            )
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ElevenLabs API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_voices():
    """
    List available ElevenLabs voices.
    """
    if not ELEVENLABS_API_KEY:
        # Return default voices if API key not configured
        return {
            "voices": [
                {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "labels": {"accent": "american"}},
                {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "labels": {"accent": "american"}},
                {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "labels": {"accent": "american"}},
                {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "labels": {"accent": "american"}},
            ]
        }
    
    url = f"{ELEVENLABS_BASE_URL}/voices"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch voices")
            
            return response.json()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
