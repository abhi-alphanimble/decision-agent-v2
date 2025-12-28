"""Zoho-first schema - Zoho as primary, Slack as dependent

Revision ID: 004_zoho_first
Revises: 003_consolidate_ai_tables
Create Date: 2025-01-XX

This migration restructures the database to support Zoho-first onboarding:
- ZohoInstallation is now the parent table (uses zoho_org_id as primary key)
- SlackInstallation now has zoho_org_id FK to ZohoInstallation
- Decision now has zoho_org_id FK to ZohoInstallation
- OrganizationAILimits now has zoho_org_id FK to ZohoInstallation

IMPORTANT: This migration requires a fresh database. Run `alembic downgrade base` 
then `alembic upgrade head` or drop and recreate the database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_zoho_first'
down_revision: Union[str, Sequence[str], None] = '003_consolidate_ai_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Restructure schema for Zoho-first onboarding.
    
    WARNING: This is a destructive migration that drops and recreates tables.
    Make sure to backup data before running if needed.
    """
    
    # Drop existing tables in reverse dependency order
    op.drop_table('organization_ai_limits')
    op.drop_table('zoho_installations')
    op.drop_table('votes')
    op.drop_table('decisions')
    op.drop_table('config_change_logs')
    op.drop_table('channel_configs')
    op.drop_table('slack_installations')
    
    # Create zoho_installations table FIRST (now the parent table)
    op.create_table('zoho_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('zoho_org_id', sa.String(100), nullable=False),
        sa.Column('zoho_domain', sa.String(50), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.Column('installed_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zoho_org_id', name='uq_zoho_installations_zoho_org_id')
    )
    op.create_index(op.f('ix_zoho_installations_id'), 'zoho_installations', ['id'], unique=False)
    op.create_index(op.f('ix_zoho_installations_zoho_org_id'), 'zoho_installations', ['zoho_org_id'], unique=True)
    
    # Create slack_installations table (now depends on zoho_installations)
    op.create_table('slack_installations',
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('bot_user_id', sa.String(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.Column('zoho_org_id', sa.String(100), nullable=False),
        sa.ForeignKeyConstraint(['zoho_org_id'], ['zoho_installations.zoho_org_id'], name='fk_slack_zoho_org_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('team_id')
    )
    op.create_index(op.f('ix_slack_installations_team_id'), 'slack_installations', ['team_id'], unique=False)
    op.create_index(op.f('ix_slack_installations_zoho_org_id'), 'slack_installations', ['zoho_org_id'], unique=False)
    
    # Create decisions table (references both team_id and zoho_org_id)
    op.create_table('decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('proposer_phone', sa.String(), nullable=False),
        sa.Column('proposer_name', sa.String(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('group_size_at_creation', sa.Integer(), nullable=False),
        sa.Column('approval_threshold', sa.Integer(), nullable=False),
        sa.Column('approval_count', sa.Integer(), nullable=False),
        sa.Column('rejection_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('zoho_org_id', sa.String(100), nullable=True),
        sa.Column('zoho_synced', sa.Boolean(), nullable=False, server_default='false'),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'expired')", name='check_valid_status'),
        sa.CheckConstraint('approval_count >= 0', name='check_approval_count_positive'),
        sa.CheckConstraint('approval_threshold > 0', name='check_threshold_positive'),
        sa.CheckConstraint('group_size_at_creation > 0', name='check_group_size_positive'),
        sa.CheckConstraint('rejection_count >= 0', name='check_rejection_count_positive'),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], name='fk_decisions_team_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['zoho_org_id'], ['zoho_installations.zoho_org_id'], name='fk_decisions_zoho_org_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decisions_channel_id'), 'decisions', ['channel_id'], unique=False)
    op.create_index(op.f('ix_decisions_id'), 'decisions', ['id'], unique=False)
    op.create_index(op.f('ix_decisions_proposer_phone'), 'decisions', ['proposer_phone'], unique=False)
    op.create_index(op.f('ix_decisions_team_id'), 'decisions', ['team_id'], unique=False)
    op.create_index(op.f('ix_decisions_zoho_org_id'), 'decisions', ['zoho_org_id'], unique=False)
    
    # Create votes table
    op.create_table('votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.Integer(), nullable=False),
        sa.Column('voter_phone', sa.String(), nullable=False),
        sa.Column('voter_name', sa.String(), nullable=False),
        sa.Column('vote_type', sa.String(), nullable=False),
        sa.Column('voted_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("vote_type IN ('approve', 'reject')", name='check_valid_vote_type'),
        sa.ForeignKeyConstraint(['decision_id'], ['decisions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('decision_id', 'voter_phone', name='unique_voter_per_decision')
    )
    op.create_index(op.f('ix_votes_decision_id'), 'votes', ['decision_id'], unique=False)
    op.create_index(op.f('ix_votes_id'), 'votes', ['id'], unique=False)
    op.create_index(op.f('ix_votes_voter_phone'), 'votes', ['voter_phone'], unique=False)
    
    # Create channel_configs table
    op.create_table('channel_configs',
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('approval_percentage', sa.Integer(), nullable=False),
        sa.Column('group_size', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.CheckConstraint('approval_percentage > 0 AND approval_percentage <= 100', name='check_valid_percentage'),
        sa.PrimaryKeyConstraint('channel_id')
    )
    op.create_index(op.f('ix_channel_configs_channel_id'), 'channel_configs', ['channel_id'], unique=False)
    
    # Create config_change_logs table
    op.create_table('config_change_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('setting_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.Integer(), nullable=False),
        sa.Column('new_value', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.String(), nullable=False),
        sa.Column('changed_by_name', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("setting_name = 'approval_percentage'", name='check_valid_setting_name'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_change_logs_channel_id'), 'config_change_logs', ['channel_id'], unique=False)
    op.create_index(op.f('ix_config_change_logs_id'), 'config_change_logs', ['id'], unique=False)
    
    # Create organization_ai_limits table (uses zoho_org_id now)
    op.create_table('organization_ai_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('zoho_org_id', sa.String(100), nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),
        sa.Column('monthly_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('command_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint('monthly_limit > 0', name='check_monthly_limit_positive'),
        sa.CheckConstraint('command_count >= 0', name='check_command_count_non_negative'),
        sa.ForeignKeyConstraint(['zoho_org_id'], ['zoho_installations.zoho_org_id'], name='fk_ai_limits_zoho_org_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('zoho_org_id', 'month_year', name='unique_org_month_limits')
    )
    op.create_index(op.f('ix_organization_ai_limits_id'), 'organization_ai_limits', ['id'], unique=False)
    op.create_index('ix_ai_limits_org_month', 'organization_ai_limits', ['zoho_org_id', 'month_year'], unique=False)


def downgrade() -> None:
    """
    Revert to old schema (Slack-first).
    
    WARNING: This will drop all data.
    """
    # Drop all tables
    op.drop_table('organization_ai_limits')
    op.drop_table('config_change_logs')
    op.drop_table('channel_configs')
    op.drop_table('votes')
    op.drop_table('decisions')
    op.drop_table('slack_installations')
    op.drop_table('zoho_installations')
    
    # Recreate old schema (slack_installations first)
    op.create_table('slack_installations',
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('bot_user_id', sa.String(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('team_id')
    )
    op.create_index(op.f('ix_slack_installations_team_id'), 'slack_installations', ['team_id'], unique=False)
    
    # Recreate zoho_installations with team_id FK
    op.create_table('zoho_installations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(50), nullable=False),
        sa.Column('zoho_org_id', sa.String(100), nullable=True),
        sa.Column('zoho_domain', sa.String(50), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.Column('installed_by', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id', name='uq_zoho_installations_team_id')
    )
    
    # Recreate decisions with team_id FK only
    op.create_table('decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('proposer_phone', sa.String(), nullable=False),
        sa.Column('proposer_name', sa.String(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('group_size_at_creation', sa.Integer(), nullable=False),
        sa.Column('approval_threshold', sa.Integer(), nullable=False),
        sa.Column('approval_count', sa.Integer(), nullable=False),
        sa.Column('rejection_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('team_id', sa.String(), nullable=True),
        sa.Column('zoho_synced', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate other tables with old schema
    op.create_table('votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('decision_id', sa.Integer(), nullable=False),
        sa.Column('voter_phone', sa.String(), nullable=False),
        sa.Column('voter_name', sa.String(), nullable=False),
        sa.Column('vote_type', sa.String(), nullable=False),
        sa.Column('voted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['decision_id'], ['decisions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('channel_configs',
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('approval_percentage', sa.Integer(), nullable=False),
        sa.Column('group_size', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('channel_id')
    )
    
    op.create_table('config_change_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('setting_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.Integer(), nullable=False),
        sa.Column('new_value', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.String(), nullable=False),
        sa.Column('changed_by_name', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('organization_ai_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.String(50), nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),
        sa.Column('monthly_limit', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('command_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['slack_installations.team_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
