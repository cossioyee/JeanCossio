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


# --- casos nuevos v2 ---

def test_crear_tarea_inicializa_next_due_at(db_session, jean):
    parser.parse_config("nueva tarea Barrer el patio, cada 5 dias", jean, db_session)

    task = db_session.query(Task).filter_by(name="Barrer el patio").first()
    assert task.next_due_at is not None


def test_crear_tarea_frecuencia_cero_rechazada(db_session, jean):
    respuesta = parser.parse_config("nueva tarea Regar plantas, cada 0 dias", jean, db_session)

    assert "al menos 1 día" in respuesta
    assert db_session.query(Task).count() == 0


def test_editar_con_match_parcial_ambiguo_pide_aclaracion(db_session, jean):
    parser.parse_config("nueva tarea Lavar platos, cada 2 dias", jean, db_session)
    parser.parse_config("nueva tarea Lavar el baño, cada 7 dias", jean, db_session)

    respuesta = parser.parse_config("editar tarea Lavar, cada 3 dias", jean, db_session)

    assert "varias tareas" in respuesta
    assert "Lavar platos" in respuesta
    assert "Lavar el baño" in respuesta
    # Ninguna de las dos debe haber cambiado
    frecuencias = {t.name: t.frequency_days for t in db_session.query(Task).all()}
    assert frecuencias == {"Lavar platos": 2, "Lavar el baño": 7}


def test_eliminar_con_match_exacto_ignora_parciales(db_session, jean):
    parser.parse_config("nueva tarea Lavar, cada 2 dias", jean, db_session)
    parser.parse_config("nueva tarea Lavar el baño, cada 7 dias", jean, db_session)

    respuesta = parser.parse_config("eliminar tarea Lavar", jean, db_session)

    assert "eliminada" in respuesta.lower()
    activas = [t.name for t in db_session.query(Task).filter_by(is_active=True).all()]
    assert activas == ["Lavar el baño"]
