from datetime import datetime, timedelta

from bot.core import dispatcher
from bot.db.models import Task


def _crear_tarea(db_session, jean, frequency_days=7, next_due_at=None):
    task = Task(
        name="Lavar platos",
        frequency_days=frequency_days,
        current_assignee_id=jean.id,
        created_by_id=jean.id,
        next_due_at=next_due_at,
    )
    db_session.add(task)
    db_session.commit()
    return task


def test_listo_completa_tarea_y_reasigna_al_siguiente(db_session, jean, anelys):
    task = _crear_tarea(db_session, jean)

    respuesta = dispatcher.handle("listo", jean, db_session)

    db_session.refresh(task)
    assert "Lavar platos" in respuesta
    assert "Anelys" in respuesta
    assert task.current_assignee_id == anelys.id
    assert task.next_due_at is not None


def test_listo_sin_tareas_pendientes(db_session, jean, anelys):
    respuesta = dispatcher.handle("listo", jean, db_session)

    assert "No tienes tareas pendientes" in respuesta


def test_listar_con_tareas(db_session, jean, anelys):
    # Mediodía UTC para que la fecha local (Panamá, UTC-5) sea el mismo día
    _crear_tarea(db_session, jean, next_due_at=datetime(2026, 8, 1, 12, 0))

    respuesta = dispatcher.handle("mis tareas", jean, db_session)

    assert "Lavar platos" in respuesta
    assert "01/08" in respuesta


def test_listar_sin_tareas(db_session, jean, anelys):
    respuesta = dispatcher.handle("mis tareas", jean, db_session)

    assert "No tienes tareas asignadas" in respuesta


def test_nueva_tarea_como_admin_crea_tarea(db_session, jean, anelys):
    respuesta = dispatcher.handle(
        "nueva tarea Sacar la basura, cada 3 dias", jean, db_session
    )

    task = db_session.query(Task).filter_by(name="Sacar la basura").first()
    assert task is not None
    assert task.frequency_days == 3
    assert "creada" in respuesta.lower()


def test_nueva_tarea_como_no_admin_rechazada(db_session, jean, anelys):
    respuesta = dispatcher.handle(
        "nueva tarea Sacar la basura, cada 3 dias", anelys, db_session
    )

    assert respuesta == "Solo Jean puede configurar tareas."
    assert db_session.query(Task).filter_by(name="Sacar la basura").first() is None


def test_mensaje_no_reconocido_muestra_ayuda(db_session, jean, anelys):
    respuesta = dispatcher.handle("hola bot", jean, db_session)

    assert "Comandos:" in respuesta


def test_round_robin_alterna_entre_dos_personas(db_session, jean, anelys):
    task = _crear_tarea(db_session, jean)

    dispatcher.handle("listo", jean, db_session)
    db_session.refresh(task)
    assert task.current_assignee_id == anelys.id

    dispatcher.handle("listo", anelys, db_session)
    db_session.refresh(task)
    assert task.current_assignee_id == jean.id


# --- casos nuevos v2 ---

def test_listo_completa_la_tarea_mas_urgente(db_session, jean, anelys):
    tarde = Task(
        name="Regar plantas", frequency_days=7,
        current_assignee_id=jean.id, created_by_id=jean.id,
        next_due_at=datetime(2026, 8, 1),
    )
    urgente = Task(
        name="Lavar platos", frequency_days=2,
        current_assignee_id=jean.id, created_by_id=jean.id,
        next_due_at=datetime(2026, 7, 1),
    )
    db_session.add_all([tarde, urgente])
    db_session.commit()

    respuesta = dispatcher.handle("listo", jean, db_session)

    assert "Lavar platos" in respuesta
    db_session.refresh(tarde)
    assert tarde.current_assignee_id == jean.id  # la otra no se toca


def test_listar_muestra_fecha_en_hora_local(db_session, jean, anelys):
    # 02:00 UTC del 2 de agosto = 21:00 del 1 de agosto en Panamá
    _crear_tarea(db_session, jean, next_due_at=datetime(2026, 8, 2, 2, 0))

    respuesta = dispatcher.handle("mis tareas", jean, db_session)

    assert "01/08" in respuesta
