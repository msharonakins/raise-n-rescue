import uuid

from sqlalchemy.orm import Session

from backend.app.repositories.adopter_profile_repository import (
    AdopterProfileRepository,
)
from tests.integration.test_database import create_adopter_and_animal


def test_get_by_user_id_returns_adopter_profile(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    repository = AdopterProfileRepository(db_session)

    result = repository.get_by_user_id(adopter_profile.user_id)

    assert result is not None
    assert result.id == adopter_profile.id
    assert result.user_id == adopter_profile.user_id


def test_get_by_user_id_returns_none_for_missing_profile(
    db_session: Session,
):
    repository = AdopterProfileRepository(db_session)

    result = repository.get_by_user_id(uuid.uuid4())

    assert result is None
