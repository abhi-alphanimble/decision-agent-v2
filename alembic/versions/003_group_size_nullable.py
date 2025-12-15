"""Make group_size nullable in channel_configs

Revision ID: 003_group_size_nullable
Revises: 002_zoho_installations_and_team_id
Create Date: 2025-12-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_group_size_nullable'
down_revision: Union[str, Sequence[str], None] = '002_zoho_team'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make group_size column nullable since we now fetch it dynamically from Slack."""
    # Drop the NOT NULL constraint and the check constraint
    op.drop_constraint('check_valid_group_size', 'channel_configs', type_='check')
    op.alter_column('channel_configs', 'group_size',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade() -> None:
    """Revert group_size to NOT NULL."""
    # Make it NOT NULL again
    op.alter_column('channel_configs', 'group_size',
                    existing_type=sa.Integer(),
                    nullable=False)
    # Recreate the check constraint
    op.create_check_constraint('check_valid_group_size', 'channel_configs', 'group_size > 0')
