from datetime import datetime, time, timedelta

import pytest

from bot.core import scheduler, tiempo
from bot.db.models import Person, Setting, Task


@pytest.fixture
def envios(monkeypatch, db_factory):
    """Redirige el scheduler a la DB de test y captura los envíos de WhatsApp."""
    monkeypatch.setattr(scheduler, "SessionLocal", db_factory)
    capturados = []
    monkeypatch.setattr(
        scheduler.sender, "send",
        lambda to, body: capturados.append({"to": to, "body": body}),
    )
    return capturados


def _crear_tarea(db_session, persona, vencida=True, **kwargs):
    delta = timedelta(hours=-1) if vencida else timedelta(days=3)
    task = Task(
        name=kwargs.pop("name", "Lavar platos"),
        frequency_days=7,
        current_assignee_id=persona.id,
        created_by_id=persona.id,
        next_due_at=tiempo.ahora_utc() + delta,
        **kwargs,
    )
    db_session.add(task)
    db_session.commit()
    return task


# --- _send_reminders ---

def test_recordatorio_de_tarea_vencida(envios, db_session, jean, anelys):
    _crear_tarea(db_session, jean, vencida=True)

    scheduler._send_reminders()

    assert len(envios) == 1
    assert envios[0]["to"] == jean.phone_number
    assert "Lavar platos" in envios[0]["body"]


def test_tarea_no_vencida_no_se_recuerda(envios, db_session, jean, anelys):
    _crear_tarea(db_session, jean, vencida=False)

    scheduler._send_reminders()

    assert envios == []


def test_tarea_inactiva_no_se_recuerda(envios, db_session, jean, anelys):
    _crear_tarea(db_session, jean, vencida=True, is_active=False)

    scheduler._send_reminders()

    assert envios == []


def test_recordatorio_actualiza_last_reminder_sent_at(envios, db_session, jean, anelys):
    task = _crear_tarea(db_session, jean, vencida=True)

    scheduler._send_reminders()

    db_session.expire_all()
    assert task.last_reminder_sent_at is not None


def test_no_reenvia_si_el_ultimo_recordatorio_fue_reciente(envios, db_session, jean, anelys):
    _crear_tarea(
        db_session, jean, vencida=True,
        last_reminder_sent_at=tiempo.ahora_utc() - timedelta(minutes=30),
    )

    scheduler._send_reminders()

    assert envios == []


def test_si_reenvia_pasada_la_ventana_antiduplicado(envios, db_session, jean, anelys):
    _crear_tarea(
        db_session, jean, vencida=True,
        last_reminder_sent_at=tiempo.ahora_utc() - timedelta(hours=12),
    )

    scheduler._send_reminders()

    assert len(envios) == 1


def test_no_envia_en_horario_de_sueno(envios, db_session, jean, anelys):
    # Ventana que cubre todo el día: garantiza que la hora actual cae dentro
    jean.sleep_start = time(0, 0)
    jean.sleep_end = time(23, 59, 59)
    db_session.commit()
    _crear_tarea(db_session, jean, vencida=True)

    scheduler._send_reminders()

    assert envios == []


def test_agrupa_varias_tareas_en_un_solo_mensaje(envios, db_session, jean, anelys):
    _crear_tarea(db_session, jean, vencida=True, name="Lavar platos")
    _crear_tarea(db_session, jean, vencida=True, name="Sacar la basura")

    scheduler._send_reminders()

    assert len(envios) == 1
    assert "Lavar platos" in envios[0]["body"]
    assert "Sacar la basura" in envios[0]["body"]


# --- _en_horario_sueno ---

def test_sin_horario_de_sueno_configurado():
    persona = Person(name="X", phone_number="whatsapp:+1")
    assert scheduler._en_horario_sueno(persona, time(3, 0)) is False


def test_horario_de_sueno_rango_normal():
    persona = Person(
        name="X", phone_number="whatsapp:+1",
        sleep_start=time(13, 0), sleep_end=time(15, 0),
    )
    assert scheduler._en_horario_sueno(persona, time(14, 0)) is True
    assert scheduler._en_horario_sueno(persona, time(16, 0)) is False


def test_horario_de_sueno_cruza_medianoche():
    persona = Person(
        name="X", phone_number="whatsapp:+1",
        sleep_start=time(22, 0), sleep_end=time(6, 0),
    )
    assert scheduler._en_horario_sueno(persona, time(23, 30)) is True
    assert scheduler._en_horario_sueno(persona, time(3, 0)) is True
    assert scheduler._en_horario_sueno(persona, time(12, 0)) is False


# --- setup ---

def test_setup_lee_horarios_de_settings(monkeypatch, db_factory, db_session):
    db_session.add(Setting(key="morning_reminder_time", value="08:15"))
    db_session.add(Setting(key="night_reminder_time", value="20:45"))
    db_session.commit()
    monkeypatch.setattr(scheduler, "SessionLocal", db_factory)

    jobs = []

    class FakeScheduler:
        running = False

        def add_job(self, fn, trigger, **kwargs):
            jobs.append((kwargs["id"], str(trigger)))

        def start(self):
            self.running = True

    monkeypatch.setattr(scheduler, "scheduler", FakeScheduler())
    scheduler.setup()

    assert len(jobs) == 2
    assert "hour='8', minute='15'" in jobs[0][1]
    assert "hour='20', minute='45'" in jobs[1][1]


def test_setup_usa_defaults_sin_settings(monkeypatch, db_factory):
    monkeypatch.setattr(scheduler, "SessionLocal", db_factory)

    jobs = []

    class FakeScheduler:
        running = False

        def add_job(self, fn, trigger, **kwargs):
            jobs.append(str(trigger))

        def start(self):
            pass

    monkeypatch.setattr(scheduler, "scheduler", FakeScheduler())
    scheduler.setup()

    assert "hour='7', minute='30'" in jobs[0]
    assert "hour='21', minute='0'" in jobs[1]


def test_parse_hhmm():
    assert scheduler._parse_hhmm("07:30") == (7, 30)
    assert scheduler._parse_hhmm("21:05") == (21, 5)
