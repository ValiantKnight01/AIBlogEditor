"""Convert status enums to string columns

Revision ID: c411177ade7b
Revises: 58dc630129a8
Create Date: 2025-09-13 07:52:37.876644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c411177ade7b'
down_revision: Union[str, Sequence[str], None] = '58dc630129a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert blog_posts.status from enum to string
    op.alter_column('blog_posts', 'status',
                    type_=sa.String(20),
                    nullable=False,
                    postgresql_using='status::text')
    
    # Convert projects.status from enum to string  
    op.alter_column('projects', 'status',
                    type_=sa.String(20),
                    nullable=False,
                    postgresql_using='status::text')
    
    # Drop enum types if they exist
    op.execute("DROP TYPE IF EXISTS poststatus CASCADE")
    op.execute("DROP TYPE IF EXISTS projectstatus CASCADE")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate enum types
    op.execute("CREATE TYPE poststatus AS ENUM ('draft', 'published')")
    op.execute("CREATE TYPE projectstatus AS ENUM ('draft', 'published')")
    
    # Convert back to enum columns
    op.alter_column('blog_posts', 'status',
                    type_=sa.Enum('draft', 'published', name='poststatus'),
                    nullable=False,
                    postgresql_using='status::poststatus')
    
    op.alter_column('projects', 'status',
                    type_=sa.Enum('draft', 'published', name='projectstatus'),
                    nullable=False,
                    postgresql_using='status::projectstatus')
