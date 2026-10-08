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
    UserRole,
)
from backend.app.models.adopter_child_age_group import AdopterChildAgeGroup
from backend.app.models.adopter_preferred_size import AdopterPreferredSize
from backend.app.models.adopter_preferred_species import AdopterPreferredSpecies
from backend.app.models.animal import Animal
from backend.app.models.application import Application
from backend.app.models.application_child_age_group import ApplicationChildAgeGroup
from backend.app.models.application_preferred_size import ApplicationPreferredSize
from backend.app.models.application_preferred_species import (
    ApplicationPreferredSpecies,
)
from backend.app.models.application_status_history import (
    ApplicationStatusHistory,
)
from backend.app.models.facility import Facility
from backend.app.models.organisation import RescueOrganisation
from backend.app.models.user import User
from backend.app.services.application_errors import (
    ActiveApplicationExistsError,
    AdopterProfileNotFoundError,
    AnimalNotAvailableError,
    AnimalNotFoundError,
    ApplicationAuthorisationError,
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


def create_rescue_staff(
    db_session: Session,
    organisation_id: uuid.UUID,
) -> User:
    user = User(
        email=f"rescue-staff-{uuid.uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.RESCUE_STAFF,
        organisation_id=organisation_id,
    )
    db_session.add(user)
    db_session.flush()
    return user


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


def test_submit_application_translates_active_application_unique_constraint(
    service_sessions: tuple[Session, Session],
    monkeypatch: pytest.MonkeyPatch,
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

    monkeypatch.setattr(
        service.application_repository,
        "get_active_by_adopter_and_animal",
        lambda adopter_profile_id, animal_id: None,
    )

    with pytest.raises(ActiveApplicationExistsError):
        service.submit_application(
            user_id=adopter_profile.user_id,
            submission=submission,
        )

    application_count = service_session.execute(
        select(Application).where(
            Application.adopter_profile_id == adopter_profile.id,
            Application.animal_id == animal.id,
        )
    ).scalars().all()

    assert len(application_count) == 1
    assert application_count[0].id == existing_application.id


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

    facility = setup_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        setup_session,
        facility.organisation_id,
    )
    setup_session.commit()

    service = ApplicationService(service_session)

    note = "Initial application review completed."

    updated_application = service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.UNDER_REVIEW,
        actor=rescue_staff,
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
    assert status_history[0].changed_by == rescue_staff.id
    assert status_history[0].note == note


def test_transition_application_status_raises_when_application_does_not_exist(
    service_sessions: tuple[Session, Session],
):
    _, service_session = service_sessions

    service = ApplicationService(service_session)

    actor = User(
        id=uuid.uuid4(),
        email="missing@example.com",
        password_hash="test-password-hash",
        role=UserRole.RESCUE_STAFF,
        organisation_id=uuid.uuid4(),
    )

    with pytest.raises(ApplicationNotFoundError):
        service.transition_application_status(
            application_id=uuid.uuid4(),
            target_status=ApplicationStatus.UNDER_REVIEW,
            actor=actor,
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

    facility = setup_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        setup_session,
        facility.organisation_id,
    )
    setup_session.commit()

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationStatusTransitionError):
        service.transition_application_status(
            application_id=application.id,
            target_status=ApplicationStatus.APPROVED,
            actor=rescue_staff,
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

    facility = setup_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        setup_session,
        facility.organisation_id,
    )
    setup_session.commit()

    service = ApplicationService(service_session)

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.UNDER_REVIEW,
        actor=rescue_staff,
    )

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.HOME_CHECK,
        actor=rescue_staff,
    )

    service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.APPROVED,
        actor=rescue_staff,
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


def test_adopter_can_only_withdraw_own_application(
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
    setup_session.commit()

    adopter = setup_session.get(User, adopter_profile.user_id)
    assert adopter is not None

    service = ApplicationService(service_session)

    updated_application = service.transition_application_status(
        application_id=application.id,
        target_status=ApplicationStatus.WITHDRAWN,
        actor=adopter,
    )

    assert updated_application.status == ApplicationStatus.WITHDRAWN


def test_adopter_cannot_manage_application_status(
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
    setup_session.commit()

    adopter = setup_session.get(User, adopter_profile.user_id)
    assert adopter is not None

    service = ApplicationService(service_session)

    with pytest.raises(ApplicationAuthorisationError):
        service.transition_application_status(
            application_id=application.id,
            target_status=ApplicationStatus.UNDER_REVIEW,
            actor=adopter,
        )


def test_rescue_staff_cannot_manage_application_from_another_organisation(
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

    other_organisation = RescueOrganisation(
        name="Other Rescue",
        contact_email="other@example.com",
        contact_phone="0000000000",
        address="Other Address",
    )
    setup_session.add(other_organisation)
    setup_session.flush()

    rescue_staff = create_rescue_staff(
        setup_session,
        other_organisation.id,
    )
    setup_session.commit()

    service = ApplicationService(service_session)

    with pytest.raises(ApplicationAuthorisationError):
        service.transition_application_status(
            application_id=application.id,
            target_status=ApplicationStatus.UNDER_REVIEW,
            actor=rescue_staff,
        )


def test_transition_application_status_cannot_directly_adopt(
    service_sessions: tuple[Session, Session],
):
    setup_session, service_session = service_sessions

    adopter_profile, animal = create_adopter_and_animal(setup_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.APPROVED,
    )
    setup_session.add(application)
    setup_session.flush()

    facility = setup_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        setup_session,
        facility.organisation_id,
    )
    setup_session.commit()

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationStatusTransitionError):
        service.transition_application_status(
            application_id=application.id,
            target_status=ApplicationStatus.ADOPTED,
            actor=rescue_staff,
        )


def test_complete_adoption_updates_application_and_animal(
    service_sessions: tuple[Session, Session],
) -> None:
    db_session, service_session = service_sessions
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.APPROVED,
    )
    db_session.add(application)
    db_session.commit()

    facility = db_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        db_session,
        facility.organisation_id,
    )
    db_session.commit()

    service = ApplicationService(service_session)

    result = service.complete_adoption(
        application_id=application.id,
        actor=rescue_staff,
    )

    db_session.expire_all()

    refreshed_application = db_session.get(Application, application.id)
    refreshed_animal = db_session.get(Animal, animal.id)

    assert result.status == ApplicationStatus.ADOPTED
    assert refreshed_application is not None
    assert refreshed_application.status == ApplicationStatus.ADOPTED
    assert refreshed_animal is not None
    assert refreshed_animal.status == AnimalStatus.ADOPTED

    history = db_session.scalars(
        select(ApplicationStatusHistory)
        .where(ApplicationStatusHistory.application_id == application.id)
        .order_by(ApplicationStatusHistory.created_at)
    ).all()

    assert history[-1].status == ApplicationStatus.ADOPTED
    assert history[-1].changed_by == rescue_staff.id


def test_complete_adoption_closes_other_active_applications(
    service_sessions: tuple[Session, Session],
) -> None:
    db_session, service_session = service_sessions
    adopter_profile, animal = create_adopter_and_animal(db_session)

    approved_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.APPROVED,
    )

    other_adopter_profile, _ = create_adopter_and_animal(db_session)

    other_application = create_application(
        other_adopter_profile,
        animal,
        ApplicationStatus.UNDER_REVIEW,
    )

    db_session.add_all([approved_application, other_application])
    db_session.commit()

    facility = db_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        db_session,
        facility.organisation_id,
    )
    db_session.commit()

    service = ApplicationService(service_session)

    service.complete_adoption(
        application_id=approved_application.id,
        actor=rescue_staff,
    )

    db_session.expire_all()

    refreshed_approved = db_session.get(
        Application,
        approved_application.id,
    )
    refreshed_other = db_session.get(
        Application,
        other_application.id,
    )

    assert refreshed_approved is not None
    assert refreshed_other is not None
    assert refreshed_approved.status == ApplicationStatus.ADOPTED
    assert (
        refreshed_other.status
        == ApplicationStatus.CLOSED_ANIMAL_ADOPTED
    )

    other_history = db_session.scalars(
        select(ApplicationStatusHistory)
        .where(
            ApplicationStatusHistory.application_id
            == other_application.id
        )
        .order_by(ApplicationStatusHistory.created_at)
    ).all()

    assert other_history[-1].status == ApplicationStatus.CLOSED_ANIMAL_ADOPTED
    assert other_history[-1].changed_by == rescue_staff.id


def test_complete_adoption_raises_when_application_does_not_exist(
    service_sessions: tuple[Session, Session],
) -> None:
    _, service_session = service_sessions

    service = ApplicationService(service_session)

    actor = User(
        id=uuid.uuid4(),
        email="missing-rescue-staff@example.com",
        password_hash="test-password-hash",
        role=UserRole.RESCUE_STAFF,
        organisation_id=uuid.uuid4(),
    )

    with pytest.raises(ApplicationNotFoundError):
        service.complete_adoption(
            application_id=uuid.uuid4(),
            actor=actor,
        )


def test_complete_adoption_raises_when_animal_does_not_exist(
    service_sessions: tuple[Session, Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_session, service_session = service_sessions
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.APPROVED,
    )
    db_session.add(application)
    db_session.commit()

    facility = db_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        db_session,
        facility.organisation_id,
    )
    db_session.commit()

    service = ApplicationService(service_session)

    monkeypatch.setattr(
        service.animal_repository,
        "get_by_id_for_update",
        lambda animal_id: None,
    )

    with pytest.raises(AnimalNotFoundError):
        service.complete_adoption(
            application_id=application.id,
            actor=rescue_staff,
        )


def test_complete_adoption_raises_when_application_is_not_approved(
    service_sessions: tuple[Session, Session],
) -> None:
    db_session, service_session = service_sessions
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.UNDER_REVIEW,
    )
    db_session.add(application)
    db_session.commit()

    facility = db_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        db_session,
        facility.organisation_id,
    )
    db_session.commit()

    service = ApplicationService(service_session)

    with pytest.raises(InvalidApplicationStatusTransitionError):
        service.complete_adoption(
            application_id=application.id,
            actor=rescue_staff,
        )

    db_session.expire_all()

    refreshed_application = db_session.get(Application, application.id)
    refreshed_animal = db_session.get(Animal, animal.id)

    assert refreshed_application is not None
    assert refreshed_animal is not None
    assert refreshed_application.status == ApplicationStatus.UNDER_REVIEW
    assert refreshed_animal.status == AnimalStatus.AVAILABLE


def test_complete_adoption_rolls_back_all_changes_when_a_later_operation_fails(
    service_sessions: tuple[Session, Session],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_session, service_session = service_sessions
    adopter_profile, animal = create_adopter_and_animal(db_session)

    approved_application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.APPROVED,
    )

    other_adopter_profile, _ = create_adopter_and_animal(db_session)

    other_application = create_application(
        other_adopter_profile,
        animal,
        ApplicationStatus.UNDER_REVIEW,
    )

    db_session.add_all(
        [approved_application, other_application]
    )
    db_session.commit()

    facility = db_session.get(Facility, animal.facility_id)
    assert facility is not None

    rescue_staff = create_rescue_staff(
        db_session,
        facility.organisation_id,
    )
    db_session.commit()

    service = ApplicationService(service_session)

    original_add_status_history = (
        service.application_repository.add_status_history
    )

    call_count = 0

    def failing_add_status_history(
        status_history: ApplicationStatusHistory,
    ) -> ApplicationStatusHistory:
        nonlocal call_count
        call_count += 1

        if call_count == 2:
            raise RuntimeError("simulated failure")

        return original_add_status_history(status_history)

    monkeypatch.setattr(
        service.application_repository,
        "add_status_history",
        failing_add_status_history,
    )

    with pytest.raises(RuntimeError, match="simulated failure"):
        service.complete_adoption(
            application_id=approved_application.id,
            actor=rescue_staff,
        )

    db_session.expire_all()

    refreshed_approved = db_session.get(
        Application,
        approved_application.id,
    )
    refreshed_other = db_session.get(
        Application,
        other_application.id,
    )
    refreshed_animal = db_session.get(
        Animal,
        animal.id,
    )

    assert refreshed_approved is not None
    assert refreshed_other is not None
    assert refreshed_animal is not None

    assert refreshed_approved.status == ApplicationStatus.APPROVED
    assert refreshed_other.status == ApplicationStatus.UNDER_REVIEW
    assert refreshed_animal.status == AnimalStatus.AVAILABLE

    approved_history = db_session.scalars(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id
            == approved_application.id
        )
    ).all()

    other_history = db_session.scalars(
        select(ApplicationStatusHistory).where(
            ApplicationStatusHistory.application_id
            == other_application.id
        )
    ).all()

    assert approved_history == []
    assert other_history == []
