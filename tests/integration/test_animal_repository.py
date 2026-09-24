import uuid

from sqlalchemy.orm import Session

from backend.app.repositories.animal_repository import AnimalRepository
from tests.integration.test_database import create_adopter_and_animal


def test_get_by_id_returns_animal(db_session: Session):
    _, animal = create_adopter_and_animal(db_session)

    repository = AnimalRepository(db_session)

    result = repository.get_by_id(animal.id)

    assert result is not None
    assert result.id == animal.id
    assert result.name == animal.name
    assert result.status == animal.status


def test_get_by_id_returns_none_for_missing_animal(
    db_session: Session,
):
    repository = AnimalRepository(db_session)

    result = repository.get_by_id(uuid.uuid4())

    assert result is None
