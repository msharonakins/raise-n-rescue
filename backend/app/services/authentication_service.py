from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.session import Session as UserSession
from backend.app.models.user import User
from backend.app.repositories.session_repository import SessionRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.security.email import normalize_email
from backend.app.security.password import hash_password, verify_password
from backend.app.security.session_token import (
    generate_session_token,
    hash_session_token,
)
from backend.app.services.authentication_errors import AuthenticationError
from backend.app.services.registration_errors import (
    EmailAlreadyRegisteredError,
)


_DUMMY_PASSWORD_HASH = hash_password("raise-n-rescue-dummy-password")


class AuthenticationResult:
    def __init__(self, user: User, session_token: str) -> None:
        self.user = user
        self.session_token = session_token


class AuthenticationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.session_repository = SessionRepository(session)


    def register_adopter(
        self,
        email: str,
        password: str,
    ) -> AuthenticationResult:
        canonical_email = normalize_email(email)

        try:
            with self.session.begin():
                existing_user = self.user_repository.get_by_email(
                    canonical_email
                )

                if existing_user is not None:
                    raise EmailAlreadyRegisteredError

                user = User(
                    email=canonical_email,
                    password_hash=hash_password(password),
                    role=UserRole.ADOPTER,
                    organisation_id=None,
                    account_status=AccountStatus.ACTIVE,
                )
                self.user_repository.add(user)
                self.session.flush()

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
        except IntegrityError as exc:
            original_error = exc.orig
            diagnostic = getattr(original_error, "diag", None)
            constraint_name = getattr(
                diagnostic,
                "constraint_name",
                None,
            )

            if constraint_name == "uq_users_email_canonical":
                raise EmailAlreadyRegisteredError from exc

            raise


    def authenticate(
        self,
        email: str,
        password: str,
    ) -> AuthenticationResult:
        with self.session.begin():
            user = self.user_repository.get_by_email(normalize_email(email))

            if user is None:
                verify_password(password, _DUMMY_PASSWORD_HASH)
                raise AuthenticationError

            if user.account_status != AccountStatus.ACTIVE:
                verify_password(password, _DUMMY_PASSWORD_HASH)
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


    def revoke_session(self, session_token: str) -> None:
        token_hash = hash_session_token(session_token)

        with self.session.begin():
            user_session = self.session_repository.get_by_token_hash(
                token_hash
            )

            if user_session is None:
                raise AuthenticationError

            if user_session.revoked_at is not None:
                raise AuthenticationError

            user_session.revoked_at = datetime.now(timezone.utc)
