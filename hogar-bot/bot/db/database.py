from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from bot.db.models import Base

_DB_DIR = Path(__file__).parent.parent.parent / "data"
_DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{_DB_DIR / 'hogar.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Activa WAL mode y foreign keys en cada conexión nueva
@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependencia de FastAPI. Abre una sesión por request y la cierra al terminar."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
