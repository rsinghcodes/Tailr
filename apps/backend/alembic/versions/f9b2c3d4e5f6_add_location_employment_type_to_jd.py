"""add location and employment_type to job_descriptions

Revision ID: f9b2c3d4e5f6
Revises: e7a3f1b2c5d6
Create Date: 2026-07-30 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e7a3f1b2c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_descriptions",
        sa.Column("location", sa.String(100), nullable=True),
    )
    op.add_column(
        "job_descriptions",
        sa.Column("employment_type", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_descriptions", "employment_type")
    op.drop_column("job_descriptions", "location")
