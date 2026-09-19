import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import (
    AgeUnit,
    AnimalStatus,
    Compatibility,
    EnergyLevel,
    ExperienceRequirement,
    OutdoorSpaceRequirement,
    Sex,
    Size,
    Species,
    SuitableHomeType,
)
from backend.app.models.base import Base


class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    species: Mapped[Species] = mapped_column(
        SAEnum(Species, name="species"),
        nullable=False,
    )

    age_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    age_unit: Mapped[AgeUnit] = mapped_column(
        SAEnum(AgeUnit, name="age_unit"),
        nullable=False,
    )

    age_recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sex: Mapped[Sex] = mapped_column(
        SAEnum(Sex, name="sex"),
        nullable=False,
    )

    size: Mapped[Size] = mapped_column(
        SAEnum(Size, name="size"),
        nullable=False,
    )

    facility_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("facilities.id"),
        nullable=False,
    )

    energy_level: Mapped[EnergyLevel] = mapped_column(
        SAEnum(EnergyLevel, name="energy_level"),
        nullable=False,
        default=EnergyLevel.UNKNOWN,
    )

    personality_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    children_compatibility: Mapped[Compatibility] = mapped_column(
        SAEnum(Compatibility, name="compatibility"),
        nullable=False,
        default=Compatibility.UNKNOWN,
    )

    dog_compatibility: Mapped[Compatibility] = mapped_column(
        SAEnum(Compatibility, name="compatibility"),
        nullable=False,
        default=Compatibility.UNKNOWN,
    )

    cat_compatibility: Mapped[Compatibility] = mapped_column(
        SAEnum(Compatibility, name="compatibility"),
        nullable=False,
        default=Compatibility.UNKNOWN,
    )

    suitable_home_type: Mapped[SuitableHomeType] = mapped_column(
        SAEnum(SuitableHomeType, name="suitable_home_type"),
        nullable=False,
        default=SuitableHomeType.UNKNOWN,
    )

    outdoor_space_requirement: Mapped[OutdoorSpaceRequirement] = mapped_column(
        SAEnum(OutdoorSpaceRequirement, name="outdoor_space_requirement"),
        nullable=False,
        default=OutdoorSpaceRequirement.UNKNOWN,
    )

    experience_requirement: Mapped[ExperienceRequirement] = mapped_column(
        SAEnum(ExperienceRequirement, name="experience_requirement"),
        nullable=False,
        default=ExperienceRequirement.UNKNOWN,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[AnimalStatus] = mapped_column(
        SAEnum(AnimalStatus, name="animal_status"),
        nullable=False,
        default=AnimalStatus.AVAILABLE,
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

    __table_args__ = (
        CheckConstraint(
            "age_value >= 0",
            name="ck_animals_age_value_non_negative",
        ),
    )


class PersonalityTrait(Base):
    __tablename__ = "personality_traits"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )


class AnimalPersonalityTrait(Base):
    __tablename__ = "animal_personality_traits"

    animal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("animals.id"),
        primary_key=True,
    )

    personality_trait_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("personality_traits.id"),
        primary_key=True,
    )


class AnimalPhoto(Base):
    __tablename__ = "animal_photos"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    animal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("animals.id"),
        nullable=False,
    )

    image_url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    display_order: Mapped[int] = mapped_column(
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "display_order >= 0",
            name="ck_animal_photos_display_order_non_negative",
        ),
    )


Index(
    "uq_animal_photos_one_primary",
    AnimalPhoto.animal_id,
    unique=True,
    postgresql_where=AnimalPhoto.is_primary.is_(True),
)