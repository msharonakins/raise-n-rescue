import os
import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient

from backend.app.api.dependencies import get_db
from backend.app.main import app
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.getenv("ALEMBIC_TEST_DATABASE_URL")

    if not database_url:
        pytest.fail(
            "ALEMBIC_TEST_DATABASE_URL must be set before running database tests."
        )

    return database_url


@pytest.fixture(scope="session")
def test_engine(test_database_url: str) -> Generator[Engine, None, None]:
    engine = create_engine(test_database_url)

    with engine.connect() as connection:
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

    if revision != "72438f37f02d":
        engine.dispose()
        pytest.fail(
            "Test database is not at the expected Alembic head "
            f"(expected 72438f37f02d, found {revision})."
        )

    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def service_sessions(
    test_engine: Engine,
) -> Generator[tuple[Session, Session], None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    setup_session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    service_session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield setup_session, service_session
    finally:
        service_session.close()
        setup_session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
