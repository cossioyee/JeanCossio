from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from bot.db.database import get_db
from bot.db.models import Person

router = APIRouter(prefix="/webhook", tags=["whatsapp"])


def _validate_twilio_signature(request: Request, body: bytes) -> None:
    """Rechaza requests que no vengan de Twilio."""
    import os

    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    validator = RequestValidator(auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    # Twilio firma sobre los campos del form, no el body raw
    form_data = {}
    if body:
        from urllib.parse import parse_qs
        parsed = parse_qs(body.decode())
        form_data = {k: v[0] for k, v in parsed.items()}

    if not validator.validate(url, form_data, signature):
        raise HTTPException(status_code=403, detail="Firma Twilio inválida")


def _twiml_reply(text: str) -> Response:
    resp = MessagingResponse()
    resp.message(text)
    return Response(content=str(resp), media_type="application/xml")


def _get_sender(phone_number: str, db: Session) -> Person | None:
    return db.query(Person).filter_by(phone_number=phone_number).first()


@router.post("/twilio")
async def twilio_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    db: Session = Depends(get_db),
) -> Response:
    raw_body = await request.body()
    _validate_twilio_signature(request, raw_body)

    sender = _get_sender(From, db)
    if sender is None:
        return _twiml_reply("No estás registrado en el bot. Habla con Jean para que te agregue.")

    message = Body.strip()

    # Delegar al handler correspondiente según el contenido del mensaje
    from bot.core import dispatcher
    reply = dispatcher.handle(message=message, sender=sender, db=db)

    return _twiml_reply(reply)
