"""initialize database

Revision ID: 4508fd1c189d
Revises:
Create Date: 2026-09-25 09:42:56.066212

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "4508fd1c189d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
