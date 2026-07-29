"""drop raw_text from resume_versions

Revision ID: c3f8a1d2e5b4
Revises: 5a442b000d86
Create Date: 2026-07-29 13:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3f8a1d2e5b4"
down_revision: Union[str, Sequence[str], None] = "5a442b000d86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop raw_text column from resume_versions."""
    op.drop_column("resume_versions", "raw_text")


def downgrade() -> None:
    """Add raw_text column back to resume_versions."""
    op.add_column(
        "resume_versions",
        sa.Column("raw_text", sa.Text(), nullable=True),
    )
