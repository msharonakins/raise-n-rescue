import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import (
    ActivityLevel,
    ExperienceLevel,
    HomeType,
    OutdoorSpace,
    TimeAvailable,
)
from backend.app.models.base import Base


class AdopterProfile(Base):
    __tablename__ = "adopter_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
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

    created_at: Mapped[datetime] = mapped_column(
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