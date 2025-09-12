"""
Slug generation utility.
Provides functions to generate URL-friendly slugs from titles and handle duplicates.
"""

import re
import unicodedata
from typing import Optional, Callable
from sqlalchemy.orm import Session


class SlugUtils:
    """Utility class for generating and managing URL slugs."""
    
    @staticmethod
    def create_slug(text: str, max_length: int = 100) -> str:
        """
        Create a URL-friendly slug from text.
        
        Args:
            text: The text to convert to a slug
            max_length: Maximum length of the generated slug
            
        Returns:
            A clean URL-friendly slug
        """
        if not text:
            return ""
        
        # Convert to lowercase and normalize unicode
        slug = text.lower().strip()
        slug = unicodedata.normalize('NFKD', slug)
        
        # Remove accents and special characters
        slug = slug.encode('ascii', 'ignore').decode('ascii')
        
        # Replace special characters and spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        
        # Truncate to max length while preserving word boundaries
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip('-')
            
            # Try to cut at word boundary
            last_dash = slug.rfind('-')
            if last_dash > max_length * 0.7:  # Only if we're not cutting too much
                slug = slug[:last_dash]
        
        # Ensure we have a valid slug
        if not slug:
            return "untitled"
        
        return slug
    
    @staticmethod
    def ensure_unique_slug(
        db: Session,
        base_slug: str,
        check_existence: Callable[[Session, str], bool],
        max_attempts: int = 100
    ) -> str:
        """
        Ensure a slug is unique by appending numbers if necessary.
        
        Args:
            db: Database session
            base_slug: The base slug to check
            check_existence: Function that takes (session, slug) and returns True if slug exists
            max_attempts: Maximum number of attempts to find a unique slug
            
        Returns:
            A unique slug
        """
        if not check_existence(db, base_slug):
            return base_slug
        
        for i in range(2, max_attempts + 2):
            candidate_slug = f"{base_slug}-{i}"
            if not check_existence(db, candidate_slug):
                return candidate_slug
        
        # If we can't find a unique slug after max_attempts, use timestamp
        import time
        timestamp_slug = f"{base_slug}-{int(time.time())}"
        return timestamp_slug
    
    @staticmethod
    def validate_slug(slug: str) -> bool:
        """
        Validate if a slug meets the requirements.
        
        Args:
            slug: The slug to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not slug:
            return False
        
        # Check length
        if len(slug) > 100 or len(slug) < 1:
            return False
        
        # Check format (only lowercase letters, numbers, and hyphens)
        if not re.match(r'^[a-z0-9-]+$', slug):
            return False
        
        # Cannot start or end with hyphen
        if slug.startswith('-') or slug.endswith('-'):
            return False
        
        # Cannot have consecutive hyphens
        if '--' in slug:
            return False
        
        return True
    
    @staticmethod
    def create_unique_slug_from_title(
        db: Session,
        title: str,
        check_existence: Callable[[Session, str], bool],
        max_length: int = 100
    ) -> str:
        """
        Create a unique slug from a title.
        
        Args:
            db: Database session
            title: The title to convert to slug
            check_existence: Function to check if slug exists
            max_length: Maximum slug length
            
        Returns:
            A unique slug based on the title
        """
        base_slug = SlugUtils.create_slug(title, max_length)
        return SlugUtils.ensure_unique_slug(db, base_slug, check_existence)
    
    @staticmethod
    def update_slug_if_needed(
        db: Session,
        current_slug: str,
        new_title: str,
        check_existence: Callable[[Session, str], bool],
        max_length: int = 100
    ) -> str:
        """
        Update slug if title changed, ensuring uniqueness.
        
        Args:
            db: Database session
            current_slug: Current slug
            new_title: New title
            check_existence: Function to check if slug exists (should exclude current item)
            max_length: Maximum slug length
            
        Returns:
            Updated slug (may be same as current if no change needed)
        """
        new_base_slug = SlugUtils.create_slug(new_title, max_length)
        
        # If the base slug hasn't changed, keep current slug
        if current_slug == new_base_slug:
            return current_slug
        
        # If the base slug is different, ensure uniqueness
        return SlugUtils.ensure_unique_slug(db, new_base_slug, check_existence)
    
    @staticmethod
    def generate_fallback_slug() -> str:
        """
        Generate a fallback slug when title is empty or invalid.
        
        Returns:
            A timestamp-based fallback slug
        """
        import time
        return f"post-{int(time.time())}"


# Convenience functions
def create_slug(text: str, max_length: int = 100) -> str:
    """Create a URL-friendly slug from text."""
    return SlugUtils.create_slug(text, max_length)


def ensure_unique_slug(
    db: Session,
    base_slug: str,
    check_existence: Callable[[Session, str], bool],
    max_attempts: int = 100
) -> str:
    """Ensure a slug is unique by appending numbers if necessary."""
    return SlugUtils.ensure_unique_slug(db, base_slug, check_existence, max_attempts)


def validate_slug(slug: str) -> bool:
    """Validate if a slug meets the requirements."""
    return SlugUtils.validate_slug(slug)