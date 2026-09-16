import os
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvolutionClient:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "agi")
        
        if not self.base_url:
            logger.warning("EVOLUTION_API_URL not set. WhatsApp replies will fail.")
        if not self.api_key:
            logger.warning("EVOLUTION_API_KEY not set. WhatsApp replies will fail.")

    async def send_message(self, remote_jid: str, text: str):
        """
        Sends a text message to a specific remoteJid using Evolution API.
        """
        if not self.base_url or not self.api_key:
            logger.error("Cannot send message: Missing configuration.")
            return None

        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": remote_jid, # API usually expects 'number' or 'remoteJid' depending on version, generic fallback
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": text
            }
        }
        
        # Evolution API v2 might use a different payload structure for 'number'.
        # Often it expects just the number string in the URL or body.
        # Let's try to be compatible. If remote_jid contains @s.whatsapp.net, we might need to strip it or keep it.
        # Usually sendText endpoint takes 'number' in body.
        
        # Adjust payload for common Evolution API / v2
        # Some versions use: {"number": "ZPqp...", "text": "..."} 
        # But standard v2 is often: 
        # POST /message/sendText/{instance}
        # { "number": "5511...", "text": "Msg", "delay": 1200 }
        
        # Redefining payload to robust standard
        payload = {
            "number": remote_jid.replace("@s.whatsapp.net", ""), 
            "text": text,
            "delay": 1200,
            "linkPreview": False
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"Sending WhatsApp message to {remote_jid}...")
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Message sent successfully: {response.json()}")
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP Error sending message: {e.response.text}")
                return None
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                return None
