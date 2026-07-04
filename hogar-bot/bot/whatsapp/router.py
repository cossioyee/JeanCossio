import os
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from bot.db.database import get_db
from bot.db.models import Person

router = APIRouter(prefix="/webhook", tags=["whatsapp"])


def _parse_form(body: bytes) -> dict[str, str]:
    if not body:
        return {}
    # keep_blank_values: Twilio firma sobre TODOS los parámetros, incluidos
    # los vacíos (ej. Body="" en mensajes solo-media); si parse_qs los
    # descarta, la firma calculada nunca coincide y se rechaza con 403
    parsed = parse_qs(body.decode(), keep_blank_values=True)
    return {k: v[0] for k, v in parsed.items()}


def _validate_twilio_signature(request: Request, form_data: dict[str, str]) -> None:
    """Rechaza requests que no vengan de Twilio."""
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    validator = RequestValidator(auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Firma Twilio inválida")


def _twiml_reply(text: str) -> Response:
    resp = MessagingResponse()
    resp.message(text)
    return Response(content=str(resp), media_type="application/xml")


def _get_sender(phone_number: str, db: Session) -> Person | None:
    return db.query(Person).filter_by(phone_number=phone_number).first()


@router.post("/twilio")
async def twilio_webhook(request: Request, db: Session = Depends(get_db)) -> Response:
    raw_body = await request.body()
    form_data = _parse_form(raw_body)
    _validate_twilio_signature(request, form_data)

    from_number = form_data.get("From", "")
    sender = _get_sender(from_number, db)
    if sender is None:
        return _twiml_reply("No estás registrado en el bot. Habla con Jean para que te agregue.")

    message = form_data.get("Body", "").strip()

    # Delegar al handler correspondiente según el contenido del mensaje
    from bot.core import dispatcher
    reply = dispatcher.handle(message=message, sender=sender, db=db)

    return _twiml_reply(reply)
