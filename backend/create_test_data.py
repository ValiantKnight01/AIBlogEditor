#!/usr/bin/env python3
"""
Script to create test data for contract tests.
"""
import sys
import os
sys.path.append('/app/src')
sys.path.append('/app')

from sqlalchemy.orm import Session
from datetime import datetime, date

# Import database connection
from src.database import SessionLocal

# Import services
from src.services.user_service import UserService
from src.services.tag_service import TagService
from src.services.project_service import ProjectService
from src.services.blog_service import BlogPostService

def create_test_data():
    """Create test data."""
    # Get database session
    db = SessionLocal()
    
    try:
        print("Creating test data...")
        
        # Services
        tag_service = TagService()
        project_service = ProjectService()
        blog_service = BlogPostService()
        
        # Get or create test user (should already exist)
        user_service = UserService()
        test_user = user_service.get_user_by_email(db, "test@example.com")
        if not test_user:
            test_user = user_service.create_user(
                db=db,
                email="test@example.com",
                username="testuser",
                password="TestP@ss_w0rd!",
                full_name="Test User",
                bio="A test user for development"
            )
            print(f"Created test user: {test_user.email}")
        else:
            print(f"Using existing test user: {test_user.email}")
        
        # Create test tags
        tags = []
        tag_data = [
            {"name": "React", "color": "#61DAFB", "description": "JavaScript library for building user interfaces"},
            {"name": "Python", "color": "#3776AB", "description": "High-level programming language"},
            {"name": "FastAPI", "color": "#009688", "description": "Modern web framework for building APIs"},
            {"name": "PostgreSQL", "color": "#336791", "description": "Advanced open source relational database"},
            {"name": "Docker", "color": "#2496ED", "description": "Platform for developing, shipping, and running applications"}
        ]
        
        for tag_info in tag_data:
            try:
                existing_tag = tag_service.get_tag_by_name(db, tag_info["name"])
                if not existing_tag:
                    tag = tag_service.create_tag(
                        db=db,
                        name=tag_info["name"],
                        color=tag_info["color"],
                        description=tag_info["description"]
                    )
                    tags.append(tag)
                    print(f"Created tag: {tag.name}")
                else:
                    tags.append(existing_tag)
                    print(f"Using existing tag: {existing_tag.name}")
            except Exception as e:
                print(f"Error creating tag {tag_info['name']}: {e}")
                
        # Create test projects
        projects = []
        project_data = [
            {
                "title": "Awesome Project",
                "description": "A really awesome project showcasing React and Python integration",
                "tech_stack": ["React", "Python", "FastAPI", "PostgreSQL"],
                "github_url": "https://github.com/testuser/awesome-project",
                "live_url": "https://awesome-project.example.com",
                "status": "published",
                "featured": True,
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 6, 1)
            },
            {
                "title": "Personal Blog Platform",
                "description": "A full-stack blog platform with authentication and CMS features",
                "tech_stack": ["FastAPI", "PostgreSQL", "Docker"],
                "github_url": "https://github.com/testuser/blog-platform",
                "live_url": "https://blog-platform.example.com",
                "status": "published",
                "featured": False,
                "start_date": date(2024, 3, 1),
                "end_date": date(2024, 12, 1)
            }
        ]
        
        for project_info in project_data:
            try:
                # Get tag IDs for this project
                tag_ids = []
                for tech in project_info["tech_stack"]:
                    for tag in tags:
                        if tag.name == tech:
                            tag_ids.append(str(tag.id))
                            break
                
                project = project_service.create_project(
                    db=db,
                    user_id=test_user.id,
                    title=project_info["title"],
                    description=project_info["description"],
                    tech_stack=project_info["tech_stack"],
                    github_url=project_info["github_url"],
                    live_url=project_info["live_url"],
                    status=project_info["status"],
                    featured=project_info["featured"],
                    start_date=project_info["start_date"],
                    end_date=project_info["end_date"],
                    tag_ids=tag_ids
                )
                projects.append(project)
                print(f"Created project: {project.title} (slug: {project.slug})")
            except Exception as e:
                print(f"Error creating project {project_info['title']}: {e}")
        
        # Create test blog posts
        blog_data = [
            {
                "title": "Getting Started with FastAPI",
                "content": "This is a comprehensive guide to getting started with FastAPI...",
                "excerpt": "Learn how to build modern web APIs with FastAPI",
                "status": "published",
                "featured": True
            },
            {
                "title": "Building React Components",
                "content": "In this post, we'll explore how to build reusable React components...",
                "excerpt": "Master the art of component-driven development",
                "status": "published",
                "featured": False
            }
        ]
        
        for blog_info in blog_data:
            try:
                # Get some tag IDs
                tag_ids = [str(tags[0].id), str(tags[1].id)] if len(tags) >= 2 else []
                
                blog_post = blog_service.create_post(
                    db=db,
                    user_id=test_user.id,
                    title=blog_info["title"],
                    content=blog_info["content"],
                    excerpt=blog_info["excerpt"],
                    status=blog_info["status"],
                    featured=blog_info["featured"],
                    tag_ids=tag_ids
                )
                print(f"Created blog post: {blog_post.title} (slug: {blog_post.slug})")
            except Exception as e:
                print(f"Error creating blog post {blog_info['title']}: {e}")
        
        print("Test data creation completed!")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()