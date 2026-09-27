import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.adopter_profile import AdopterProfile


class AdopterProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
    ) -> AdopterProfile | None:
        statement = select(AdopterProfile).where(
            AdopterProfile.user_id == user_id
        )
        return self.session.execute(statement).scalar_one_or_none()
