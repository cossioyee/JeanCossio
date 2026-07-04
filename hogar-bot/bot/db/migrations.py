"""
Migraciones manuales para SQLite.

create_all() solo crea tablas que no existen — nunca altera las que ya
están en la DB. Cada cambio de schema sobre una tabla existente vive aquí
como un paso idempotente: se puede ejecutar en cada arranque sin romper nada.
Se ejecuta desde el lifespan de main.py, después de create_tables().
"""
from loguru import logger
from sqlalchemy import inspect, text

from bot.db import database

# Mismos nombres que genera SQLAlchemy con index=True (ix_<tabla>_<columna>),
# para que la DB migrada quede idéntica a una creada desde cero
_INDICES = [
    "CREATE INDEX IF NOT EXISTS ix_tasks_current_assignee_id ON tasks (current_assignee_id)",
    "CREATE INDEX IF NOT EXISTS ix_tasks_next_due_at ON tasks (next_due_at)",
    "CREATE INDEX IF NOT EXISTS ix_task_completions_task_id ON task_completions (task_id)",
    "CREATE INDEX IF NOT EXISTS ix_task_completions_person_id ON task_completions (person_id)",
    "CREATE INDEX IF NOT EXISTS ix_task_completions_completed_at ON task_completions (completed_at)",
]


def run() -> None:
    with database.engine.begin() as conn:
        _agregar_columna_last_reminder(conn)
        _backfill_next_due_at(conn)
        _crear_indices(conn)
    logger.info("Migraciones aplicadas")


def _agregar_columna_last_reminder(conn) -> None:
    columnas = [c["name"] for c in inspect(conn).get_columns("tasks")]
    if "last_reminder_sent_at" not in columnas:
        conn.execute(text("ALTER TABLE tasks ADD COLUMN last_reminder_sent_at DATETIME"))
        logger.info("Migración: columna tasks.last_reminder_sent_at agregada")


def _backfill_next_due_at(conn) -> None:
    # Tareas creadas en v1 quedaban con next_due_at NULL; el scheduler de v2
    # filtra por esa columna, así que las rellenamos con created_at + frecuencia
    resultado = conn.execute(text(
        "UPDATE tasks "
        "SET next_due_at = datetime(created_at, '+' || frequency_days || ' days') "
        "WHERE next_due_at IS NULL AND is_active = 1"
    ))
    if resultado.rowcount:
        logger.info(f"Migración: next_due_at rellenado en {resultado.rowcount} tareas")


def _crear_indices(conn) -> None:
    for sql in _INDICES:
        conn.execute(text(sql))
