"""
Ejecutar una sola vez para poblar la DB con datos iniciales.
Uso: python -m bot.db.seed
Requiere JEAN_PHONE_NUMBER y ANELYS_PHONE_NUMBER en el entorno (.env).
"""
import os

from bot.db.database import SessionLocal, create_tables
from bot.db.models import Person, Setting


def _phone_number(env_var: str) -> str:
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {env_var} (revisa .env)")
    return value


PERSONS = [
    {
        "name": "Jean",
        "phone_number": _phone_number("JEAN_PHONE_NUMBER"),
        "is_admin": True,
    },
    {
        "name": "Anelys",
        "phone_number": _phone_number("ANELYS_PHONE_NUMBER"),
        "is_admin": False,
    },
]

SETTINGS = [
    {"key": "morning_reminder_time", "value": "07:30"},
    {"key": "night_reminder_time", "value": "21:00"},
]


def run() -> None:
    create_tables()

    with SessionLocal() as db:
        _seed_persons(db)
        _seed_settings(db)
        db.commit()
        print("Seed completado.")


def _seed_persons(db) -> None:
    for data in PERSONS:
        exists = db.query(Person).filter_by(phone_number=data["phone_number"]).first()
        if exists:
            print(f"  [skip] Persona ya existe: {data['name']}")
            continue
        db.add(Person(**data))
        print(f"  [ok]   Persona creada: {data['name']}")


def _seed_settings(db) -> None:
    for data in SETTINGS:
        exists = db.query(Setting).filter_by(key=data["key"]).first()
        if exists:
            print(f"  [skip] Setting ya existe: {data['key']}")
            continue
        db.add(Setting(**data))
        print(f"  [ok]   Setting creado: {data['key']} = {data['value']}")


if __name__ == "__main__":
    run()
