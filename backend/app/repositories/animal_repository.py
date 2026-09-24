import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.animal import Animal


class AnimalRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, animal_id: uuid.UUID) -> Animal | None:
        statement = select(Animal).where(Animal.id == animal_id)
        return self.session.execute(statement).scalar_one_or_none()
