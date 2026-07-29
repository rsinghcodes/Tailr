"""add raw_extracted column to job_descriptions

Revision ID: e7a3f1b2c5d6
Revises: c3f8a1d2e5b4
Create Date: 2026-07-30 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "e7a3f1b2c5d6"
down_revision: Union[str, Sequence[str], None] = "c3f8a1d2e5b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add raw_extracted JSONB column to job_descriptions."""
    op.add_column(
        "job_descriptions",
        sa.Column("raw_extracted", JSONB(), nullable=True),
    )


def downgrade() -> None:
    """Drop raw_extracted column from job_descriptions."""
    op.drop_column("job_descriptions", "raw_extracted")
