import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session as SQLAlchemySession

from backend.app.core.enums import UserRole
from backend.app.models.session import Session
from backend.app.models.user import User
from backend.app.repositories.session_repository import SessionRepository


def create_user(db_session: SQLAlchemySession) -> User:
    user = User(
        email=f"session-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.ADOPTER,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_add_and_get_session_by_token_hash(
    db_session: SQLAlchemySession,
):
    user = create_user(db_session)

    session = Session(
        user_id=user.id,
        token_hash="a" * 64,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    repository = SessionRepository(db_session)
    repository.add(session)
    db_session.flush()

    result = repository.get_by_token_hash("a" * 64)

    assert result is not None
    assert result.id == session.id
    assert result.user_id == user.id


def test_get_by_token_hash_returns_none_when_not_found(
    db_session: SQLAlchemySession,
):
    repository = SessionRepository(db_session)

    result = repository.get_by_token_hash("b" * 64)

    assert result is None


def test_get_by_id_returns_session(
    db_session: SQLAlchemySession,
):
    user = create_user(db_session)

    session = Session(
        user_id=user.id,
        token_hash="c" * 64,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    repository = SessionRepository(db_session)
    repository.add(session)
    db_session.flush()

    result = repository.get_by_id(session.id)

    assert result is not None
    assert result.id == session.id


def test_get_by_id_returns_none_when_not_found(
    db_session: SQLAlchemySession,
):
    repository = SessionRepository(db_session)

    result = repository.get_by_id(uuid.uuid4())

    assert result is None


def test_revoke_updates_revoked_at(
    db_session: SQLAlchemySession,
):
    user = create_user(db_session)

    session = Session(
        user_id=user.id,
        token_hash="d" * 64,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    repository = SessionRepository(db_session)
    repository.add(session)
    db_session.flush()

    revoked_at = datetime.now(timezone.utc)
    repository.revoke(session, revoked_at)

    assert session.revoked_at == revoked_at
