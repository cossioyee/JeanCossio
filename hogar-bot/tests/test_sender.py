import pytest

from bot.whatsapp import sender


class FakeMessages:
    def __init__(self):
        self.enviados = []

    def create(self, from_, to, body):
        self.enviados.append({"from": from_, "to": to, "body": body})


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()


@pytest.fixture
def cliente_falso(monkeypatch):
    monkeypatch.setenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    fake = FakeClient()
    monkeypatch.setattr(sender, "_client", fake)
    return fake


def test_send_envia_con_numero_de_origen(cliente_falso):
    sender.send(to="whatsapp:+50760000001", body="hola")

    assert cliente_falso.messages.enviados == [{
        "from": "whatsapp:+14155238886",
        "to": "whatsapp:+50760000001",
        "body": "hola",
    }]


def test_send_no_propaga_errores_de_twilio(cliente_falso, monkeypatch):
    def explota(**kwargs):
        raise ConnectionError("Twilio caído")

    monkeypatch.setattr(cliente_falso.messages, "create", explota)

    # No debe lanzar: un recordatorio fallido no puede tumbar el scheduler
    sender.send(to="whatsapp:+50760000001", body="hola")
