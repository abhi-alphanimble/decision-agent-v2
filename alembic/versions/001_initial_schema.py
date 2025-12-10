"""Initial schema - all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""
    
    # decisions table
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
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'expired')", name='check_valid_status'),
        sa.CheckConstraint('approval_count >= 0', name='check_approval_count_positive'),
        sa.CheckConstraint('approval_threshold > 0', name='check_threshold_positive'),
        sa.CheckConstraint('group_size_at_creation > 0', name='check_group_size_positive'),
        sa.CheckConstraint('rejection_count >= 0', name='check_rejection_count_positive'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decisions_channel_id'), 'decisions', ['channel_id'], unique=False)
    op.create_index(op.f('ix_decisions_id'), 'decisions', ['id'], unique=False)
    op.create_index(op.f('ix_decisions_proposer_phone'), 'decisions', ['proposer_phone'], unique=False)
    
    # votes table (without is_anonymous column)
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
    
    # slack_installations table
    op.create_table('slack_installations',
        sa.Column('team_id', sa.String(), nullable=False),
        sa.Column('team_name', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('bot_user_id', sa.String(), nullable=False),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('team_id')
    )
    op.create_index(op.f('ix_slack_installations_team_id'), 'slack_installations', ['team_id'], unique=False)
    
    # channel_configs table
    op.create_table('channel_configs',
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('approval_percentage', sa.Integer(), nullable=False),
        sa.Column('auto_close_hours', sa.Integer(), nullable=False),
        sa.Column('group_size', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.CheckConstraint('approval_percentage > 0 AND approval_percentage <= 100', name='check_valid_percentage'),
        sa.CheckConstraint('auto_close_hours > 0', name='check_valid_hours'),
        sa.CheckConstraint('group_size > 0', name='check_valid_group_size'),
        sa.PrimaryKeyConstraint('channel_id')
    )
    op.create_index(op.f('ix_channel_configs_channel_id'), 'channel_configs', ['channel_id'], unique=False)
    
    # config_change_logs table
    op.create_table('config_change_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('setting_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.Integer(), nullable=False),
        sa.Column('new_value', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.String(), nullable=False),
        sa.Column('changed_by_name', sa.String(), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("setting_name IN ('approval_percentage', 'auto_close_hours', 'group_size')", name='check_valid_setting_name'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_config_change_logs_channel_id'), 'config_change_logs', ['channel_id'], unique=False)
    op.create_index(op.f('ix_config_change_logs_id'), 'config_change_logs', ['id'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_config_change_logs_id'), table_name='config_change_logs')
    op.drop_index(op.f('ix_config_change_logs_channel_id'), table_name='config_change_logs')
    op.drop_table('config_change_logs')
    
    op.drop_index(op.f('ix_channel_configs_channel_id'), table_name='channel_configs')
    op.drop_table('channel_configs')
    
    op.drop_index(op.f('ix_slack_installations_team_id'), table_name='slack_installations')
    op.drop_table('slack_installations')
    
    op.drop_index(op.f('ix_votes_voter_phone'), table_name='votes')
    op.drop_index(op.f('ix_votes_id'), table_name='votes')
    op.drop_index(op.f('ix_votes_decision_id'), table_name='votes')
    op.drop_table('votes')
    
    op.drop_index(op.f('ix_decisions_proposer_phone'), table_name='decisions')
    op.drop_index(op.f('ix_decisions_id'), table_name='decisions')
    op.drop_index(op.f('ix_decisions_channel_id'), table_name='decisions')
    op.drop_table('decisions')
