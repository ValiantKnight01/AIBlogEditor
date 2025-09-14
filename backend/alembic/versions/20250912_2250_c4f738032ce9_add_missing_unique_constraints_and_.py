"""Add missing unique constraints and defaults

Revision ID: c4f738032ce9
Revises: 36ddf23bd11d
Create Date: 2025-09-12 22:50:01.434514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f738032ce9'
down_revision: Union[str, Sequence[str], None] = '36ddf23bd11d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraints
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    op.create_unique_constraint('uq_blog_posts_slug', 'blog_posts', ['slug'])
    op.create_unique_constraint('uq_projects_slug', 'projects', ['slug'])
    op.create_unique_constraint('uq_tags_name', 'tags', ['name'])
    op.create_unique_constraint('uq_tags_slug', 'tags', ['slug'])
    
    # Add default values using ALTER COLUMN
    op.alter_column('users', 'is_active', server_default=sa.text('true'))
    op.alter_column('blog_posts', 'view_count', server_default=sa.text('0'))
    op.alter_column('tags', 'post_count', server_default=sa.text('0'))
    op.alter_column('tags', 'project_count', server_default=sa.text('0'))
    op.alter_column('blog_posts', 'status', server_default=sa.text("'draft'"))
    op.alter_column('projects', 'status', server_default=sa.text("'draft'"))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove default values
    op.alter_column('projects', 'status', server_default=None)
    op.alter_column('blog_posts', 'status', server_default=None)
    op.alter_column('tags', 'project_count', server_default=None)
    op.alter_column('tags', 'post_count', server_default=None)
    op.alter_column('blog_posts', 'view_count', server_default=None)
    op.alter_column('users', 'is_active', server_default=None)
    
    # Remove unique constraints
    op.drop_constraint('uq_tags_slug', 'tags', type_='unique')
    op.drop_constraint('uq_tags_name', 'tags', type_='unique')
    op.drop_constraint('uq_projects_slug', 'projects', type_='unique')
    op.drop_constraint('uq_blog_posts_slug', 'blog_posts', type_='unique')
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
