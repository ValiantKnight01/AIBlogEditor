"""Fix missing unique constraints

Revision ID: 58dc630129a8
Revises: 4bd008239ee1
Create Date: 2025-09-13 07:44:54.151556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '58dc630129a8'
down_revision: Union[str, Sequence[str], None] = '4bd008239ee1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - fix missing unique constraints."""
    # This migration fixes any missing unique constraints
    # Most constraints should already exist from initial migration
    pass  # No changes needed - unique constraints were properly added in initial migration


def downgrade() -> None:
    """Downgrade schema."""
    # No changes in upgrade, nothing to downgrade
    pass
