"""alter_resume_versions_latex_path_to_text

Revision ID: 4d9e2a1b8c3f
Revises: 3c8e92a1f4b5
Create Date: 2026-07-25 17:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4d9e2a1b8c3f'
down_revision: Union[str, Sequence[str], None] = '3c8e92a1f4b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'resume_versions',
        'latex_path',
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        'resume_versions',
        'pdf_path',
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'resume_versions',
        'latex_path',
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        'resume_versions',
        'pdf_path',
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
