from backend.app.core.enums import ApplicationStatus


ALLOWED_APPLICATION_STATUS_TRANSITIONS: dict[
    ApplicationStatus,
    frozenset[ApplicationStatus],
] = {
    ApplicationStatus.SUBMITTED: frozenset(
        {
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.DECLINED,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        }
    ),
    ApplicationStatus.UNDER_REVIEW: frozenset(
        {
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.DECLINED,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        }
    ),
    ApplicationStatus.HOME_CHECK: frozenset(
        {
            ApplicationStatus.APPROVED,
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.DECLINED,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        }
    ),
    ApplicationStatus.APPROVED: frozenset(
        {
            ApplicationStatus.ADOPTED,
            ApplicationStatus.WITHDRAWN,
        }
    ),
    ApplicationStatus.ADOPTED: frozenset(),
    ApplicationStatus.DECLINED: frozenset(),
    ApplicationStatus.WITHDRAWN: frozenset(),
    ApplicationStatus.CLOSED_ANIMAL_ADOPTED: frozenset(),
}


def is_valid_application_status_transition(
    current_status: ApplicationStatus,
    target_status: ApplicationStatus,
) -> bool:
    return target_status in ALLOWED_APPLICATION_STATUS_TRANSITIONS[current_status]
