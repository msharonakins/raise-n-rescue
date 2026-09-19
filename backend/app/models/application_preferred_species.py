import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import Species
from backend.app.models.base import Base


class ApplicationPreferredSpecies(Base):
    __tablename__ = "application_preferred_species"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id"),
        primary_key=True,
    )

    species: Mapped[Species] = mapped_column(
        SAEnum(Species, name="species"),
        nullable=False,
        primary_key=True,
    )