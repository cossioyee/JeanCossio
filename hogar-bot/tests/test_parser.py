from bot.core import parser
from bot.db.models import Task


def test_crear_tarea_nueva(db_session, jean):
    respuesta = parser.parse_config(
        "nueva tarea Barrer el patio, cada 5 dias", jean, db_session
    )

    task = db_session.query(Task).filter_by(name="Barrer el patio").first()
    assert task is not None
    assert task.frequency_days == 5
    assert task.current_assignee_id == jean.id
    assert task.created_by_id == jean.id
    assert "creada" in respuesta.lower()


def test_crear_tarea_duplicada_rechazada(db_session, jean):
    parser.parse_config("nueva tarea Barrer el patio, cada 5 dias", jean, db_session)

    respuesta = parser.parse_config(
        "nueva tarea Barrer el patio, cada 3 dias", jean, db_session
    )

    assert "Ya existe una tarea activa" in respuesta
    tareas = db_session.query(Task).filter_by(name="Barrer el patio").all()
    assert len(tareas) == 1


def test_editar_tarea_existente_actualiza_frecuencia(db_session, jean):
    parser.parse_config("nueva tarea Barrer el patio, cada 5 dias", jean, db_session)

    respuesta = parser.parse_config(
        "editar tarea Barrer el patio, cada 10 dias", jean, db_session
    )

    task = db_session.query(Task).filter_by(name="Barrer el patio").first()
    assert task.frequency_days == 10
    assert "actualizada" in respuesta.lower()


def test_editar_tarea_inexistente(db_session, jean):
    respuesta = parser.parse_config(
        "editar tarea Tarea Fantasma, cada 10 dias", jean, db_session
    )

    assert "No encontré ninguna tarea activa" in respuesta


def test_eliminar_tarea_existente_hace_soft_delete(db_session, jean):
    parser.parse_config("nueva tarea Barrer el patio, cada 5 dias", jean, db_session)

    respuesta = parser.parse_config("eliminar tarea Barrer el patio", jean, db_session)

    task = db_session.query(Task).filter_by(name="Barrer el patio").first()
    assert task.is_active is False
    assert "eliminada" in respuesta.lower()


def test_eliminar_tarea_inexistente(db_session, jean):
    respuesta = parser.parse_config("eliminar tarea Tarea Fantasma", jean, db_session)

    assert "No encontré ninguna tarea activa" in respuesta


def test_formato_no_reconocido_devuelve_ayuda(db_session, jean):
    respuesta = parser.parse_config("tarea rara sin formato", jean, db_session)

    assert "No entendí el formato" in respuesta
