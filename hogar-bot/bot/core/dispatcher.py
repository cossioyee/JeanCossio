import re
from datetime import timedelta

from sqlalchemy.orm import Session

from bot.core import tiempo
from bot.db.models import Person, Task, TaskCompletion

_LISTO = re.compile(r"^(listo|hecho|ya|termin[eé]|done)[\s!.]*$", re.IGNORECASE)
_LISTAR = re.compile(r"(mis tareas|qu[eé] me toca|pendientes|tareas)", re.IGNORECASE)
_NUEVA = re.compile(r"(nueva tarea|agregar tarea|a[ñn]adir tarea|crear tarea)", re.IGNORECASE)
_EDITAR = re.compile(r"(editar tarea|cambiar tarea|modificar tarea)", re.IGNORECASE)
_ELIMINAR = re.compile(r"(eliminar tarea|borrar tarea|quitar tarea)", re.IGNORECASE)


def handle(message: str, sender: Person, db: Session) -> str:
    msg = message.strip()

    if _LISTO.match(msg):
        return _completar(sender, db)

    if _LISTAR.search(msg):
        return _listar(sender, db)

    if _NUEVA.search(msg) or _EDITAR.search(msg) or _ELIMINAR.search(msg):
        if not sender.is_admin:
            return "Solo Jean puede configurar tareas."
        from bot.core import parser
        return parser.parse_config(message=msg, sender=sender, db=db)

    return _ayuda()


# --- handlers internos ---

def _completar(sender: Person, db: Session) -> str:
    task = (
        db.query(Task)
        .filter(Task.current_assignee_id == sender.id, Task.is_active.is_(True))
        .order_by(Task.next_due_at.asc().nullsfirst())
        .first()
    )
    if task is None:
        return "No tienes tareas pendientes. Buen trabajo!"

    ahora = tiempo.ahora_utc()
    db.add(TaskCompletion(
        task_id=task.id,
        person_id=sender.id,
        completed_at=ahora,
    ))

    next_person = _next_assignee(task.current_assignee_id, db)
    task.current_assignee_id = next_person.id
    task.next_due_at = ahora + timedelta(days=task.frequency_days)
    task.updated_at = ahora
    db.commit()

    return f"Perfecto! '{task.name}' lista. Ahora le toca a {next_person.name}."


def _listar(sender: Person, db: Session) -> str:
    tasks = (
        db.query(Task)
        .filter(Task.current_assignee_id == sender.id, Task.is_active.is_(True))
        .order_by(Task.next_due_at.asc().nullsfirst())
        .all()
    )
    if not tasks:
        return "No tienes tareas asignadas por ahora."

    lines = ["Tus tareas:"]
    for t in tasks:
        # La fecha se muestra en hora de Panamá; en UTC podría verse
        # corrida un día cerca de la medianoche
        if t.next_due_at:
            due = f"vence {tiempo.a_hora_local(t.next_due_at).strftime('%d/%m')}"
        else:
            due = "sin fecha"
        lines.append(f"- {t.name} ({due})")
    return "\n".join(lines)


def _next_assignee(current_id: int, db: Session) -> Person:
    """Round-robin: devuelve la siguiente persona en orden de ID."""
    persons = db.query(Person).order_by(Person.id).all()
    idx = next((i for i, p in enumerate(persons) if p.id == current_id), 0)
    return persons[(idx + 1) % len(persons)]


def _ayuda() -> str:
    return (
        "Comandos:\n"
        "- *listo* → marcar tu tarea actual como completada\n"
        "- *mis tareas* → ver qué te toca\n"
        "- *nueva tarea [nombre], cada [N] días* → agregar (solo Jean)\n"
        "- *editar tarea [nombre]* → editar (solo Jean)\n"
        "- *eliminar tarea [nombre]* → eliminar (solo Jean)"
    )
