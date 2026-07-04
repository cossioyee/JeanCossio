import pytest

from bot.db import seed
from bot.db.models import Person, Setting


@pytest.fixture
def entorno_seed(monkeypatch, db_factory):
    monkeypatch.setenv("JEAN_PHONE_NUMBER", "whatsapp:+50760000001")
    monkeypatch.setenv("ANELYS_PHONE_NUMBER", "whatsapp:+50760000002")
    monkeypatch.setattr(seed, "SessionLocal", db_factory)
    monkeypatch.setattr(seed, "create_tables", lambda: None)


def test_seed_crea_personas_y_settings(entorno_seed, db_session):
    seed.run()

    assert db_session.query(Person).count() == 2
    jean = db_session.query(Person).filter_by(name="Jean").one()
    assert jean.is_admin is True
    assert db_session.query(Setting).count() == 2


def test_seed_es_idempotente(entorno_seed, db_session):
    seed.run()
    seed.run()

    assert db_session.query(Person).count() == 2
    assert db_session.query(Setting).count() == 2


def test_seed_falla_claro_si_falta_variable(monkeypatch):
    monkeypatch.delenv("JEAN_PHONE_NUMBER", raising=False)

    with pytest.raises(RuntimeError, match="JEAN_PHONE_NUMBER"):
        seed._personas()


def test_importar_seed_no_requiere_variables(monkeypatch):
    # Regresión v2: antes _personas era una constante evaluada en el import,
    # y un .env incompleto rompía main.py antes de arrancar
    monkeypatch.delenv("JEAN_PHONE_NUMBER", raising=False)
    monkeypatch.delenv("ANELYS_PHONE_NUMBER", raising=False)

    import importlib
    importlib.reload(seed)
