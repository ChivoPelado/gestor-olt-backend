import os
from typing import Any
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include backend dir in sys.path so that we can import from db,main.py

from app.database import Base, get_db
from app.apis.base import api_router


def start_application():
    app = FastAPI()
    app.include_router(api_router)
    return app

POSTGRES_TEST_USER : str = os.getenv("POSTGRES_TEST_USER", "test_user")
POSTGRES_TEST_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD", "test123")
POSTGRES_TEST_SERVER : str = os.getenv("POSTGRES_TEST_SERVER","localhost")
POSTGRES_TEST_PORT : str = os.getenv("POSTGRES_TEST_PORT",5432) 
POSTGRES_TEST_DB : str = os.getenv("POSTGRES_TEST_DB","app_test_debug")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_TEST_USER}:{POSTGRES_TEST_PASSWORD}@{POSTGRES_TEST_SERVER}:{POSTGRES_TEST_PORT}/{POSTGRES_TEST_DB}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def app() -> Generator[FastAPI, Any, None]:
    """
    Crea una nueva base de datos para el propósito de pruebas
    """
    Base.metadata.create_all(engine)  # crea las tablas.
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine) # elimina las tablas al finalizar


@pytest.fixture(scope="module")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session  # para uso en pruebas.
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client_test(app: FastAPI, db_session: SessionTesting) -> Generator[TestClient, Any, None]:
    """
    Sobrescribe la dependencia titular de la app con la base de pruebas
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client