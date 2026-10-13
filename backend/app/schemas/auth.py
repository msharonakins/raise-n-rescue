import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


EmailInput = Annotated[str, Field(min_length=3, max_length=320)]
PasswordInput = Annotated[str, Field(min_length=12, max_length=128)]


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    email: EmailInput
    password: PasswordInput

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        value = value.strip()

        if len(value) < 3 or len(value) > 320:
            return value

        if value.count("@") != 1:
            raise ValueError("Enter a valid email address")

        local_part, domain = value.rsplit("@", 1)

        if (
            not local_part
            or len(local_part) > 64
            or not domain
            or "." not in domain
            or domain.startswith(".")
            or domain.endswith(".")
            or any(char.isspace() for char in value)
            or re.search(r"[^A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]", local_part)
            or any(not label or len(label) > 63 for label in domain.split("."))
            or any(
                not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
                for label in domain.split(".")
            )
        ):
            raise ValueError("Enter a valid email address")

        return value
