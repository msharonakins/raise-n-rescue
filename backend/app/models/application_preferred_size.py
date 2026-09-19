import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import Size
from backend.app.models.base import Base


class ApplicationPreferredSize(Base):
    __tablename__ = "application_preferred_sizes"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id"),
        primary_key=True,
    )

    size: Mapped[Size] = mapped_column(
        SAEnum(Size, name="size"),
        nullable=False,
        primary_key=True,
    )