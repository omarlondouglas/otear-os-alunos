
from fastapi import APIRouter, Request, BackgroundTasks
from app.services.evolution_client import EvolutionClient
from app.agents.agno_agents import orchestrator
from app.services.storage import StorageService
import json
import os
import logging

logger = logging.getLogger(__name__)


def _get_whatsapp_user_context(phone_number: str) -> dict:
    """
    Tenta encontrar o usuário no Supabase pelo telefone e retornar seu user_id.
    Se encontrar, os agentes usarão o perfil personalizado do usuário.
    Caso contrário, retorna dict vazio (agentes usam defaults globais).
    """
    try:
        from app.core.supabase import get_supabase
        client = get_supabase()
        # Busca por telefone no metadata do usuário do Supabase
        users = client.auth.admin.list_users()
        for user in users:
            # Checa phone ou user_metadata.phone
            if user.phone == phone_number:
                return {"user_id": str(user.id)}
            meta = user.user_metadata or {}
            if meta.get("phone") == phone_number or meta.get("whatsapp") == phone_number:
                return {"user_id": str(user.id)}
    except Exception as e:
        logger.debug(f"WhatsApp user lookup failed for {phone_number}: {e}")
    return {}

router = APIRouter()
evolution_client = EvolutionClient()

async def process_whatsapp_message(payload: dict):
    """
    Processa a mensagem recebida em background.
    """
    data = payload.get('data', {})
    key = data.get('key', {})
    from_me = key.get('fromMe', False)
    
    # Ignorar mensagens enviadas pelo próprio bot
    if from_me:
        return

    remote_jid = key.get('remoteJid') # Ex: 5511999999999@s.whatsapp.net
    if not remote_jid:
        return

    # Restrict to allowed number if set
    allowed_number = os.getenv("ALLOWED_NUMBER")
    if allowed_number:
        # Normalize: remove non-digit chars just in case, though usually env var is enough
        # Check if remote_jid starts with the allowed number (ignoring @s.whatsapp.net)
        # Assuming allowed_number is just digits e.g. "5511999999999"
        if not remote_jid.startswith(allowed_number):
            print(f"[Webhook] Ignored message from unauthorized number: {remote_jid}")
            return

    message_type = data.get('messageType')
    print(f"[Webhook] Message Type: {message_type}")
    print(f"[Webhook] Message Keys: {list(data.get('message', {}).keys())}")

    user_msg = ""
    media = {"videos": [], "images": []}
    storage_service = StorageService()

    # Robust Text Extraction
    if message_type == 'conversation':
        user_msg = data.get('message', {}).get('conversation', '')
    elif message_type == 'extendedTextMessage':
        user_msg = data.get('message', {}).get('extendedTextMessage', {}).get('text', '')
    elif message_type == 'imageMessage':
        img_msg = data.get('message', {}).get('imageMessage', {})
        user_msg = img_msg.get('caption', '')
        b64 = img_msg.get('base64')
        if b64:
            mimetype = img_msg.get('mimetype', 'image/png')
            ext = mimetype.split('/')[-1] if '/' in mimetype else 'png'
            url = storage_service.upload_base64(b64, ext, mimetype)
            if url: media["images"].append(url)
    elif message_type == 'videoMessage':
        vid_msg = data.get('message', {}).get('videoMessage', {})
        user_msg = vid_msg.get('caption', '')
        b64 = vid_msg.get('base64')
        if b64:
            mimetype = vid_msg.get('mimetype', 'video/mp4')
            ext = mimetype.split('/')[-1] if '/' in mimetype else 'mp4'
            url = storage_service.upload_base64(b64, ext, mimetype)
            if url: media["videos"].append(url)
    else:
        # Fallback: Try to find 'caption' or 'text' in the nested message object
        msg_obj = data.get('message', {})
        # Iterate over values to find string text (simple heuristic)
        for k, v in msg_obj.items():
            if isinstance(v, str): # e.g. 'conversation'
                user_msg = v
                break
            elif isinstance(v, dict): # e.g. 'imageMessage': {'caption': '...'}
                if 'caption' in v:
                    user_msg = v['caption']
                    break
                if 'text' in v:
                    user_msg = v['text']
                    break
    
    # NEW: Ensure media messages without captions aren't ignored
    if not user_msg:
         if media["images"]: user_msg = "[Imagem Recebida]"
         elif media["videos"]: user_msg = "[Vídeo Recebido]"
    
    # Se encontrou texto ou media, processa
    if user_msg or media["videos"] or media["images"]:
        import re
        urls = re.findall(r'(https?://[^\s]+)', user_msg)
        
        for url in urls:
            clean_url = url.split('?')[0].lower()
            if clean_url.endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v')):
                media["videos"].append(url)
            elif clean_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.heic')):
                media["images"].append(url)
        
        videos = media["videos"]  # Pass all videos, not just the first
        
        print(f"[Webhook] Mensagem recebida de {remote_jid}: {user_msg}")
        if media["videos"]:
             print(f"[Webhook] Videos detectados: {media['videos']}")
        if media["images"]:
             print(f"[Webhook] Imagens detectadas: {media['images']}")
        
        # Chamar o Orquestrador (Simulação - idealmente refatorar para chamar função pura)
        # Por enquanto, vamos chamar uma função adaptada ou simular a resposta
        
        # TODO: Refatorar Orchestrator para separar a lógica da rota FastAPI
        # Para este passo, vamos instanciar o fluxo manualmente ou chamar via request interno?
        # Vamos assumir que refatoraremos o orchestrator em breve.
        # Por hora, vamos responder um "Echo" melhorado.
        
        try:
           # Chamar o Orchestrator
           print("[Webhook] Chamando Orchestrator...")

           # Criar session_id baseado no número do usuário (para manter contexto)
           # Remove @s.whatsapp.net para ter apenas o número
           user_number = remote_jid.split('@')[0]
           session_id = f"whatsapp_{user_number}"

           print(f"[Webhook] Session ID: {session_id}")

           # Tentar enriquecer contexto com perfil do usuário (se cadastrado no Supabase)
           user_profile_context = _get_whatsapp_user_context(user_number)

           # Construir prompt com contexto de mídia
           prompt = user_msg
           if videos:
               prompt += f"\n\n[CONTEXTO: {len(videos)} vídeo(s) detectado(s): {', '.join(videos)}]"
           if media["images"]:
               prompt += f"\n\n[CONTEXTO: {len(media['images'])} imagem(ns) detectada(s): {', '.join(media['images'])}]"

           print(f"[Webhook] Prompt: {prompt}")

           # Executar orchestrator em thread separada (agno Team.run() é síncrono)
           import asyncio
           from concurrent.futures import ThreadPoolExecutor

           def run_orchestrator():
               return orchestrator.run(
                   prompt,
                   images=media["images"],
                   videos=videos,
                   session_id=session_id,
                   context=user_profile_context,
               )
           
           loop = asyncio.get_event_loop()
           with ThreadPoolExecutor() as executor:
               response = await loop.run_in_executor(executor, run_orchestrator)
           
           # Extrair resposta
           response_text = response.content if hasattr(response, 'content') else str(response)
           
           print(f"[Webhook] Resposta do Orchestrator ({len(response_text)} chars): {response_text[:200]}...")
           
           # Enviar resposta via Evolution API
           await evolution_client.send_message(remote_jid, response_text)
           
           print(f"[Webhook] Resposta enviada para {remote_jid}")

        except Exception as e:
            print(f"[Webhook] Erro CRÍTICO no processamento: {e}")
            import traceback
            traceback.print_exc()
            await evolution_client.send_message(remote_jid, "Ocorreu um erro interno ao processar sua solicitação.")



@router.post("/evolution")
async def evolution_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para receber webhook da Evolution API no Typebot/Global.
    """
    try:
        payload = await request.json()
        # print(f"[Webhook] Payload recebido: {json.dumps(payload)}") # Debug
        
        # Validar tipo de evento (apenas mensagens)
        event_type = payload.get('event')
        if event_type == 'messages.upsert':
            background_tasks.add_task(process_whatsapp_message, payload)
        
        return {"status": "success"}
    except Exception as e:
        print(f"[Webhook] Erro ao ler payload: {e}")
        return {"status": "error"}
