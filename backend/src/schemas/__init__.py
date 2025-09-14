"""
Input validation schemas using Pydantic.
Main module for all API request/response schemas.
"""

# Import all schema modules
from .auth_schemas import *
from .user_schemas import *
from .blog_schemas import *
from .project_schemas import *
from .tag_schemas import *
from .common_schemas import *

# Define what gets imported with "from schemas import *"
__all__ = [
    # Auth schemas
    "UserLogin",
    "UserRegister", 
    "PasswordChange",
    "TokenRequest",
    "TokenResponse",
    "LoginResponse",
    
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserListResponse",
    "UserStats",
    
    # Blog schemas
    "BlogPostBase",
    "BlogPostCreate",
    "BlogPostUpdate",
    "BlogPostResponse",
    "BlogPostSummary",
    "BlogPostListResponse",
    "BlogPostStatusUpdate",
    "BlogPostSearchParams",
    
    # Project schemas
    "ProjectBase",
    "ProjectCreate", 
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectSummary",
    "ProjectListResponse",
    "ProjectStatusUpdate",
    "ProjectFeaturedUpdate",
    "ProjectSearchParams",
    "TechStackResponse",
    
    # Tag schemas
    "TagBase",
    "TagCreate",
    "TagUpdate",
    "TagResponse",
    "TagSummary", 
    "TagListResponse",
    "TagSearchParams",
    "TagUsageStats",
    "TagMergeRequest",
    
    # Common schemas
    "PageInfo",
    "PaginatedResponse",
    "ErrorDetail",
    "ErrorResponse", 
    "SuccessResponse",
    "HealthResponse",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "SearchParams",
    "SortParams",
    "FilterParams",
    "BulkOperationRequest",
    "BulkOperationResponse",
    "StatsResponse",
    "ImportRequest",
    "ImportResponse",
    "ExportRequest",
    "ExportResponse",
]