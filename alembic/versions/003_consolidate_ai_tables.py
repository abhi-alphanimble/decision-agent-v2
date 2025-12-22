"""Consolidate AI config and usage tables into one

Revision ID: 003_consolidate_ai_tables
Revises: 002_add_ai_limits
Create Date: 2025-12-22

This migration:
1. Creates a new consolidated 'organization_ai_limits' table
2. Migrates data from both old tables
3. Drops the old tables
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_consolidate_ai_tables'
down_revision: Union[str, None] = '002_add_ai_limits'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if new table already exists (might be created by SQLAlchemy auto-create)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # 1. Create new consolidated table (if not exists)
    if 'organization_ai_limits' not in existing_tables:
        op.create_table(
            'organization_ai_limits',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.String(50), nullable=False),
            sa.Column('month_year', sa.String(7), nullable=False),  # Format: "YYYY-MM"
            sa.Column('monthly_limit', sa.Integer(), nullable=False, server_default='100'),
            sa.Column('command_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('last_used_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
            sa.UniqueConstraint('team_id', 'month_year', name='unique_team_month_limits'),
            sa.CheckConstraint('monthly_limit > 0', name='check_monthly_limit_positive'),
            sa.CheckConstraint('command_count >= 0', name='check_command_count_non_negative'),
        )
        op.create_index('ix_organization_ai_limits_id', 'organization_ai_limits', ['id'])
        op.create_index('ix_organization_ai_limits_team_id', 'organization_ai_limits', ['team_id'])
        op.create_index('ix_organization_ai_limits_month_year', 'organization_ai_limits', ['month_year'])
        op.create_index('ix_ai_limits_team_month', 'organization_ai_limits', ['team_id', 'month_year'])

    # 2. Migrate data from old tables (if they exist and new table was just created)
    if 'organization_ai_usage' in existing_tables and 'organization_ai_configs' in existing_tables:
        # Join usage with config to get the limit, or use default 100
        op.execute("""
            INSERT INTO organization_ai_limits (team_id, month_year, monthly_limit, command_count, last_used_at)
            SELECT 
                u.team_id,
                u.month_year,
                COALESCE(c.monthly_ai_limit, 100) as monthly_limit,
                u.command_count,
                u.last_used_at
            FROM organization_ai_usage u
            LEFT JOIN organization_ai_configs c ON u.team_id = c.team_id
            ON CONFLICT (team_id, month_year) DO NOTHING
        """)

    # 3. Drop old tables (if they exist)
    if 'organization_ai_usage' in existing_tables:
        try:
            op.drop_index('ix_ai_usage_team_month', table_name='organization_ai_usage')
        except Exception:
            pass
        try:
            op.drop_index('ix_organization_ai_usage_month_year', table_name='organization_ai_usage')
        except Exception:
            pass
        try:
            op.drop_index('ix_organization_ai_usage_team_id', table_name='organization_ai_usage')
        except Exception:
            pass
        try:
            op.drop_index('ix_organization_ai_usage_id', table_name='organization_ai_usage')
        except Exception:
            pass
        op.drop_table('organization_ai_usage')

    if 'organization_ai_configs' in existing_tables:
        try:
            op.drop_index('ix_organization_ai_configs_team_id', table_name='organization_ai_configs')
        except Exception:
            pass
        try:
            op.drop_index('ix_organization_ai_configs_id', table_name='organization_ai_configs')
        except Exception:
            pass
        op.drop_table('organization_ai_configs')


def downgrade() -> None:
    # Recreate old tables
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

    op.create_table(
        'organization_ai_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(50), nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),
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

    # Migrate data back
    op.execute("""
        INSERT INTO organization_ai_usage (team_id, month_year, command_count, last_used_at)
        SELECT team_id, month_year, command_count, last_used_at
        FROM organization_ai_limits
    """)
    
    op.execute("""
        INSERT INTO organization_ai_configs (team_id, monthly_ai_limit)
        SELECT DISTINCT team_id, monthly_limit
        FROM organization_ai_limits
    """)

    # Drop new table
    op.drop_index('ix_ai_limits_team_month', table_name='organization_ai_limits')
    op.drop_index('ix_organization_ai_limits_month_year', table_name='organization_ai_limits')
    op.drop_index('ix_organization_ai_limits_team_id', table_name='organization_ai_limits')
    op.drop_index('ix_organization_ai_limits_id', table_name='organization_ai_limits')
    op.drop_table('organization_ai_limits')
