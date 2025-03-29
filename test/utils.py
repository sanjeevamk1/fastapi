import pytest
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import Todos,Users
from ..router.auth import hashed
from ..main import app
from fastapi.testclient import TestClient

SQL_ALCHEMT_URL = "sqlite:///./testdb.db"

from sqlalchemy import create_engine,text
client =  TestClient(app)
engine =  create_engine(SQL_ALCHEMT_URL)
Test_session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_todos():
    todo = Todos(
    title="test the code",
    description = "Pytest working",
    priority = 3,
    completed = True,
    owner_id =10
    )
    db = Test_session()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username = "suhas123",
        email="suhas123@gmail.com",
        first_name = "suhas",
        last_name = "Garlapad",
        hashed_password = hashed.hash("SUhas@123"),
        role="Admin",
        phone_number = 87889789978
    )
    db = Test_session()
    db.add(user)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()

def override_get_db():
    db = Test_session()
    try:
        yield db
    finally:
        db.close()
def override_get_user():
    return {'username':'testsuhas','user_id':10,'role':'Admin'}

