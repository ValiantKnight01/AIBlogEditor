#!/usr/bin/env python3
"""
Simple script to create test data for contract tests.
"""
import sys
import os
sys.path.append('/app/src')

from sqlalchemy import create_engine, text
from datetime import date
import uuid

# Database connection
database_url = os.getenv('DATABASE_URL', 'postgresql://blog_user:blog_password@db:5432/blog_db')
engine = create_engine(database_url)

def create_test_data():
    """Create test data directly with SQL."""
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            print("Creating test data...")
            
            # Get test user ID
            result = conn.execute(text("SELECT id FROM users WHERE email = 'test@example.com'"))
            user_row = result.fetchone()
            if not user_row:
                print("Test user not found!")
                return
            
            user_id = user_row[0]
            print(f"Using test user ID: {user_id}")
            
            # Create tags
            tag_data = [
                ('react', 'React', '#61DAFB', 'JavaScript library for building user interfaces'),
                ('python', 'Python', '#3776AB', 'High-level programming language'),
                ('fastapi', 'FastAPI', '#009688', 'Modern web framework for building APIs'),
                ('postgresql', 'PostgreSQL', '#336791', 'Advanced open source relational database'),
                ('docker', 'Docker', '#2496ED', 'Platform for developing, shipping, and running applications')
            ]
            
            tag_ids = {}
            for slug, name, color, desc in tag_data:
                tag_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO tags (id, name, slug, color, description, created_at)
                    VALUES (:id, :name, :slug, :color, :desc, NOW())
                    ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
                """), {
                    'id': tag_id,
                    'name': name,
                    'slug': slug,
                    'color': color,
                    'desc': desc
                })
                tag_ids[slug] = tag_id
                print(f"Created/updated tag: {name}")
            
            # Create projects
            project_data = [
                {
                    'title': 'Awesome Project',
                    'slug': 'awesome-project-slug',
                    'description': 'A really awesome project showcasing React and Python integration',
                    'tech_stack': '["React", "Python", "FastAPI", "PostgreSQL"]',
                    'github_url': 'https://github.com/testuser/awesome-project',
                    'project_url': 'https://awesome-project.example.com',
                    'status': 'published',
                    'start_date': '2024-01-01',
                    'end_date': '2024-06-01'
                },
                {
                    'title': 'Personal Blog Platform',
                    'slug': 'personal-blog-platform',
                    'description': 'A full-stack blog platform with authentication and CMS features',
                    'tech_stack': '["FastAPI", "PostgreSQL", "Docker"]',
                    'github_url': 'https://github.com/testuser/blog-platform',
                    'project_url': 'https://blog-platform.example.com',
                    'status': 'published',
                    'start_date': '2024-03-01',
                    'end_date': '2024-12-01'
                }
            ]
            
            for project in project_data:
                project_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO projects (id, title, slug, description, tech_stack, 
                                        github_url, project_url, status, start_date, end_date,
                                        creator_id, created_at, updated_at)
                    VALUES (:id, :title, :slug, :desc, :tech_stack, :github_url, :project_url,
                            :status, :start_date, :end_date, :creator_id, NOW(), NOW())
                    ON CONFLICT (slug) DO UPDATE SET title = EXCLUDED.title
                """), {
                    'id': project_id,
                    'title': project['title'],
                    'slug': project['slug'],
                    'desc': project['description'],
                    'tech_stack': project['tech_stack'],
                    'github_url': project['github_url'],
                    'project_url': project['project_url'],
                    'status': project['status'],
                    'start_date': project['start_date'],
                    'end_date': project['end_date'],
                    'creator_id': user_id
                })
                print(f"Created project: {project['title']}")
            
            # Create blog posts
            blog_data = [
                {
                    'title': 'Getting Started with FastAPI',
                    'slug': 'getting-started-with-fastapi',
                    'content': 'This is a comprehensive guide to getting started with FastAPI. FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.',
                    'excerpt': 'Learn how to build modern web APIs with FastAPI',
                    'status': 'published'
                },
                {
                    'title': 'Building React Components',
                    'slug': 'building-react-components',
                    'content': 'In this post, we will explore how to build reusable React components. Component-driven development is a powerful paradigm that helps create maintainable and scalable applications.',
                    'excerpt': 'Master the art of component-driven development',
                    'status': 'published'
                }
            ]
            
            for blog in blog_data:
                blog_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO blog_posts (id, title, slug, content, excerpt, status,
                                          author_id, created_at, updated_at)
                    VALUES (:id, :title, :slug, :content, :excerpt, :status,
                            :author_id, NOW(), NOW())
                    ON CONFLICT (slug) DO UPDATE SET title = EXCLUDED.title
                """), {
                    'id': blog_id,
                    'title': blog['title'],
                    'slug': blog['slug'],
                    'content': blog['content'],
                    'excerpt': blog['excerpt'],
                    'status': blog['status'],
                    'author_id': user_id
                })
                print(f"Created blog post: {blog['title']}")
            
            # Commit transaction
            trans.commit()
            print("Test data creation completed!")
            
        except Exception as e:
            trans.rollback()
            print(f"Error creating test data: {e}")
            raise

if __name__ == "__main__":
    create_test_data()