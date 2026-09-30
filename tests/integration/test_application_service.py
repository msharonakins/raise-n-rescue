import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import (
    AnimalStatus,
    ApplicationStatus,
    ChildAgeGroup,
    Size,
    Species,
)
from backend.app.models.application_status_history import ApplicationStatusHistory
from backend.app.models.application_child_age_group import ApplicationChildAgeGroup
from backend.app.models.application_preferred_size import ApplicationPreferredSize
from backend.app.models.application_preferred_species import ApplicationPreferredSpecies
from backend.app.models.adopter_child_age_group import AdopterChildAgeGroup
from backend.app.models.adopter_preferred_size import AdopterPreferredSize
from backend.app.models.adopter_preferred_species import AdopterPreferredSpecies
from backend.app.services.application_errors import (
    ActiveApplicationExistsError,
    AdopterProfileNotFoundError,
    IncompleteAdopterProfileError,
    AnimalNotAvailableError,
    AnimalNotFoundError,
    ApplicationNotFoundError,
    InvalidApplicationSubmissionError,
    InvalidApplicationStatusTransitionError,
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

    setup_session.add_all(
        [
            AdopterPreferredSpecies(
                adopter_profile_id=adopter_profile.id,
                species=Species.DOG,
            ),
            AdopterPreferredSpecies(
                adopter_profile_id=adopter_profile.id,
                species=Species.CAT,
            ),
            AdopterPreferredSize(
                adopter_profile_id=adopter_profile.id,
                size=Size.MEDIUM,
            ),
            AdopterPreferredSize(
                adopter_profile_id=adopter_profile.id,
                size=Size.LARGE,
            ),
            AdopterChildAgeGroup(
                adopter_profile_id=adopter_profile.id,
                child_age_group=ChildAgeGroup.SCHOOL_AGE_CHILDREN,
            ),
            AdopterChildAgeGroup(
                adopter_profile_id=adopter_profile.id,
                child_age_group=ChildAgeGroup.TEENAGERS,
            ),
        ]
    )
    setup_session.flush()

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

    preferred_species = service_session.execute(
        select(ApplicationPreferredSpecies).where(
            ApplicationPreferredSpecies.application_id == application.id
        )
    ).scalars().all()

    assert {preference.species for preference in preferred_species} == {
        Species.DOG,
        Species.CAT,
    }

    preferred_sizes = service_session.execute(
        select(ApplicationPreferredSize).where(
            ApplicationPreferredSize.application_id == application.id
        )
    ).scalars().all()

    assert {preference.size for preference in preferred_sizes} == {
        Size.MEDIUM,
        Size.LARGE,
    }

    child_age_groups = service_session.execute(
        select(ApplicationChildAgeGroup).where(
            ApplicationChildAgeGroup.application_id == application.id
        )
    ).scalars().all()

    assert {
        preference.child_age_group for preference in child_age_groups
    } == {
        ChildAgeGroup.SCHOOL_AGE_CHILDREN,
        ChildAgeGroup.TEENAGERS,
    }

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


def test_submit_application_raises_when_adopter_profile_is_incomplete(
    service_sessions: tuple[Session, Session],
    monkeypatch: pytest.MonkeyPatch,
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    adopter_profile.home_type = None

    submission = ApplicationSubmissionData(
        animal_id=animal.id,
        reason_for_adoption="I want to provide a permanent home.",
        care_plan="I will provide daily exercise, feeding, and veterinary care.",
    )

    service = ApplicationService(service_session)

    monkeypatch.setattr(
        service.adopter_profile_repository,
        "get_by_user_id",
        lambda user_id: adopter_profile,
    )

    with pytest.raises(IncompleteAdopterProfileError):
        service.submit_application(
            user_id=adopter_profile.user_id,
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


def test_transition_application_status_updates_status_and_creates_history(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    setup_session.add(application)
    setup_session.flush()

    service = ApplicationService(service_session)

    note = "Initial application review completed."

    updated_application = service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.UNDER_REVIEW,
        changed_by=adopter_profile.user_id,
        note=note,
    )

    assert updated_application.status == ApplicationStatus.UNDER_REVIEW

    status_history = service_session.execute(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id == application.id
        )
    ).scalars().all()

    assert len(status_history) == 1
    assert status_history[0].status == ApplicationStatus.UNDER_REVIEW
    assert status_history[0].changed_by == adopter_profile.user_id
    assert status_history[0].note == note


def test_transition_application_status_raises_when_application_does_not_exist(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = ApplicationService(service_session)

    with pytest.raises(ApplicationNotFoundError):
        service.transition_application_status(
            application_id=uuid.uuid4(),
            target_status=ApplicationStatus.UNDER_REVIEW,
            changed_by=uuid.uuid4(),
        )


def test_transition_application_status_raises_for_invalid_transition(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    setup_session.add(application)
    setup_session.flush()

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationStatusTransitionError):
        service.transition_application_status(
            application_id=application.id,
            target_status=ApplicationStatus.APPROVED,
            changed_by=adopter_profile.user_id,
        )

    assert application.status == ApplicationStatus.SUBMITTED

    status_history = service_session.execute(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id == application.id
        )
    ).scalars().all()

    assert status_history == []


def test_transition_application_status_can_follow_multiple_valid_transitions(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    setup_session.add(application)
    setup_session.flush()

    service = ApplicationService(service_session)

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.UNDER_REVIEW,
        changed_by=adopter_profile.user_id,
    )

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.HOME_CHECK,
        changed_by=adopter_profile.user_id,
    )

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.APPROVED,
        changed_by=adopter_profile.user_id,
    )

    persisted_application = service_session.get(
        type(application),
        application.id,
    )

    assert persisted_application is not None
    assert persisted_application.status == ApplicationStatus.APPROVED

    status_history = service_session.execute(
        select(ApplicationStatusHistory)
        .where(ApplicationStatusHistory.application_id == application.id)
        .order_by(ApplicationStatusHistory.created_at)
    ).scalars().all()

    assert [history.status for history in status_history] == [
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.HOME_CHECK,
        ApplicationStatus.APPROVED,
    ]
