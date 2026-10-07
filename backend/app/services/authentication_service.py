from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.enums import AccountStatus
from backend.app.models.session import Session as UserSession
from backend.app.models.user import User
from backend.app.repositories.session_repository import SessionRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.security.password import verify_password
from backend.app.security.session_token import (
    generate_session_token,
    hash_session_token,
)
from backend.app.services.authentication_errors import AuthenticationError


class AuthenticationResult:
    def __init__(self, user: User, session_token: str) -> None:
        self.user = user
        self.session_token = session_token


class AuthenticationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.session_repository = SessionRepository(session)

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> AuthenticationResult:
        with self.session.begin():
            user = self.user_repository.get_by_email(email)

            if user is None:
                raise AuthenticationError

            if user.account_status != AccountStatus.ACTIVE:
                raise AuthenticationError

            if not verify_password(password, user.password_hash):
                raise AuthenticationError

            session_token = generate_session_token()
            token_hash = hash_session_token(session_token)
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=settings.session_lifetime_hours
            )

            user_session = UserSession(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )

            self.session_repository.add(user_session)

            return AuthenticationResult(
                user=user,
                session_token=session_token,
            )


    def resolve_user_from_session(self, session_token: str) -> User:
        token_hash = hash_session_token(session_token)

        with self.session.begin():
            user_session = self.session_repository.get_by_token_hash(
                token_hash
            )

            if user_session is None:
                raise AuthenticationError

            now = datetime.now(timezone.utc)

            if user_session.revoked_at is not None:
                raise AuthenticationError

            if user_session.expires_at <= now:
                raise AuthenticationError

            user = self.user_repository.get_by_id(user_session.user_id)

            if user is None:
                raise AuthenticationError

            if user.account_status != AccountStatus.ACTIVE:
                raise AuthenticationError

            return user
