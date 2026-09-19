import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.enums import AccountStatus, UserRole
from backend.app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
    )

    organisation_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("rescue_organisations.id"),
        nullable=True,
    )

    account_status: Mapped[AccountStatus] = mapped_column(
        SAEnum(AccountStatus, name="account_status"),
        nullable=False,
        default=AccountStatus.ACTIVE,
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
            "(role = 'ADOPTER' AND organisation_id IS NULL) "
            "OR (role = 'RESCUE_STAFF' AND organisation_id IS NOT NULL)",
            name="ck_users_role_organisation",
        ),
    )