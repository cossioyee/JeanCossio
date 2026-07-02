"""
Envío de mensajes WhatsApp via Twilio.
Rate limit de Twilio Sandbox: ~1 msg/seg. No agregar sleeps — con 2 usuarios
los recordatorios se envían en ráfaga pequeña sin problema.
"""
import os

from loguru import logger
from twilio.rest import Client

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
    return _client


def send(to: str, body: str) -> None:
    from_number = os.environ["TWILIO_WHATSAPP_NUMBER"]
    try:
        _get_client().messages.create(from_=from_number, to=to, body=body)
        logger.info(f"Mensaje enviado a {to}")
    except Exception:
        logger.exception(f"Error al enviar mensaje a {to}")
