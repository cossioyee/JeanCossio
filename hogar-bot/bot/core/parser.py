import re
from datetime import datetime

from sqlalchemy.orm import Session

from bot.db.models import Person, Task

_NUEVA_RE = re.compile(
    r"(?:nueva|agregar|a[ñn]adir|crear)\s+tarea\s+(.+?),?\s+cada\s+(\d+)\s+d[ií]as?",
    re.IGNORECASE,
)
_EDITAR_RE = re.compile(
    r"(?:editar|cambiar|modificar)\s+tarea\s+(.+?),?\s+cada\s+(\d+)\s+d[ií]as?",
    re.IGNORECASE,
)
_ELIMINAR_RE = re.compile(
    r"(?:eliminar|borrar|quitar)\s+tarea\s+(.+?)[\s.!?]*$",
    re.IGNORECASE,
)

_AYUDA_FORMATO = (
    "No entendí el formato. Usa:\n"
    "- *nueva tarea [nombre], cada [N] días*\n"
    "- *editar tarea [nombre], cada [N] días*\n"
    "- *eliminar tarea [nombre]*"
)


def parse_config(message: str, sender: Person, db: Session) -> str:
    m = _NUEVA_RE.search(message)
    if m:
        return _crear(m.group(1).strip(), int(m.group(2)), sender, db)

    m = _EDITAR_RE.search(message)
    if m:
        return _editar(m.group(1).strip(), int(m.group(2)), db)

    m = _ELIMINAR_RE.search(message)
    if m:
        return _eliminar(m.group(1).strip(), db)

    return _AYUDA_FORMATO


def _crear(name: str, frequency_days: int, sender: Person, db: Session) -> str:
    if db.query(Task).filter(Task.name.ilike(name), Task.is_active.is_(True)).first():
        return f"Ya existe una tarea activa llamada '{name}'."

    db.add(Task(
        name=name,
        frequency_days=frequency_days,
        current_assignee_id=sender.id,
        created_by_id=sender.id,
    ))
    db.commit()
    return f"Tarea '{name}' creada. Frecuencia: cada {frequency_days} días. Asignada a {sender.name}."


def _editar(name: str, frequency_days: int, db: Session) -> str:
    task = db.query(Task).filter(
        Task.name.ilike(f"%{name}%"), Task.is_active.is_(True)
    ).first()
    if task is None:
        return f"No encontré ninguna tarea activa con '{name}'."

    task.frequency_days = frequency_days
    task.updated_at = datetime.utcnow()
    db.commit()
    return f"Tarea '{task.name}' actualizada. Nueva frecuencia: cada {frequency_days} días."


def _eliminar(name: str, db: Session) -> str:
    task = db.query(Task).filter(
        Task.name.ilike(f"%{name}%"), Task.is_active.is_(True)
    ).first()
    if task is None:
        return f"No encontré ninguna tarea activa con '{name}'."

    task.is_active = False
    task.updated_at = datetime.utcnow()
    db.commit()
    return f"Tarea '{task.name}' eliminada."
