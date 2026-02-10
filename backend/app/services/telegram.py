
import httpx
from ..config import settings
import logging

logger = logging.getLogger(__name__)

async def send_telegram_message(message: str, chat_id: str = None):
    """
    Send a message to a Telegram chat.
    If chat_id is not provided, sends to the default configured group.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set. Skipping message send.")
        return

    target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    if not target_chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set and no chat_id provided. Skipping message send.")
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id": target_chat_id,
                "text": message,
                "parse_mode": "HTML"
            })
            response.raise_for_status()
            logger.info(f"Telegram message sent to {target_chat_id}")
            return response.json()
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return None
