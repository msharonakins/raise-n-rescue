import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Index, Text, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import (
    ActivityLevel,
    ApplicationStatus,
    ExperienceLevel,
    HomeType,
    OutdoorSpace,
    TimeAvailable,
)
from backend.app.models.base import Base


class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        Index(
            "uq_applications_one_active_per_adopter_animal",
            "adopter_profile_id",
            "animal_id",
            unique=True,
            postgresql_where=text(
                "status IN ('SUBMITTED', 'UNDER_REVIEW', 'HOME_CHECK', 'APPROVED')"
            ),
        ),
    )

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

    reason_for_adoption: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    care_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    additional_information: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    home_type: Mapped[HomeType] = mapped_column(
        SAEnum(HomeType, name="home_type"),
        nullable=False,
    )

    outdoor_space: Mapped[OutdoorSpace] = mapped_column(
        SAEnum(OutdoorSpace, name="outdoor_space"),
        nullable=False,
    )

    activity_level: Mapped[ActivityLevel] = mapped_column(
        SAEnum(ActivityLevel, name="activity_level"),
        nullable=False,
    )

    children_in_household: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    existing_dogs: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    existing_cats: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    experience_level: Mapped[ExperienceLevel] = mapped_column(
        SAEnum(ExperienceLevel, name="experience_level"),
        nullable=False,
    )

    time_available: Mapped[TimeAvailable] = mapped_column(
        SAEnum(TimeAvailable, name="time_available"),
        nullable=False,
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