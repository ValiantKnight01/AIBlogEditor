"""
Pagination utility.
Provides pagination logic and metadata for API responses.
"""

from typing import TypeVar, Generic, List, Dict, Any, Optional
from math import ceil
from pydantic import BaseModel
from sqlalchemy.orm import Query


T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination."""
    page: int = 1
    per_page: int = 20
    
    def __post_init__(self):
        """Validate pagination parameters."""
        if self.page < 1:
            self.page = 1
        if self.per_page < 1:
            self.per_page = 1
        elif self.per_page > 100:  # Limit max items per page
            self.per_page = 100


class PageInfo(BaseModel):
    """Pagination metadata information."""
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    
    @classmethod
    def from_params(
        cls,
        page: int,
        per_page: int,
        total_items: int
    ) -> "PageInfo":
        """Create PageInfo from pagination parameters."""
        total_pages = ceil(total_items / per_page) if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        return cls(
            current_page=page,
            per_page=per_page,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            next_page=page + 1 if has_next else None,
            prev_page=page - 1 if has_prev else None
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    page_info: PageInfo
    
    @classmethod
    def create(
        cls,
        items: List[T],
        page: int,
        per_page: int,
        total_items: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        page_info = PageInfo.from_params(page, per_page, total_items)
        return cls(items=items, page_info=page_info)


class PaginationUtils:
    """Utility functions for pagination."""
    
    @staticmethod
    def validate_pagination_params(
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> PaginationParams:
        """Validate and normalize pagination parameters."""
        page = max(1, page or 1)
        per_page = max(1, min(100, per_page or 20))  # Clamp between 1 and 100
        
        return PaginationParams(page=page, per_page=per_page)
    
    @staticmethod
    def calculate_offset(page: int, per_page: int) -> int:
        """Calculate the offset for database queries."""
        return (page - 1) * per_page
    
    @staticmethod
    def paginate_query(
        query: Query,
        page: int,
        per_page: int
    ) -> tuple[List[Any], int]:
        """
        Apply pagination to a SQLAlchemy query.
        
        Returns:
            Tuple of (items, total_count)
        """
        # Get total count before applying pagination
        total_count = query.count()
        
        # Apply pagination
        offset = PaginationUtils.calculate_offset(page, per_page)
        items = query.offset(offset).limit(per_page).all()
        
        return items, total_count
    
    @staticmethod
    def create_paginated_response(
        query: Query,
        page: int,
        per_page: int
    ) -> tuple[List[Any], PageInfo]:
        """
        Create a complete paginated response from a query.
        
        Returns:
            Tuple of (items, page_info)
        """
        # Validate parameters
        pagination = PaginationUtils.validate_pagination_params(page, per_page)
        page = pagination.page
        per_page = pagination.per_page
        
        # Get paginated data
        items, total_count = PaginationUtils.paginate_query(query, page, per_page)
        
        # Create page info
        page_info = PageInfo.from_params(page, per_page, total_count)
        
        return items, page_info
    
    @staticmethod
    def paginate_list(
        items: List[T],
        page: int,
        per_page: int
    ) -> PaginatedResponse[T]:
        """
        Paginate a list of items.
        Useful for in-memory pagination of pre-filtered data.
        """
        # Validate parameters
        pagination = PaginationUtils.validate_pagination_params(page, per_page)
        page = pagination.page
        per_page = pagination.per_page
        
        total_items = len(items)
        offset = PaginationUtils.calculate_offset(page, per_page)
        
        # Slice the list
        paginated_items = items[offset:offset + per_page]
        
        return PaginatedResponse.create(paginated_items, page, per_page, total_items)
    
    @staticmethod
    def get_pagination_links(
        base_url: str,
        page_info: PageInfo,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Optional[str]]:
        """
        Generate pagination links for API responses.
        
        Returns:
            Dictionary with first, prev, next, last links
        """
        query_params = query_params or {}
        
        def build_url(page_num: Optional[int]) -> Optional[str]:
            if page_num is None:
                return None
            
            params = {**query_params, 'page': page_num, 'per_page': page_info.per_page}
            query_string = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
            return f"{base_url}?{query_string}" if query_string else base_url
        
        return {
            "first": build_url(1) if page_info.total_pages > 0 else None,
            "prev": build_url(page_info.prev_page),
            "next": build_url(page_info.next_page),
            "last": build_url(page_info.total_pages) if page_info.total_pages > 0 else None
        }


# Convenience functions
def paginate_query(query: Query, page: int = 1, per_page: int = 20) -> tuple[List[Any], PageInfo]:
    """Convenience function for query pagination."""
    return PaginationUtils.create_paginated_response(query, page, per_page)


def paginate_list(items: List[T], page: int = 1, per_page: int = 20) -> PaginatedResponse[T]:
    """Convenience function for list pagination."""
    return PaginationUtils.paginate_list(items, page, per_page)