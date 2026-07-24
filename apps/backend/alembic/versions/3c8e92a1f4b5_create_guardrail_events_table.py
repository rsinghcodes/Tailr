"""create_guardrail_events_table

Revision ID: 3c8e92a1f4b5
Revises: 28a71dd2aea7
Create Date: 2026-07-21 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c8e92a1f4b5'
down_revision: Union[str, Sequence[str], None] = '28a71dd2aea7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'guardrail_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('validator_name', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('violation_code', sa.String(length=100), nullable=True),
        sa.Column('repaired', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_guardrail_events'))
    )
    op.create_index(op.f('ix_guardrail_events_workflow_id'), 'guardrail_events', ['workflow_id'], unique=False)
    op.create_index(op.f('ix_guardrail_events_validator_name'), 'guardrail_events', ['validator_name'], unique=False)
    op.create_index(op.f('ix_guardrail_events_severity'), 'guardrail_events', ['severity'], unique=False)
    op.create_index(op.f('ix_guardrail_events_created_at'), 'guardrail_events', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_guardrail_events_created_at'), table_name='guardrail_events')
    op.drop_index(op.f('ix_guardrail_events_severity'), table_name='guardrail_events')
    op.drop_index(op.f('ix_guardrail_events_validator_name'), table_name='guardrail_events')
    op.drop_index(op.f('ix_guardrail_events_workflow_id'), table_name='guardrail_events')
    op.drop_table('guardrail_events')
