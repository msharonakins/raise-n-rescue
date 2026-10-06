from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from backend.app.models.session import Session


class SessionRepository:
    def __init__(self, session: SQLAlchemySession) -> None:
        self.session = session

    def add(self, session: Session) -> Session:
        self.session.add(session)
        return session

    def get_by_token_hash(self, token_hash: str) -> Session | None:
        statement = select(Session).where(Session.token_hash == token_hash)
        return self.session.scalar(statement)

    def revoke(self, session: Session, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at

    def get_by_id(self, session_id: uuid.UUID) -> Session | None:
        statement = select(Session).where(Session.id == session_id)
        return self.session.scalar(statement)
