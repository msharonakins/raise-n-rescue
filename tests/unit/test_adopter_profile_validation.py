from types import SimpleNamespace

import pytest

from backend.app.services.adopter_profile_validation import (
    is_adopter_profile_complete,
)


COMPLETE_PROFILE_VALUES = {
    "home_type": "HOUSE",
    "outdoor_space": "AVAILABLE",
    "activity_level": "MEDIUM",
    "children_in_household": False,
    "existing_dogs": False,
    "existing_cats": False,
    "experience_level": "SOME_EXPERIENCE",
    "time_available": "TWO_TO_FOUR_HOURS",
}


def create_profile(**overrides):
    values = COMPLETE_PROFILE_VALUES | overrides
    return SimpleNamespace(**values)


def test_adopter_profile_is_complete_when_all_required_fields_are_populated():
    profile = create_profile()

    assert is_adopter_profile_complete(profile)


@pytest.mark.parametrize(
    "field_name",
    [
        "home_type",
        "outdoor_space",
        "activity_level",
        "children_in_household",
        "existing_dogs",
        "existing_cats",
        "experience_level",
        "time_available",
    ],
)
def test_adopter_profile_is_incomplete_when_required_field_is_missing(
    field_name: str,
):
    profile = create_profile(**{field_name: None})

    assert not is_adopter_profile_complete(profile)


def test_adopter_profile_can_be_complete_without_preference_collections():
    profile = create_profile()

    assert is_adopter_profile_complete(profile)
