from sqlalchemy import create_engine, inspect, text

from bot.db import database, migrations


def _crear_db_v1(tmp_path):
    """Crea una DB con el schema viejo de v1 (sin last_reminder_sent_at
    ni índices) y una tarea con next_due_at NULL."""
    engine = create_engine(f"sqlite:///{tmp_path / 'v1.db'}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE tasks ("
            "id INTEGER PRIMARY KEY, name VARCHAR(200), frequency_days INTEGER, "
            "current_assignee_id INTEGER, created_by_id INTEGER, "
            "next_due_at DATETIME, is_active BOOLEAN, "
            "created_at DATETIME, updated_at DATETIME)"
        ))
        conn.execute(text(
            "CREATE TABLE task_completions ("
            "id INTEGER PRIMARY KEY, task_id INTEGER, person_id INTEGER, "
            "completed_at DATETIME)"
        ))
        conn.execute(text(
            "INSERT INTO tasks (name, frequency_days, is_active, created_at, updated_at) "
            "VALUES ('Lavar platos', 3, 1, '2026-07-01 00:00:00', '2026-07-01 00:00:00')"
        ))
    return engine


def test_migracion_completa_sobre_db_v1(tmp_path, monkeypatch):
    engine = _crear_db_v1(tmp_path)
    monkeypatch.setattr(database, "engine", engine)

    migrations.run()

    inspector = inspect(engine)
    columnas = [c["name"] for c in inspector.get_columns("tasks")]
    assert "last_reminder_sent_at" in columnas

    indices = {i["name"] for i in inspector.get_indexes("tasks")}
    indices |= {i["name"] for i in inspector.get_indexes("task_completions")}
    assert "ix_tasks_next_due_at" in indices
    assert "ix_tasks_current_assignee_id" in indices
    assert "ix_task_completions_task_id" in indices
    assert "ix_task_completions_person_id" in indices
    assert "ix_task_completions_completed_at" in indices

    with engine.connect() as conn:
        vencimiento = conn.execute(
            text("SELECT next_due_at FROM tasks WHERE name = 'Lavar platos'")
        ).scalar()
    # Backfill: created_at (01/07) + 3 días de frecuencia
    assert vencimiento == "2026-07-04 00:00:00"


def test_migracion_es_idempotente(tmp_path, monkeypatch):
    engine = _crear_db_v1(tmp_path)
    monkeypatch.setattr(database, "engine", engine)

    migrations.run()
    migrations.run()  # segunda corrida no debe fallar ni duplicar nada

    columnas = [c["name"] for c in inspect(engine).get_columns("tasks")]
    assert columnas.count("last_reminder_sent_at") == 1
