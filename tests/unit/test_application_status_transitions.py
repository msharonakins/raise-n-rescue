import pytest

from backend.app.core.enums import ApplicationStatus
from backend.app.services.application_status_transitions import (
    is_valid_application_status_transition,
)


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.UNDER_REVIEW,
        ),
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.WITHDRAWN,
        ),
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.DECLINED,
        ),
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        ),
        (
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.HOME_CHECK,
        ),
        (
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.WITHDRAWN,
        ),
        (
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.DECLINED,
        ),
        (
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        ),
        (
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.APPROVED,
        ),
        (
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.WITHDRAWN,
        ),
        (
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.DECLINED,
        ),
        (
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
        ),
        (
            ApplicationStatus.APPROVED,
            ApplicationStatus.ADOPTED,
        ),
        (
            ApplicationStatus.APPROVED,
            ApplicationStatus.WITHDRAWN,
        ),
    ],
)
def test_valid_application_status_transitions(
    current_status: ApplicationStatus,
    target_status: ApplicationStatus,
):
    assert is_valid_application_status_transition(
        current_status,
        target_status,
    )


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.HOME_CHECK,
        ),
        (
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.APPROVED,
        ),
        (
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.APPROVED,
        ),
        (
            ApplicationStatus.HOME_CHECK,
            ApplicationStatus.ADOPTED,
        ),
        (
            ApplicationStatus.APPROVED,
            ApplicationStatus.DECLINED,
        ),
        (
            ApplicationStatus.ADOPTED,
            ApplicationStatus.UNDER_REVIEW,
        ),
        (
            ApplicationStatus.DECLINED,
            ApplicationStatus.UNDER_REVIEW,
        ),
        (
            ApplicationStatus.WITHDRAWN,
            ApplicationStatus.SUBMITTED,
        ),
        (
            ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
            ApplicationStatus.APPROVED,
        ),
    ],
)
def test_invalid_application_status_transitions(
    current_status: ApplicationStatus,
    target_status: ApplicationStatus,
):
    assert not is_valid_application_status_transition(
        current_status,
        target_status,
    )


@pytest.mark.parametrize(
    "terminal_status",
    [
        ApplicationStatus.ADOPTED,
        ApplicationStatus.DECLINED,
        ApplicationStatus.WITHDRAWN,
        ApplicationStatus.CLOSED_ANIMAL_ADOPTED,
    ],
)
def test_terminal_application_statuses_have_no_valid_transitions(
    terminal_status: ApplicationStatus,
):
    for target_status in ApplicationStatus:
        assert not is_valid_application_status_transition(
            terminal_status,
            target_status,
        )
