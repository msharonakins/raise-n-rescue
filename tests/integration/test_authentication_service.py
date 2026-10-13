import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.session import Session as UserSession
from backend.app.models.user import User
from backend.app.services.authentication_errors import AuthenticationError
from backend.app.services.authentication_service import (
    AuthenticationService,
    _DUMMY_PASSWORD_HASH,
)
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


def test_authenticate_normalizes_email_before_lookup(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)
    service = AuthenticationService(service_session)

    result = service.authenticate(
        email=f"  {user.email.upper()}  ",
        password="correct-password",
    )

    assert result.user.id == user.id
    assert result.session_token


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


def test_authenticate_verifies_dummy_hash_for_unknown_email(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = AuthenticationService(service_session)

    with patch(
        "backend.app.services.authentication_service.verify_password",
        return_value=False,
    ) as verify_mock:
        with pytest.raises(AuthenticationError):
            service.authenticate(
                email="missing@example.com",
                password="correct-password",
            )

    verify_mock.assert_called_once()
    assert verify_mock.call_args.args[1] == _DUMMY_PASSWORD_HASH
    assert verify_mock.call_args.args[0] == "correct-password"
    assert service_session.scalars(select(UserSession)).all() == []


def test_authenticate_verifies_dummy_hash_for_inactive_user(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(
        setup_session,
        account_status=AccountStatus.INACTIVE,
    )

    service = AuthenticationService(service_session)

    with patch(
        "backend.app.services.authentication_service.verify_password",
        return_value=False,
    ) as verify_mock:
        with pytest.raises(AuthenticationError):
            service.authenticate(
                email=user.email,
                password="correct-password",
            )

    verify_mock.assert_called_once()
    assert verify_mock.call_args.args[1] == _DUMMY_PASSWORD_HASH
    assert verify_mock.call_args.args[0] == "correct-password"
    assert service_session.scalars(select(UserSession)).all() == []


def test_authenticate_verifies_password_for_active_user_with_wrong_password(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)
    service = AuthenticationService(service_session)

    with patch(
        "backend.app.services.authentication_service.verify_password",
        return_value=False,
    ) as verify_mock:
        with pytest.raises(AuthenticationError):
            service.authenticate(
                email=user.email,
                password="wrong-password",
            )

    verify_mock.assert_called_once()
    assert verify_mock.call_args.args[0] == "wrong-password"
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


def test_resolve_user_from_session_token_raises_for_inactive_user(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)
    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    user.account_status = AccountStatus.INACTIVE
    setup_session.commit()

    with pytest.raises(AuthenticationError):
        service.resolve_user_from_session(
            authentication_result.session_token
        )


def test_revoke_session_marks_session_as_revoked(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    service.revoke_session(authentication_result.session_token)

    stored_session = service_session.scalar(
        select(UserSession).where(UserSession.user_id == user.id)
    )

    assert stored_session is not None
    assert stored_session.revoked_at is not None

    service_session.commit()

    with pytest.raises(AuthenticationError):
        service.resolve_user_from_session(
            authentication_result.session_token
        )


def test_revoke_session_raises_for_unknown_token(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = AuthenticationService(service_session)

    with pytest.raises(AuthenticationError):
        service.revoke_session("unknown-session-token")


def test_revoke_session_raises_for_already_revoked_session(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    user = create_user(setup_session)

    service = AuthenticationService(service_session)

    authentication_result = service.authenticate(
        email=user.email,
        password="correct-password",
    )

    service.revoke_session(authentication_result.session_token)

    with pytest.raises(AuthenticationError):
        service.revoke_session(authentication_result.session_token)


def test_register_adopter_creates_user_and_session(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions
    service = AuthenticationService(service_session)

    result = service.register_adopter(
        email="  New.Adopter@Example.com ",
        password="correct-horse-battery",
    )

    assert result.user.email == "new.adopter@example.com"
    assert result.user.role == UserRole.ADOPTER
    assert result.user.organisation_id is None
    assert result.user.account_status == AccountStatus.ACTIVE
    assert result.user.password_hash != "correct-horse-battery"

    assert result.session_token

    stored_session = service_session.scalar(
        select(UserSession).where(
            UserSession.user_id == result.user.id
        )
    )

    assert stored_session is not None
    assert stored_session.token_hash == hash_session_token(
        result.session_token
    )
    assert stored_session.revoked_at is None


def test_register_adopter_rejects_duplicate_canonical_email(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    existing_user = create_user(setup_session)
    service = AuthenticationService(service_session)

    from backend.app.services.registration_errors import (
        EmailAlreadyRegisteredError,
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        service.register_adopter(
            email=f"  {existing_user.email.upper()} ",
            password="correct-horse-battery",
        )

    assert service_session.scalars(select(UserSession)).all() == []


def test_register_adopter_rolls_back_user_if_session_creation_fails(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions
    service = AuthenticationService(service_session)

    with patch.object(
        service.session_repository,
        "add",
        side_effect=RuntimeError("Simulated session persistence failure"),
    ):
        with pytest.raises(
            RuntimeError,
            match="Simulated session persistence failure",
        ):
            service.register_adopter(
                email="rollback@example.com",
                password="correct-horse-battery",
            )

    user = service_session.scalar(
        select(User).where(User.email == "rollback@example.com")
    )
    assert user is None
