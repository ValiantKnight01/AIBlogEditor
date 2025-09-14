"""Add server defaults for status columns

Revision ID: da8b4ab0c5ae
Revises: dd286aefafa4
Create Date: 2025-09-13 10:37:01.338661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da8b4ab0c5ae'
down_revision: Union[str, Sequence[str], None] = 'dd286aefafa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add server defaults for status columns
    op.execute("ALTER TABLE blog_posts ALTER COLUMN status SET DEFAULT 'draft';")
    op.execute("ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'draft';")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove server defaults for status columns
    op.execute("ALTER TABLE blog_posts ALTER COLUMN status DROP DEFAULT;")
    op.execute("ALTER TABLE projects ALTER COLUMN status DROP DEFAULT;")
