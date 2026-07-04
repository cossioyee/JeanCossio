from datetime import time, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from bot.core import tiempo
from bot.db.database import SessionLocal
from bot.db.models import Person, Setting, Task
from bot.whatsapp import sender

scheduler = BackgroundScheduler(timezone="America/Panama")

# Si el último recordatorio de una tarea fue hace menos de esto, no se
# reenvía — evita duplicados si el proceso se reinicia cerca de la hora cron
_VENTANA_ANTIDUPLICADO = timedelta(hours=4)


def _en_horario_sueno(person: Person, hora_local: time) -> bool:
    """True si la hora local cae dentro de la ventana de sueño de la persona."""
    if person.sleep_start is None or person.sleep_end is None:
        return False
    if person.sleep_start <= person.sleep_end:
        return person.sleep_start <= hora_local < person.sleep_end
    # Rango que cruza medianoche, ej. 22:00 → 06:00
    return hora_local >= person.sleep_start or hora_local < person.sleep_end


def _send_reminders() -> None:
    db = SessionLocal()
    try:
        ahora = tiempo.ahora_utc()

        # Solo tareas vencidas: recordar "lavar platos" 7 días antes de que
        # toque solo genera ruido (bug corregido en v2)
        tasks = (
            db.query(Task)
            .filter(
                Task.is_active.is_(True),
                Task.current_assignee_id.isnot(None),
                Task.next_due_at.isnot(None),
                Task.next_due_at <= ahora,
            )
            .all()
        )

        by_person: dict[int, list[Task]] = {}
        for t in tasks:
            if t.last_reminder_sent_at and ahora - t.last_reminder_sent_at < _VENTANA_ANTIDUPLICADO:
                continue
            by_person.setdefault(t.current_assignee_id, []).append(t)

        hora_local = tiempo.a_hora_local(ahora).time()
        for person_id, person_tasks in by_person.items():
            person = db.get(Person, person_id)
            if person is None:
                continue
            if _en_horario_sueno(person, hora_local):
                logger.info(f"Recordatorio omitido: {person.name} está en horario de sueño")
                continue

            names = ", ".join(t.name for t in person_tasks)
            sender.send(
                to=person.phone_number,
                body=f"Recordatorio: te toca {names}. Responde *listo* cuando termines.",
            )
            for t in person_tasks:
                t.last_reminder_sent_at = ahora
        db.commit()
    except Exception:
        logger.exception("Error al enviar recordatorios")
    finally:
        db.close()


def _parse_hhmm(value: str) -> tuple[int, int]:
    h, m = value.split(":")
    return int(h), int(m)


def setup() -> None:
    db = SessionLocal()
    try:
        morning = db.query(Setting).filter_by(key="morning_reminder_time").first()
        night = db.query(Setting).filter_by(key="night_reminder_time").first()
        m_h, m_m = _parse_hhmm(morning.value if morning else "07:30")
        n_h, n_m = _parse_hhmm(night.value if night else "21:00")
    finally:
        db.close()

    scheduler.add_job(
        _send_reminders,
        CronTrigger(hour=m_h, minute=m_m),
        id="morning_reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        _send_reminders,
        CronTrigger(hour=n_h, minute=n_m),
        id="night_reminder",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler iniciado — mañana {m_h:02d}:{m_m:02d}, noche {n_h:02d}:{n_m:02d}")


def shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown()
