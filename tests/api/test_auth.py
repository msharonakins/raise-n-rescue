import uuid

from sqlalchemy.orm import Session

from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.user import User
from backend.app.security.password import hash_password


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
    assert "session" not in response.json()

    set_cookie = response.headers["set-cookie"]

    assert "HttpOnly" in set_cookie
    assert "Max-Age=86400" in set_cookie
    assert "Path=/" in set_cookie
    assert "SameSite=lax" in set_cookie
