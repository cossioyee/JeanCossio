from datetime import datetime

from bot.core import tiempo


def test_ahora_utc_es_naive():
    ahora = tiempo.ahora_utc()
    assert ahora.tzinfo is None


def test_a_hora_local_convierte_utc_a_panama():
    # Panamá es UTC-5 todo el año (no tiene horario de verano)
    dt_utc = datetime(2026, 7, 3, 12, 0)
    local = tiempo.a_hora_local(dt_utc)
    assert local.hour == 7
    assert local.day == 3


def test_a_hora_local_cruce_de_medianoche():
    # 02:00 UTC del día 4 = 21:00 del día 3 en Panamá
    dt_utc = datetime(2026, 7, 4, 2, 0)
    local = tiempo.a_hora_local(dt_utc)
    assert local.hour == 21
    assert local.day == 3


def test_ahora_local_tiene_timezone():
    assert tiempo.ahora_local().tzinfo is not None
