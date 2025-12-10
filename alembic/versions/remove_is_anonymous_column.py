"""Remove is_anonymous column from votes table

Revision ID: remove_is_anonymous
Revises: 88f915c66504
Create Date: 2025-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_is_anonymous'
down_revision: Union[str, None] = '88f915c66504'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove is_anonymous column from votes table."""
    op.drop_column('votes', 'is_anonymous')


def downgrade() -> None:
    """Add is_anonymous column back to votes table."""
    op.add_column('votes', sa.Column('is_anonymous', sa.Boolean(), nullable=False, server_default='false'))
