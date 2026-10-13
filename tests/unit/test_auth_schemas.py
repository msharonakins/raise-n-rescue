import pytest
from pydantic import ValidationError

from backend.app.schemas.auth import RegisterRequest


def test_register_request_trims_email_whitespace():
    request = RegisterRequest(
        email="  Person@example.com  ",
        password="correct-horse-battery",
    )

    assert request.email == "Person@example.com"


def test_register_request_accepts_valid_email_and_password():
    request = RegisterRequest(
        email="person@example.com",
        password="correct-horse-battery",
    )

    assert request.email == "person@example.com"
    assert request.password == "correct-horse-battery"


@pytest.mark.parametrize(
    "email",
    [
        "",
        "not-an-email",
        "person@",
        "@example.com",
        "person@example",
        "person @example.com",
        "person@example..com",
    ],
)
def test_register_request_rejects_invalid_email(email: str):
    with pytest.raises(ValidationError):
        RegisterRequest(
            email=email,
            password="correct-horse-battery",
        )


@pytest.mark.parametrize(
    "password",
    [
        "",
        "short",
        "a" * 129,
    ],
)
def test_register_request_rejects_invalid_password(password: str):
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="person@example.com",
            password=password,
        )


@pytest.mark.parametrize(
    "extra_field",
    [
        {"role": "RESCUE_STAFF"},
        {"organisation_id": "123"},
    ],
)
def test_register_request_rejects_server_controlled_fields(
    extra_field: dict[str, str],
):
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="person@example.com",
            password="correct-horse-battery",
            **extra_field,
        )
