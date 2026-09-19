import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import ApplicationStatus
from backend.app.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    adopter_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("adopter_profiles.id"),
        nullable=False,
    )

    animal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("animals.id"),
        nullable=False,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, name="application_status"),
        nullable=False,
    )

    applicant_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )