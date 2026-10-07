import uuid

from sqlalchemy.orm import Session as SQLAlchemySession

from backend.app.core.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


def create_user(db_session: SQLAlchemySession) -> User:
    user = User(
        email=f"user-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.ADOPTER,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_get_by_email_returns_user(
    db_session: SQLAlchemySession,
):
    user = create_user(db_session)
    repository = UserRepository(db_session)

    result = repository.get_by_email(user.email)

    assert result is not None
    assert result.id == user.id


def test_get_by_email_returns_none_when_not_found(
    db_session: SQLAlchemySession,
):
    repository = UserRepository(db_session)

    result = repository.get_by_email("missing@example.com")

    assert result is None


def test_get_by_id_returns_user(
    db_session: SQLAlchemySession,
):
    user = create_user(db_session)
    repository = UserRepository(db_session)

    result = repository.get_by_id(user.id)

    assert result is not None
    assert result.id == user.id


def test_get_by_id_returns_none_when_not_found(
    db_session: SQLAlchemySession,
):
    repository = UserRepository(db_session)

    result = repository.get_by_id(uuid.uuid4())

    assert result is None
