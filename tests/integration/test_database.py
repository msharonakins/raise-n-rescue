import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.enums import (
    ActivityLevel,
    AgeUnit,
    AnimalStatus,
    ApplicationStatus,
    Compatibility,
    EnergyLevel,
    ExperienceLevel,
    ExperienceRequirement,
    HomeType,
    OutdoorSpace,
    OutdoorSpaceRequirement,
    Sex,
    Size,
    Species,
    SuitableHomeType,
    TimeAvailable,
    UserRole,
)
from backend.app.models.adopter_profile import AdopterProfile
from backend.app.models.animal import Animal
from backend.app.models.application import Application
from backend.app.models.facility import Facility
from backend.app.models.favourite import Favourite
from backend.app.models.organisation import RescueOrganisation
from backend.app.models.user import User


def test_database_is_at_expected_migration_head(db_session: Session):
    revision = db_session.execute(
        text("SELECT version_num FROM alembic_version")
    ).scalar_one()

    assert revision == "0346aeed357c"


def test_database_has_required_constraints_and_indexes(
    db_session: Session,
):
    indexes = {
        row[0]
        for row in db_session.execute(
            text(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                """
            )
        ).all()
    }

    constraints = {
        row[0]
        for row in db_session.execute(
            text(
                """
                SELECT conname
                FROM pg_constraint
                WHERE connamespace = 'public'::regnamespace
                """
            )
        ).all()
    }

    assert "uq_applications_one_active_per_adopter_animal" in indexes
    assert "uq_animal_photos_one_primary" in indexes
    assert "ck_users_role_organisation" in constraints
    assert "ck_animals_age_value_non_negative" in constraints


def test_database_rejects_adopter_with_organisation(
    db_session: Session,
):
    organisation = RescueOrganisation(
        name="Test Rescue",
        contact_email="test@example.com",
        contact_phone="0000000000",
        address="Test Address",
    )
    db_session.add(organisation)
    db_session.flush()

    user = User(
        email=f"adopter-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.ADOPTER,
        organisation_id=organisation.id,
    )
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_rescue_staff_without_organisation(
    db_session: Session,
):
    user = User(
        email=f"rescue-staff-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.RESCUE_STAFF,
        organisation_id=None,
    )
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_negative_animal_age(
    db_session: Session,
):
    organisation = RescueOrganisation(
        name="Test Rescue",
        contact_email="test@example.com",
        contact_phone="0000000000",
        address="Test Address",
    )
    db_session.add(organisation)
    db_session.flush()

    facility = Facility(
        organisation_id=organisation.id,
        name="Test Facility",
        address="Test Address",
        contact_phone="0000000000",
    )
    db_session.add(facility)
    db_session.flush()

    animal = Animal(
        name="Test Animal",
        species=Species.DOG,
        age_value=-1,
        age_unit=AgeUnit.YEARS,
        sex=Sex.MALE,
        size=Size.MEDIUM,
        facility_id=facility.id,
        energy_level=EnergyLevel.MEDIUM,
        children_compatibility=Compatibility.COMPATIBLE,
        dog_compatibility=Compatibility.COMPATIBLE,
        cat_compatibility=Compatibility.COMPATIBLE,
        suitable_home_type=SuitableHomeType.EITHER,
        outdoor_space_requirement=OutdoorSpaceRequirement.NOT_REQUIRED,
        experience_requirement=ExperienceRequirement.NO_EXPERIENCE_REQUIRED,
        description="Test animal",
        status=AnimalStatus.AVAILABLE,
    )
    db_session.add(animal)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_rejects_animal_with_nonexistent_facility(
    db_session: Session,
):
    animal = Animal(
        name="Test Animal",
        species=Species.DOG,
        age_value=2,
        age_unit=AgeUnit.YEARS,
        sex=Sex.MALE,
        size=Size.MEDIUM,
        facility_id=uuid.uuid4(),
        energy_level=EnergyLevel.MEDIUM,
        children_compatibility=Compatibility.COMPATIBLE,
        dog_compatibility=Compatibility.COMPATIBLE,
        cat_compatibility=Compatibility.COMPATIBLE,
        suitable_home_type=SuitableHomeType.EITHER,
        outdoor_space_requirement=OutdoorSpaceRequirement.NOT_REQUIRED,
        experience_requirement=ExperienceRequirement.NO_EXPERIENCE_REQUIRED,
        description="Test animal",
        status=AnimalStatus.AVAILABLE,
    )
    db_session.add(animal)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def create_adopter_and_animal(db_session: Session) -> tuple[AdopterProfile, Animal]:
    organisation = RescueOrganisation(
        name="Test Rescue",
        contact_email="test@example.com",
        contact_phone="0000000000",
        address="Test Address",
    )
    db_session.add(organisation)
    db_session.flush()

    facility = Facility(
        organisation_id=organisation.id,
        name="Test Facility",
        address="Test Address",
        contact_phone="0000000000",
    )
    db_session.add(facility)
    db_session.flush()

    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.ADOPTER,
    )
    db_session.add(user)
    db_session.flush()

    adopter_profile = AdopterProfile(
        user_id=user.id,
        home_type=HomeType.HOUSE,
        outdoor_space=OutdoorSpace.AVAILABLE,
        activity_level=ActivityLevel.MEDIUM,
        children_in_household=False,
        existing_dogs=False,
        existing_cats=False,
        experience_level=ExperienceLevel.SOME_EXPERIENCE,
        time_available=TimeAvailable.TWO_TO_FOUR_HOURS,
    )
    db_session.add(adopter_profile)
    db_session.flush()

    animal = Animal(
        name="Test Animal",
        species=Species.DOG,
        age_value=2,
        age_unit=AgeUnit.YEARS,
        sex=Sex.MALE,
        size=Size.MEDIUM,
        facility_id=facility.id,
        energy_level=EnergyLevel.MEDIUM,
        children_compatibility=Compatibility.COMPATIBLE,
        dog_compatibility=Compatibility.COMPATIBLE,
        cat_compatibility=Compatibility.COMPATIBLE,
        suitable_home_type=SuitableHomeType.EITHER,
        outdoor_space_requirement=OutdoorSpaceRequirement.NOT_REQUIRED,
        experience_requirement=ExperienceRequirement.NO_EXPERIENCE_REQUIRED,
        description="Test animal",
        status=AnimalStatus.AVAILABLE,
    )
    db_session.add(animal)
    db_session.flush()

    return adopter_profile, animal


def create_application(
    adopter_profile: AdopterProfile,
    animal: Animal,
    status: ApplicationStatus,
) -> Application:
    return Application(
        adopter_profile_id=adopter_profile.id,
        animal_id=animal.id,
        status=status,
        reason_for_adoption="Test reason",
        care_plan="Test care plan",
        additional_information=None,
        home_type=HomeType.HOUSE,
        outdoor_space=OutdoorSpace.AVAILABLE,
        activity_level=ActivityLevel.MEDIUM,
        children_in_household=False,
        existing_dogs=False,
        existing_cats=False,
        experience_level=ExperienceLevel.SOME_EXPERIENCE,
        time_available=TimeAvailable.TWO_TO_FOUR_HOURS,
    )


def test_database_rejects_two_active_applications_for_same_adopter_and_animal(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    first_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    db_session.add(first_application)
    db_session.commit()

    second_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.UNDER_REVIEW,
    )
    db_session.add(second_application)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_database_allows_terminal_application_after_active_application(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    active_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    db_session.add(active_application)
    db_session.commit()

    terminal_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.DECLINED,
    )
    db_session.add(terminal_application)
    db_session.commit()

    assert terminal_application.status == ApplicationStatus.DECLINED


def test_database_rejects_duplicate_favourite(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    first_favourite = Favourite(
        adopter_profile_id=adopter_profile.id,
        animal_id=animal.id,
    )
    db_session.add(first_favourite)
    db_session.commit()
    db_session.expunge(first_favourite)

    second_favourite = Favourite(
        adopter_profile_id=adopter_profile.id,
        animal_id=animal.id,
    )
    db_session.add(second_favourite)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
