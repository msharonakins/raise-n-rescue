import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import Size
from backend.app.models.base import Base


class AdopterPreferredSize(Base):
    __tablename__ = "adopter_preferred_sizes"

    adopter_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("adopter_profiles.id"),
        primary_key=True,
    )

    size: Mapped[Size] = mapped_column(
        SAEnum(Size, name="size"),
        nullable=False,
        primary_key=True,
    )