import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.session import Session as UserSession
from backend.app.models.user import User
from backend.app.services.authentication_errors import AuthenticationError
from backend.app.services.authentication_service import AuthenticationService
from backend.app.security.password import hash_password
from backend.app.security.session_token import hash_session_token


def create_user(
    db_session: Session,
    *,
    password: str = "correct-password",
    account_status: AccountStatus = AccountStatus.ACTIVE,
) -> User:
    user = User(
        email=f"user-{uuid.uuid4()}@example.com",
        password_hash=hash_password(password),
        role=UserRole.ADOPTER,
        account_status=account_status,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_authenticate_creates_session_and_returns_raw_token(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    assert result.user.id == user.id
    assert result.session_token

    stored_session = service_session.scalar(
        select(UserSession).where(UserSession.user_id == user.id)
    )

    assert stored_session is not None
    assert stored_session.user_id == user.id
    assert stored_session.token_hash == hash_session_token(
        result.session_token
    )
    assert stored_session.revoked_at is None

    now = datetime.now(timezone.utc)
    expected_expiry = now + timedelta(hours=24)

    assert expected_expiry - timedelta(seconds=5) <= stored_session.expires_at
    assert stored_session.expires_at <= expected_expiry + timedelta(seconds=5)


def test_authenticate_raises_for_unknown_email(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = AuthenticationService(service_session)

    with pytest.raises(AuthenticationError):
        service.authenticate(
            email="missing@example.com",
            password="correct-password",
        )

    assert service_session.scalars(select(UserSession)).all() == []


def test_authenticate_raises_for_incorrect_password(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    with pytest.raises(AuthenticationError):
        service.authenticate(
            email=user.email,
            password="wrong-password",
        )

    assert service_session.scalars(select(UserSession)).all() == []


def test_authenticate_raises_for_inactive_user(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(
        setup_session,
        account_status=AccountStatus.INACTIVE,
    )

    service = AuthenticationService(service_session)

    with pytest.raises(AuthenticationError):
        service.authenticate(
            email=user.email,
            password="correct-password",
        )

    assert service_session.scalars(select(UserSession)).all() == []


def test_resolve_user_from_session_token_returns_user(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    resolved_user = service.resolve_user_from_session(
        authentication_result.session_token
    )

    assert resolved_user.id == user.id


def test_resolve_user_from_session_token_raises_for_unknown_token(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = AuthenticationService(service_session)

    with pytest.raises(AuthenticationError):
        service.resolve_user_from_session("unknown-session-token")


def test_resolve_user_from_session_token_raises_for_expired_session(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    stored_session = service_session.scalar(
        select(UserSession).where(UserSession.user_id == user.id)
    )
    assert stored_session is not None

    stored_session.expires_at = datetime.now(timezone.utc) - timedelta(
        seconds=1
    )
    service_session.commit()

    with pytest.raises(AuthenticationError):
        service.resolve_user_from_session(
            authentication_result.session_token
        )


def test_resolve_user_from_session_token_raises_for_revoked_session(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    stored_session = service_session.scalar(
        select(UserSession).where(UserSession.user_id == user.id)
    )
    assert stored_session is not None

    stored_session.revoked_at = datetime.now(timezone.utc)
    service_session.commit()

    with pytest.raises(AuthenticationError):
        service.resolve_user_from_session(
            authentication_result.session_token
        )
