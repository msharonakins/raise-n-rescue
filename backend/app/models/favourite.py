import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class Favourite(Base):
    __tablename__ = "favourites"

    adopter_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("adopter_profiles.id"),
        primary_key=True,
    )

    animal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("animals.id"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )