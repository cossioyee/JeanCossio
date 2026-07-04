import pytest
from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator

from bot.db.database import get_db
from main import app

_AUTH_TOKEN = "token_de_prueba"
_URL = "http://testserver/webhook/twilio"


@pytest.fixture
def client(monkeypatch, db_session):
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", _AUTH_TOKEN)
    app.dependency_overrides[get_db] = lambda: db_session
    # Sin "with": no se dispara el lifespan (que tocaría la DB real)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _post_firmado(client, params, token=_AUTH_TOKEN):
    firma = RequestValidator(token).compute_signature(_URL, params)
    return client.post(
        "/webhook/twilio",
        data=params,
        headers={"X-Twilio-Signature": firma},
    )


def test_firma_invalida_devuelve_403(client, jean):
    respuesta = client.post(
        "/webhook/twilio",
        data={"From": jean.phone_number, "Body": "listo"},
        headers={"X-Twilio-Signature": "firma-falsa"},
    )
    assert respuesta.status_code == 403


def test_sin_firma_devuelve_403(client, jean):
    respuesta = client.post(
        "/webhook/twilio",
        data={"From": jean.phone_number, "Body": "listo"},
    )
    assert respuesta.status_code == 403


def test_numero_desconocido_recibe_mensaje_amigable(client, jean):
    respuesta = _post_firmado(
        client, {"From": "whatsapp:+50799999999", "Body": "hola"}
    )
    assert respuesta.status_code == 200
    assert "No estás registrado" in respuesta.text


def test_mensaje_valido_pasa_por_el_dispatcher(client, jean):
    respuesta = _post_firmado(
        client, {"From": jean.phone_number, "Body": "mis tareas"}
    )
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("application/xml")
    assert "No tienes tareas asignadas" in respuesta.text


def test_parametro_vacio_no_rompe_la_firma(client, jean):
    # Twilio firma incluyendo parámetros vacíos (ej. Body="" en mensajes
    # solo-media); sin keep_blank_values esto devolvía 403 (fix de v2)
    respuesta = _post_firmado(
        client, {"From": jean.phone_number, "Body": "", "NumMedia": "1"}
    )
    assert respuesta.status_code == 200
