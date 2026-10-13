"""Enforce canonical user email uniqueness

Revision ID: 6c48bc6e88db
Revises: 72438f37f02d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6c48bc6e88db"
down_revision: Union[str, Sequence[str], None] = "72438f37f02d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Normalize user emails and enforce canonical uniqueness."""
    connection = op.get_bind()

    collisions = connection.execute(
        sa.text(
            """
            SELECT lower(trim(email)) AS canonical_email, count(*) AS email_count
            FROM users
            GROUP BY lower(trim(email))
            HAVING count(*) > 1
            ORDER BY canonical_email
            LIMIT 10
            """
        )
    ).all()

    if collisions:
        examples = ", ".join(
            f"{row.canonical_email!r} ({row.email_count} accounts)"
            for row in collisions
        )
        raise RuntimeError(
            "Cannot normalize user emails because canonical email collisions "
            f"exist. Resolve these accounts before retrying the migration: {examples}"
        )

    connection.execute(
        sa.text("UPDATE users SET email = lower(trim(email))")
    )

    op.drop_constraint("uq_users_email", "users", type_="unique")

    op.create_index(
        "uq_users_email_canonical",
        "users",
        [sa.text("lower(trim(email))")],
        unique=True,
    )


def downgrade() -> None:
    """Restore exact-match uniqueness for user emails."""
    op.drop_index("uq_users_email_canonical", table_name="users")

    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )
