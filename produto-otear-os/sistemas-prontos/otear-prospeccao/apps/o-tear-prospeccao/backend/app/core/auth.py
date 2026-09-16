from fastapi import Depends, HTTPException, Header
from app.core.config import get_settings


async def verify_api_key(x_api_key: str = Header(...)):
    settings = get_settings()
    if x_api_key != settings.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


async def verify_webhook_secret(x_webhook_secret: str = Header(...)):
    settings = get_settings()
    if x_webhook_secret != settings.inbound_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return x_webhook_secret
