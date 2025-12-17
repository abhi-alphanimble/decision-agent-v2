"""Remove auto_close_hours from channel_configs and update config_change_logs constraint

Revision ID: 004_remove_auto_close
Revises: 003_group_size_nullable
Create Date: 2025-12-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_remove_auto_close'
down_revision: Union[str, Sequence[str], None] = '003_group_size_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove auto_close_hours column and related constraints."""
    # Drop the check constraint for auto_close_hours
    op.drop_constraint('check_valid_hours', 'channel_configs', type_='check')
    
    # Drop the auto_close_hours column
    op.drop_column('channel_configs', 'auto_close_hours')
    
    # Update config_change_logs constraint to only allow 'approval_percentage'
    # First drop the old constraint
    op.drop_constraint('check_valid_setting_name', 'config_change_logs', type_='check')
    
    # Create new constraint without auto_close_hours
    op.create_check_constraint(
        'check_valid_setting_name',
        'config_change_logs',
        "setting_name = 'approval_percentage'"
    )


def downgrade() -> None:
    """Re-add auto_close_hours column and constraints."""
    # Add the column back
    op.add_column(
        'channel_configs',
        sa.Column('auto_close_hours', sa.Integer(), nullable=False, server_default='48')
    )
    
    # Re-create the check constraint
    op.create_check_constraint('check_valid_hours', 'channel_configs', 'auto_close_hours > 0')
    
    # Update config_change_logs constraint to include auto_close_hours again
    op.drop_constraint('check_valid_setting_name', 'config_change_logs', type_='check')
    op.create_check_constraint(
        'check_valid_setting_name',
        'config_change_logs',
        "setting_name IN ('approval_percentage', 'auto_close_hours')"
    )
