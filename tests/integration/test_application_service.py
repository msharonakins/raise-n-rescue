import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import AnimalStatus, ApplicationStatus
from backend.app.models.application_status_history import ApplicationStatusHistory
from backend.app.services.application_errors import (
    ActiveApplicationExistsError,
    AdopterProfileNotFoundError,
    AnimalNotAvailableError,
    AnimalNotFoundError,
    InvalidApplicationSubmissionError,
)
from backend.app.services.application_inputs import ApplicationSubmissionData
from backend.app.services.application_service import ApplicationService
from tests.integration.test_database import (
    create_adopter_and_animal,
    create_application,
)


def test_submit_application_creates_application_and_initial_history(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
        additional_information="I have experience caring for dogs.",
    )

    service = ApplicationService(service_session)

    application = service.submit_application(
        user_id=adopter_profile.user_id,
        submission=submission,
    )

    assert application.id is not None
    assert application.adopter_profile_id == adopter_profile.id
    assert application.animal_id == animal.id
    assert application.status == ApplicationStatus.SUBMITTED
    assert application.reason_for_adoption == submission.reason_for_adoption
    assert application.care_plan == submission.care_plan
    assert application.additional_information == submission.additional_information

    assert application.home_type == adopter_profile.home_type
    assert application.outdoor_space == adopter_profile.outdoor_space
    assert application.activity_level == adopter_profile.activity_level
    assert (
        application.children_in_household
        == adopter_profile.children_in_household
    )
    assert application.existing_dogs == adopter_profile.existing_dogs
    assert application.existing_cats == adopter_profile.existing_cats
    assert application.experience_level == adopter_profile.experience_level
    assert application.time_available == adopter_profile.time_available

    status_history = service_session.execute(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id == application.id
        )
    ).scalar_one()

    assert status_history.status == ApplicationStatus.SUBMITTED
    assert status_history.changed_by == adopter_profile.user_id
    assert status_history.note is None


def test_submit_application_raises_when_adopter_profile_does_not_exist(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    _, animal = create_adopter_and_animal(setup_session)

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    with pytest.raises(AdopterProfileNotFoundError):
        service.submit_application(
            user_id=uuid.uuid4(),
            submission=submission,
        )


def test_submit_application_raises_when_animal_does_not_exist(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, _ = create_adopter_and_animal(setup_session)

    submission = ApplicationSubmissionData(
        animal_id=uuid.uuid4(),
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    with pytest.raises(AnimalNotFoundError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )


def test_submit_application_raises_when_animal_is_not_available(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    animal.status = AnimalStatus.ADOPTION_PENDING
    setup_session.flush()

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    with pytest.raises(AnimalNotAvailableError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )


def test_submit_application_raises_when_active_application_exists(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    existing_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    setup_session.add(existing_application)
    setup_session.flush()

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide another permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    with pytest.raises(ActiveApplicationExistsError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )


def test_submit_application_raises_when_reason_for_adoption_is_blank(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="   ",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationSubmissionError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )


def test_submit_application_raises_when_care_plan_is_blank(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="   ",
    )

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationSubmissionError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )
