"""Add organization AI config and usage tables

Revision ID: 002_add_ai_limits
Revises: 001_initial
Create Date: 2025-12-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_ai_limits'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organization_ai_configs table
    op.create_table(
        'organization_ai_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(50), nullable=False),
        sa.Column('monthly_ai_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
        sa.CheckConstraint('monthly_ai_limit > 0', name='check_ai_limit_positive'),
    )
    op.create_index('ix_organization_ai_configs_id', 'organization_ai_configs', ['id'])
    op.create_index('ix_organization_ai_configs_team_id', 'organization_ai_configs', ['team_id'], unique=True)

    # Create organization_ai_usage table
    op.create_table(
        'organization_ai_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(50), nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),  # Format: "YYYY-MM"
        sa.Column('command_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('team_id', 'month_year', name='unique_team_month_usage'),
        sa.CheckConstraint('command_count >= 0', name='check_command_count_non_negative'),
    )
    op.create_index('ix_organization_ai_usage_id', 'organization_ai_usage', ['id'])
    op.create_index('ix_organization_ai_usage_team_id', 'organization_ai_usage', ['team_id'])
    op.create_index('ix_organization_ai_usage_month_year', 'organization_ai_usage', ['month_year'])
    op.create_index('ix_ai_usage_team_month', 'organization_ai_usage', ['team_id', 'month_year'])


def downgrade() -> None:
    # Drop organization_ai_usage table
    op.drop_index('ix_ai_usage_team_month', table_name='organization_ai_usage')
    op.drop_index('ix_organization_ai_usage_month_year', table_name='organization_ai_usage')
    op.drop_index('ix_organization_ai_usage_team_id', table_name='organization_ai_usage')
    op.drop_index('ix_organization_ai_usage_id', table_name='organization_ai_usage')
    op.drop_table('organization_ai_usage')

    # Drop organization_ai_configs table
    op.drop_index('ix_organization_ai_configs_team_id', table_name='organization_ai_configs')
    op.drop_index('ix_organization_ai_configs_id', table_name='organization_ai_configs')
    op.drop_table('organization_ai_configs')
