import uuid

from sqlalchemy.orm import Session

from backend.app.core.enums import ApplicationStatus
from backend.app.models.application_status_history import ApplicationStatusHistory
from backend.app.repositories.application_repository import ApplicationRepository
from tests.integration.test_database import create_adopter_and_animal, create_application


def test_get_by_id_returns_application(db_session: Session):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    db_session.add(application)
    db_session.commit()

    repository = ApplicationRepository(db_session)

    result = repository.get_by_id(application.id)

    assert result is not None
    assert result.id == application.id
    assert result.adopter_profile_id == adopter_profile.id
    assert result.animal_id == animal.id
    assert result.status == ApplicationStatus.SUBMITTED


def test_get_by_id_returns_none_for_missing_application(
    db_session: Session,
):
    repository = ApplicationRepository(db_session)

    result = repository.get_by_id(uuid.uuid4())

    assert result is None


def test_get_active_by_adopter_and_animal_returns_only_active_application(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )
    db_session.add(application)
    db_session.commit()

    repository = ApplicationRepository(db_session)

    result = repository.get_active_by_adopter_and_animal(
        adopter_profile.id,
        animal.id,
    )

    assert result is not None
    assert result.id == application.id
    assert result.status == ApplicationStatus.SUBMITTED


def test_get_active_by_adopter_and_animal_ignores_terminal_application(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.DECLINED,
    )
    db_session.add(application)
    db_session.commit()

    repository = ApplicationRepository(db_session)

    result = repository.get_active_by_adopter_and_animal(
        adopter_profile.id,
        animal.id,
    )

    assert result is None


def test_add_application_and_status_history_persists_records(
    db_session: Session,
):
    adopter_profile, animal = create_adopter_and_animal(db_session)

    repository = ApplicationRepository(db_session)

    application = create_application(
        adopter_profile,
        animal,
        ApplicationStatus.SUBMITTED,
    )

    repository.add(application)

    db_session.flush()

    status_history = ApplicationStatusHistory(
        application_id=application.id,
        status=ApplicationStatus.SUBMITTED,
        changed_by=adopter_profile.user_id,
        note=None,
    )

    repository.add_status_history(status_history)

    db_session.commit()

    persisted_application = repository.get_by_id(application.id)

    assert persisted_application is not None
    assert persisted_application.id == application.id

    persisted_history = db_session.get(
        ApplicationStatusHistory,
        status_history.id,
    )

    assert persisted_history is not None
    assert persisted_history.application_id == application.id
    assert persisted_history.status == ApplicationStatus.SUBMITTED
    assert persisted_history.changed_by == adopter_profile.user_id
