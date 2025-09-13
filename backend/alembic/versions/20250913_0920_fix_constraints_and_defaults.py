"""Fix missing constraints and defaults

Revision ID: dd286aefafa4
Revises: c411177ade7b
Create Date: 2025-09-13 09:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd286aefafa4'
down_revision: Union[str, Sequence[str], None] = 'c411177ade7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing unique constraints and default values."""
    
    # Add unique constraints
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    op.create_unique_constraint('blog_posts_slug_key', 'blog_posts', ['slug'])
    op.create_unique_constraint('projects_slug_key', 'projects', ['slug'])
    op.create_unique_constraint('tags_name_key', 'tags', ['name'])
    op.create_unique_constraint('tags_slug_key', 'tags', ['slug'])
    
    # Add default values for status columns (they should already exist from previous migrations)
    # These are already string type after enum conversion
    
    # Add missing indexes
    op.create_index('ix_blog_posts_published_at', 'blog_posts', ['published_at'])


def downgrade() -> None:
    """Remove added constraints and indexes."""
    
    # Remove indexes
    op.drop_index('ix_blog_posts_published_at', 'blog_posts')
    
    # Remove unique constraints
    op.drop_constraint('tags_slug_key', 'tags', type_='unique')
    op.drop_constraint('tags_name_key', 'tags', type_='unique')
    op.drop_constraint('projects_slug_key', 'projects', type_='unique')
    op.drop_constraint('blog_posts_slug_key', 'blog_posts', type_='unique')
    op.drop_constraint('users_username_key', 'users', type_='unique')
    op.drop_constraint('users_email_key', 'users', type_='unique')