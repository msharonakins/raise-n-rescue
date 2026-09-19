import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import ChildAgeGroup
from backend.app.models.base import Base


class AdopterChildAgeGroup(Base):
    __tablename__ = "adopter_child_age_groups"

    adopter_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("adopter_profiles.id"),
        primary_key=True,
    )

    child_age_group: Mapped[ChildAgeGroup] = mapped_column(
        SAEnum(ChildAgeGroup, name="child_age_group"),
        nullable=False,
        primary_key=True,
    )