import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.enums import ApplicationStatus
from backend.app.models.application import Application
from backend.app.models.application_status_history import ApplicationStatusHistory


class ApplicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        statement = select(Application).where(Application.id == application_id)
        return self.session.execute(statement).scalar_one_or_none()

    def get_active_by_adopter_and_animal(
        self,
        adopter_profile_id: uuid.UUID,
        animal_id: uuid.UUID,
    ) -> Application | None:
        statement = select(Application).where(
            Application.adopter_profile_id == adopter_profile_id,
            Application.animal_id == animal_id,
            Application.status.in_(
                (
                    ApplicationStatus.SUBMITTED,
                    ApplicationStatus.UNDER_REVIEW,
                    ApplicationStatus.HOME_CHECK,
                    ApplicationStatus.APPROVED,
                )
            ),
        )
        return self.session.execute(statement).scalar_one_or_none()

    def add(self, application: Application) -> Application:
        self.session.add(application)
        return application

    def add_status_history(
        self,
        status_history: ApplicationStatusHistory,
    ) -> ApplicationStatusHistory:
        self.session.add(status_history)
        return status_history
