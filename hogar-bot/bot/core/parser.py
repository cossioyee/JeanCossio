import re
from datetime import timedelta

from sqlalchemy.orm import Session

from bot.core import tiempo
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
    if frequency_days < 1:
        return "La frecuencia debe ser de al menos 1 día."

    if db.query(Task).filter(Task.name.ilike(name), Task.is_active.is_(True)).first():
        return f"Ya existe una tarea activa llamada '{name}'."

    db.add(Task(
        name=name,
        frequency_days=frequency_days,
        current_assignee_id=sender.id,
        created_by_id=sender.id,
        # Vence por primera vez a los N días de creada; sin esto el
        # scheduler (que filtra por next_due_at) nunca la recordaría
        next_due_at=tiempo.ahora_utc() + timedelta(days=frequency_days),
    ))
    db.commit()
    return f"Tarea '{name}' creada. Frecuencia: cada {frequency_days} días. Asignada a {sender.name}."


def _buscar_tarea(name: str, db: Session) -> tuple[Task | None, str | None]:
    """Busca una tarea activa por nombre. Devuelve (tarea, None) si hay un
    match claro, o (None, mensaje de error) si no hay o hay varios."""
    exacta = db.query(Task).filter(
        Task.name.ilike(name), Task.is_active.is_(True)
    ).first()
    if exacta:
        return exacta, None

    parciales = db.query(Task).filter(
        Task.name.ilike(f"%{name}%"), Task.is_active.is_(True)
    ).all()
    if not parciales:
        return None, f"No encontré ninguna tarea activa con '{name}'."
    if len(parciales) > 1:
        opciones = "\n".join(f"- {t.name}" for t in parciales)
        return None, (
            f"Hay varias tareas que coinciden con '{name}':\n{opciones}\n"
            "Escribe el nombre completo para que no me equivoque."
        )
    return parciales[0], None


def _editar(name: str, frequency_days: int, db: Session) -> str:
    if frequency_days < 1:
        return "La frecuencia debe ser de al menos 1 día."

    task, error = _buscar_tarea(name, db)
    if task is None:
        return error

    task.frequency_days = frequency_days
    task.updated_at = tiempo.ahora_utc()
    db.commit()
    return f"Tarea '{task.name}' actualizada. Nueva frecuencia: cada {frequency_days} días."


def _eliminar(name: str, db: Session) -> str:
    task, error = _buscar_tarea(name, db)
    if task is None:
        return error

    task.is_active = False
    task.updated_at = tiempo.ahora_utc()
    db.commit()
    return f"Tarea '{task.name}' eliminada."
