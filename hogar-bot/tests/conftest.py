import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.db.models import Base, Person


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
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
