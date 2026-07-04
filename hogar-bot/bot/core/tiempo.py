"""
Helpers de fecha/hora para todo el proyecto.

Regla única: en la DB todo se guarda en UTC naive (sin tzinfo). Para
mostrar fechas al usuario o comparar contra horarios locales (sueño,
recordatorios) se convierte a America/Panama con estos helpers.
Reemplaza a datetime.utcnow(), deprecado desde Python 3.12.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

ZONA_LOCAL = ZoneInfo("America/Panama")


def ahora_utc() -> datetime:
    """Hora actual en UTC naive — el formato que se guarda en la DB."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def a_hora_local(dt_utc: datetime) -> datetime:
    """Convierte un datetime UTC naive de la DB a hora local de Panamá."""
    return dt_utc.replace(tzinfo=timezone.utc).astimezone(ZONA_LOCAL)


def ahora_local() -> datetime:
    """Hora actual en Panamá (timezone-aware)."""
    return datetime.now(ZONA_LOCAL)
