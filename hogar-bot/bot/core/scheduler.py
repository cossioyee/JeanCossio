from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from bot.db.database import SessionLocal
from bot.db.models import Person, Setting, Task
from bot.whatsapp import sender

scheduler = BackgroundScheduler(timezone="America/Panama")


def _send_reminders() -> None:
    db = SessionLocal()
    try:
        tasks = db.query(Task).filter(Task.is_active.is_(True)).all()
        if not tasks:
            return

        by_person: dict[int, list[Task]] = {}
        for t in tasks:
            by_person.setdefault(t.current_assignee_id, []).append(t)

        for person_id, person_tasks in by_person.items():
            person = db.get(Person, person_id)
            if person is None:
                continue
            names = ", ".join(t.name for t in person_tasks)
            sender.send(
                to=person.phone_number,
                body=f"Recordatorio: te toca {names}. Responde *listo* cuando termines.",
            )
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
