import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.session import Session as UserSession
from backend.app.models.user import User
from backend.app.security.password import hash_password
from backend.app.security.session_token import hash_session_token


def create_user(
    db_session: Session,
    *,
    password: str = "correct-password",
) -> User:
    user = User(
        email=f"user-{uuid.uuid4()}@example.com",
        password_hash=hash_password(password),
        role=UserRole.ADOPTER,
        account_status=AccountStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_login_returns_401_for_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "missing@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_returns_user_and_sets_http_only_session_cookie(
    client,
    db_session: Session,
):
    user = create_user(db_session)

    user_email = user.email
    user_id = str(user.id)

    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "email": user_email,
            "password": "correct-password",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "id": user_id,
            "email": user_email,
            "role": "ADOPTER",
        }
    }

    assert "session" in response.cookies
    assert "csrf_token" in response.cookies
    assert "session" not in response.json()

    set_cookie_headers = response.headers.get_list("set-cookie")

    session_cookie = next(
        cookie for cookie in set_cookie_headers if cookie.startswith("session=")
    )
    csrf_cookie = next(
        cookie for cookie in set_cookie_headers if cookie.startswith("csrf_token=")
    )

    assert "HttpOnly" in session_cookie
    assert "Max-Age=86400" in session_cookie
    assert "Path=/" in session_cookie
    assert "SameSite=lax" in session_cookie

    assert "HttpOnly" not in csrf_cookie
    assert "Max-Age=86400" in csrf_cookie
    assert "Path=/" in csrf_cookie
    assert "SameSite=lax" in csrf_cookie


def create_session(
    db_session: Session,
    user: User,
    *,
    token: str = "valid-session-token",
    expires_at: datetime | None = None,
    revoked_at: datetime | None = None,
) -> str:
    if expires_at is None:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    user_session = UserSession(
        user_id=user.id,
        token_hash=hash_session_token(token),
        expires_at=expires_at,
        revoked_at=revoked_at,
    )

    db_session.add(user_session)
    db_session.commit()

    return token


def csrf_request_headers(token: str) -> dict[str, str]:
    return {"X-CSRF-Token": token}


def test_me_returns_401_without_session_cookie(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_me_returns_authenticated_user(client, db_session: Session):
    user = create_user(db_session)

    token = create_session(
        db_session,
        user,
    )

    response = client.get(
        "/api/auth/me",
        cookies={"session": token},
    )

    assert response.status_code == 200
    assert response.json() == {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": "ADOPTER",
        }
    }


def test_me_returns_401_for_invalid_session_cookie(client):
    response = client.get(
        "/api/auth/me",
        cookies={"session": "invalid-session-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_me_returns_401_for_revoked_session(
    client,
    db_session: Session,
):
    user = create_user(db_session)

    token = create_session(
        db_session,
        user,
        revoked_at=datetime.now(timezone.utc),
    )

    response = client.get(
        "/api/auth/me",
        cookies={"session": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_me_returns_401_for_expired_session(
    client,
    db_session: Session,
):
    user = create_user(db_session)

    token = create_session(
        db_session,
        user,
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    response = client.get(
        "/api/auth/me",
        cookies={"session": token},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_logout_revokes_session_and_clears_cookie(
    client,
    db_session: Session,
):
    user = create_user(db_session)

    token = create_session(
        db_session,
        user,
    )

    csrf_token = "valid-csrf-token"

    response = client.post(
        "/api/auth/logout",
        cookies={
            "session": token,
            "csrf_token": csrf_token,
        },
        headers=csrf_request_headers(csrf_token),
    )

    assert response.status_code == 204
    assert response.content == b""

    set_cookie_headers = response.headers.get_list("set-cookie")

    session_cookie = next(
        cookie for cookie in set_cookie_headers if cookie.startswith("session=")
    )
    csrf_cookie = next(
        cookie for cookie in set_cookie_headers if cookie.startswith("csrf_token=")
    )

    assert "Max-Age=0" in session_cookie
    assert "HttpOnly" in session_cookie
    assert "Path=/" in session_cookie
    assert "SameSite=lax" in session_cookie

    assert "Max-Age=0" in csrf_cookie
    assert "HttpOnly" not in csrf_cookie
    assert "Path=/" in csrf_cookie
    assert "SameSite=lax" in csrf_cookie

    db_session.expire_all()

    stored_session = db_session.scalar(
        select(UserSession).where(UserSession.user_id == user.id)
    )

    assert stored_session is not None
    assert stored_session.revoked_at is not None


def test_logout_returns_403_without_csrf_token(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}


def test_logout_is_idempotent_for_invalid_session_cookie(client):
    csrf_token = "valid-csrf-token"

    response = client.post(
        "/api/auth/logout",
        cookies={
            "session": "invalid-session-token",
            "csrf_token": csrf_token,
        },
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 204
    assert response.content == b""


def test_logout_is_idempotent_for_already_revoked_session(
    client,
    db_session: Session,
):
    user = create_user(db_session)

    token = create_session(
        db_session,
        user,
    )

    csrf_token = "valid-csrf-token"

    first_response = client.post(
        "/api/auth/logout",
        cookies={
            "session": token,
            "csrf_token": csrf_token,
        },
        headers={"X-CSRF-Token": csrf_token},
    )

    assert first_response.status_code == 204

    second_response = client.post(
        "/api/auth/logout",
        cookies={
            "session": token,
            "csrf_token": csrf_token,
        },
        headers={"X-CSRF-Token": csrf_token},
    )

    assert second_response.status_code == 204
    assert second_response.content == b""


def test_logout_returns_403_for_mismatched_csrf_token(client):
    response = client.post(
        "/api/auth/logout",
        cookies={"csrf_token": "cookie-token"},
        headers=csrf_request_headers("header-token"),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}


def test_logout_returns_403_for_missing_csrf_header(client):
    response = client.post(
        "/api/auth/logout",
        cookies={"csrf_token": "cookie-token"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "CSRF validation failed"}
