"""add_slack_installations_table

Revision ID: 8b146b2fa096
Revises: 60751c4d60fc
Create Date: 2025-11-21 14:47:03.594227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b146b2fa096'
down_revision: Union[str, Sequence[str], None] = '60751c4d60fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create slack_installations table
    op.create_table('slack_installations',
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('bot_user_id', sa.String(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('team_id')
    )
    op.create_index(op.f('ix_slack_installations_team_id'), 'slack_installations', ['team_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop slack_installations table
    op.drop_index(op.f('ix_slack_installations_team_id'), table_name='slack_installations')
    op.drop_table('slack_installations')
