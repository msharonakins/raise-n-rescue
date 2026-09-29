import uuid

from sqlalchemy.orm import Session

from backend.app.core.enums import ChildAgeGroup, Size, Species
from backend.app.models.adopter_child_age_group import AdopterChildAgeGroup
from backend.app.models.adopter_preferred_size import AdopterPreferredSize
from backend.app.models.adopter_preferred_species import AdopterPreferredSpecies
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


def test_get_preferred_species_returns_profile_preferences(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    db_session.add_all(
        [
            AdopterPreferredSpecies(
                adopter_profile_id=adopter_profile.id,
                species=Species.DOG,
            ),
            AdopterPreferredSpecies(
                adopter_profile_id=adopter_profile.id,
                species=Species.CAT,
            ),
        ]
    )
    db_session.flush()

    repository = AdopterProfileRepository(db_session)

    result = repository.get_preferred_species(adopter_profile.id)

    assert {preference.species for preference in result} == {
        Species.DOG,
        Species.CAT,
    }


def test_get_preferred_species_returns_empty_list_when_no_preferences_exist(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    repository = AdopterProfileRepository(db_session)

    result = repository.get_preferred_species(adopter_profile.id)

    assert result == []


def test_get_preferred_sizes_returns_profile_preferences(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    db_session.add_all(
        [
            AdopterPreferredSize(
                adopter_profile_id=adopter_profile.id,
                size=Size.SMALL,
            ),
            AdopterPreferredSize(
                adopter_profile_id=adopter_profile.id,
                size=Size.MEDIUM,
            ),
        ]
    )
    db_session.flush()

    repository = AdopterProfileRepository(db_session)

    result = repository.get_preferred_sizes(adopter_profile.id)

    assert {preference.size for preference in result} == {
        Size.SMALL,
        Size.MEDIUM,
    }


def test_get_preferred_sizes_returns_empty_list_when_no_preferences_exist(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    repository = AdopterProfileRepository(db_session)

    result = repository.get_preferred_sizes(adopter_profile.id)

    assert result == []


def test_get_child_age_groups_returns_profile_preferences(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    db_session.add_all(
        [
            AdopterChildAgeGroup(
                adopter_profile_id=adopter_profile.id,
                child_age_group=ChildAgeGroup.YOUNG_CHILDREN,
            ),
            AdopterChildAgeGroup(
                adopter_profile_id=adopter_profile.id,
                child_age_group=ChildAgeGroup.TEENAGERS,
            ),
        ]
    )
    db_session.flush()

    repository = AdopterProfileRepository(db_session)

    result = repository.get_child_age_groups(adopter_profile.id)

    assert {preference.child_age_group for preference in result} == {
        ChildAgeGroup.YOUNG_CHILDREN,
        ChildAgeGroup.TEENAGERS,
    }


def test_get_child_age_groups_returns_empty_list_when_no_preferences_exist(
    db_session: Session,
):
    adopter_profile, _ = create_adopter_and_animal(db_session)

    repository = AdopterProfileRepository(db_session)

    result = repository.get_child_age_groups(adopter_profile.id)

    assert result == []
