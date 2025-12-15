"""Add zoho_installations table and team_id to decisions

Revision ID: 002_zoho_team
Revises: 001_initial
Create Date: 2025-12-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_zoho_team'
down_revision: Union[str, Sequence[str], None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add zoho_installations table and team_id column to decisions."""
    
    # Create zoho_installations table
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
    op.create_index(op.f('ix_zoho_installations_id'), 'zoho_installations', ['id'], unique=False)
    op.create_index(op.f('ix_zoho_installations_team_id'), 'zoho_installations', ['team_id'], unique=True)
    
    # Add team_id column to decisions table
    op.add_column('decisions', sa.Column('team_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_decisions_team_id'), 'decisions', ['team_id'], unique=False)
    op.create_foreign_key(
        'fk_decisions_team_id', 
        'decisions', 
        'slack_installations', 
        ['team_id'], 
        ['team_id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Remove zoho_installations table and team_id from decisions."""
    
    # Remove team_id from decisions
    op.drop_constraint('fk_decisions_team_id', 'decisions', type_='foreignkey')
    op.drop_index(op.f('ix_decisions_team_id'), table_name='decisions')
    op.drop_column('decisions', 'team_id')
    
    # Drop zoho_installations table
    op.drop_index(op.f('ix_zoho_installations_team_id'), table_name='zoho_installations')
    op.drop_index(op.f('ix_zoho_installations_id'), table_name='zoho_installations')
    op.drop_table('zoho_installations')
