import os
from collections.abc import Generator

import pytest
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

    if revision != "0346aeed357c":
        engine.dispose()
        pytest.fail(
            "Test database is not at the expected Alembic head "
            f"(expected 0346aeed357c, found {revision})."
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
