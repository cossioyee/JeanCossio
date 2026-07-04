import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from bot.db.models import Base, Person


@pytest.fixture
def db_engine():
    # StaticPool: todas las sesiones comparten la misma conexión en memoria,
    # necesario para que el scheduler (que abre su propia sesión) vea los
    # datos creados por las fixtures
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_factory(db_engine):
    return sessionmaker(bind=db_engine)


@pytest.fixture
def db_session(db_factory):
    session = db_factory()
    yield session
    session.close()


@pytest.fixture
def jean(db_session):
    person = Person(name="Jean", phone_number="whatsapp:+50760000001", is_admin=True)
    db_session.add(person)
    db_session.commit()
    return person


@pytest.fixture
def anelys(db_session):
    person = Person(name="Anelys", phone_number="whatsapp:+50760000002", is_admin=False)
    db_session.add(person)
    db_session.commit()
    return person
