"""Initial schema with users, blog_posts, projects, tags, and associations

Revision ID: 36ddf23bd11d
Revises: 
Create Date: 2025-09-12 17:07:58.767867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36ddf23bd11d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('slug', sa.String(60), nullable=False, unique=True, index=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('post_count', sa.Integer(), nullable=False, default=0),
        sa.Column('project_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create blog_posts table
    op.create_table(
        'blog_posts',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(250), nullable=False, unique=True, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('excerpt', sa.String(300), nullable=True),
        sa.Column('status', sa.Enum('draft', 'published', name='poststatus'), nullable=False, default='draft', index=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('author_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('featured_image_url', sa.String(500), nullable=True),
        sa.Column('meta_title', sa.String(200), nullable=True),
        sa.Column('meta_description', sa.String(300), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(120), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('short_description', sa.String(200), nullable=True),
        sa.Column('status', sa.Enum('draft', 'published', name='projectstatus'), nullable=False, default='draft', index=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('creator_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('project_url', sa.String(500), nullable=True),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('tech_stack', sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create blog_post_tags junction table
    op.create_table(
        'blog_post_tags',
        sa.Column('blog_post_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create project_tags junction table
    op.create_table(
        'project_tags',
        sa.Column('project_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'))
    )

    # Create indexes for performance
    op.create_index('ix_blog_posts_published_at', 'blog_posts', ['published_at'])
    op.create_index('ix_blog_posts_status_published_at', 'blog_posts', ['status', 'published_at'])
    op.create_index('ix_projects_created_at', 'projects', ['created_at'])
    op.create_index('ix_projects_status_created_at', 'projects', ['status', 'created_at'])
    op.create_index('ix_blog_post_tags_blog_post_id', 'blog_post_tags', ['blog_post_id'])
    op.create_index('ix_blog_post_tags_tag_id', 'blog_post_tags', ['tag_id'])
    op.create_index('ix_project_tags_project_id', 'project_tags', ['project_id'])
    op.create_index('ix_project_tags_tag_id', 'project_tags', ['tag_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_project_tags_tag_id')
    op.drop_index('ix_project_tags_project_id')
    op.drop_index('ix_blog_post_tags_tag_id')
    op.drop_index('ix_blog_post_tags_blog_post_id')
    op.drop_index('ix_projects_status_created_at')
    op.drop_index('ix_projects_created_at')
    op.drop_index('ix_blog_posts_status_published_at')
    op.drop_index('ix_blog_posts_published_at')
    
    # Drop tables in reverse order
    op.drop_table('project_tags')
    op.drop_table('blog_post_tags')
    op.drop_table('projects')
    op.drop_table('blog_posts')
    op.drop_table('tags')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS projectstatus')
    op.execute('DROP TYPE IF EXISTS poststatus')
