import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.enums import AnimalStatus, ApplicationStatus
from backend.app.models.application import Application
from backend.app.models.application_child_age_group import ApplicationChildAgeGroup
from backend.app.models.application_preferred_size import ApplicationPreferredSize
from backend.app.models.application_preferred_species import ApplicationPreferredSpecies
from backend.app.models.application_status_history import ApplicationStatusHistory
from backend.app.repositories.adopter_profile_repository import (
    AdopterProfileRepository,
)
from backend.app.repositories.animal_repository import AnimalRepository
from backend.app.repositories.application_repository import ApplicationRepository
from backend.app.services.application_errors import (
    ActiveApplicationExistsError,
    AdopterProfileNotFoundError,
    AnimalNotAvailableError,
    AnimalNotFoundError,
    ApplicationNotFoundError,
    InvalidApplicationSubmissionError,
    InvalidApplicationStatusTransitionError,
)
from backend.app.services.application_inputs import ApplicationSubmissionData
from backend.app.services.application_status_transitions import (
    is_valid_application_status_transition,
)


ACTIVE_APPLICATION_UNIQUE_CONSTRAINT = (
    "uq_applications_one_active_per_adopter_animal"
)


def _is_active_application_unique_violation(
    error: IntegrityError,
) -> bool:
    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)
    constraint_name = getattr(diagnostic, "constraint_name", None)

    return constraint_name == ACTIVE_APPLICATION_UNIQUE_CONSTRAINT


class ApplicationService:
    def __init__(self, session: Session):
        self.session = session
        self.adopter_profile_repository = AdopterProfileRepository(session)
        self.animal_repository = AnimalRepository(session)
        self.application_repository = ApplicationRepository(session)

    def submit_application(
        self,
        user_id: uuid.UUID,
        submission: ApplicationSubmissionData,
    ) -> Application:
        
        if not submission.reason_for_adoption.strip():
            raise InvalidApplicationSubmissionError(
                "Reason for adoption must not be blank."
            )

        if not submission.care_plan.strip():
            raise InvalidApplicationSubmissionError(
                "Care plan must not be blank."
            )

        try:
            with self.session.begin():
                adopter_profile = self.adopter_profile_repository.get_by_user_id(
                    user_id
                )

                if adopter_profile is None:
                    raise AdopterProfileNotFoundError(
                        "Adopter profile not found."
                    )

                animal = self.animal_repository.get_by_id(submission.animal_id)

                if animal is None:
                    raise AnimalNotFoundError(
                        "Animal not found."
                    )

                if animal.status != AnimalStatus.AVAILABLE:
                    raise AnimalNotAvailableError(
                        "Animal is not currently available for applications."
                    )

                active_application = (
                    self.application_repository.get_active_by_adopter_and_animal(
                        adopter_profile.id,
                        animal.id,
                    )
                )

                if active_application is not None:
                    raise ActiveApplicationExistsError(
                        "An active application already exists for this adopter and animal."
                    )

                application = Application(
                    adopter_profile_id=adopter_profile.id,
                    animal_id=animal.id,
                    status=ApplicationStatus.SUBMITTED,
                    reason_for_adoption=submission.reason_for_adoption,
                    care_plan=submission.care_plan,
                    additional_information=submission.additional_information,
                    home_type=adopter_profile.home_type,
                    outdoor_space=adopter_profile.outdoor_space,
                    activity_level=adopter_profile.activity_level,
                    children_in_household=adopter_profile.children_in_household,
                    existing_dogs=adopter_profile.existing_dogs,
                    existing_cats=adopter_profile.existing_cats,
                    experience_level=adopter_profile.experience_level,
                    time_available=adopter_profile.time_available,
                )

                self.application_repository.add(application)
                self.session.flush()

                preferred_species = (
                    self.adopter_profile_repository.get_preferred_species(
                        adopter_profile.id
                    )
                )

                for preference in preferred_species:
                    self.session.add(
                        ApplicationPreferredSpecies(
                            application_id=application.id,
                            species=preference.species,
                        )
                    )

                preferred_sizes = (
                    self.adopter_profile_repository.get_preferred_sizes(
                        adopter_profile.id
                    )
                )

                for preference in preferred_sizes:
                    self.session.add(
                        ApplicationPreferredSize(
                            application_id=application.id,
                            size=preference.size,
                        )
                    )

                child_age_groups = (
                    self.adopter_profile_repository.get_child_age_groups(
                        adopter_profile.id
                    )
                )

                for preference in child_age_groups:
                    self.session.add(
                        ApplicationChildAgeGroup(
                            application_id=application.id,
                            child_age_group=preference.child_age_group,
                        )
                    )

                status_history = ApplicationStatusHistory(
                    application_id=application.id,
                    status=ApplicationStatus.SUBMITTED,
                    changed_by=user_id,
                    note=None,
                )

                self.application_repository.add_status_history(status_history)

        except IntegrityError as error:
            if _is_active_application_unique_violation(error):
                raise ActiveApplicationExistsError(
                    "An active application already exists for this adopter and animal."
                ) from error

            raise

        return application

    def transition_application_status(
        self,
        application_id: uuid.UUID,
        target_status: ApplicationStatus,
        changed_by: uuid.UUID,
        note: str | None = None,
    ) -> Application:
        with self.session.begin():
            application = self.application_repository.get_by_id(application_id)

            if application is None:
                raise ApplicationNotFoundError("Application not found.")

            if not is_valid_application_status_transition(
                application.status,
                target_status,
            ):
                raise InvalidApplicationStatusTransitionError(
                    f"Cannot transition application from "
                    f"{application.status.value} to {target_status.value}."
                )

            application.status = target_status

            status_history = ApplicationStatusHistory(
                application_id=application.id,
                status=target_status,
                changed_by=changed_by,
                note=note,
            )

            self.application_repository.add_status_history(status_history)

        return application

    def complete_adoption(
        self,
        application_id: uuid.UUID,
        changed_by: uuid.UUID,
    ) -> Application:
        with self.session.begin():
            application = self.application_repository.get_by_id(
                application_id
            )

            if application is None:
                raise ApplicationNotFoundError(
                    "Application not found."
                )

            animal = self.animal_repository.get_by_id(
                application.animal_id
            )

            if animal is None:
                raise AnimalNotFoundError(
                    "Animal not found."
                )

            if not is_valid_application_status_transition(
                application.status,
                ApplicationStatus.ADOPTED,
            ):
                raise InvalidApplicationStatusTransitionError(
                    f"Cannot transition application from "
                    f"{application.status.value} to "
                    f"{ApplicationStatus.ADOPTED.value}."
                )

            application.status = ApplicationStatus.ADOPTED
            animal.status = AnimalStatus.ADOPTED

            status_history = ApplicationStatusHistory(
                application_id=application.id,
                status=ApplicationStatus.ADOPTED,
                changed_by=changed_by,
                note=None,
            )

            self.application_repository.add_status_history(
                status_history
            )

            active_applications = (
                self.application_repository.get_active_by_animal(
                    animal.id
                )
            )

            for other_application in active_applications:
                if other_application.id == application.id:
                    continue

                other_application.status = (
                    ApplicationStatus.CLOSED_ANIMAL_ADOPTED
                )

                other_status_history = ApplicationStatusHistory(
                    application_id=other_application.id,
                    status=ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
                    changed_by=changed_by,
                    note=None,
                )

                self.application_repository.add_status_history(
                    other_status_history
                )

        return application
