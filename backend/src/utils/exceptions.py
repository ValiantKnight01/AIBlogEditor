"""
Custom exception classes and error handlers for API responses.
Ensures all error responses include both 'detail' and 'error_code' fields as expected by contract tests.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class APIException(HTTPException):
    """
    Base API exception that includes error codes for contract compliance.
    """
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        error_code: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class AuthenticationError(APIException):
    """Authentication-related errors."""
    
    def __init__(self, detail: str, error_code: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(APIException):
    """Authorization-related errors."""
    
    def __init__(self, detail: str = "Access forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class ValidationError(APIException):
    """Validation-related errors."""
    
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(APIException):
    """Resource not found errors."""
    
    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictError(APIException):
    """Resource conflict errors."""
    
    def __init__(self, detail: str = "Resource conflict", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


# Predefined authentication error instances for common cases
class AuthErrors:
    """Common authentication errors with proper error codes."""
    
    MISSING_TOKEN = AuthenticationError(
        detail="Authentication required",
        error_code="MISSING_TOKEN"
    )
    
    INVALID_TOKEN = AuthenticationError(
        detail="Could not validate credentials",
        error_code="INVALID_TOKEN"
    )
    
    EXPIRED_TOKEN = AuthenticationError(
        detail="Token expired",
        error_code="TOKEN_EXPIRED"
    )
    
    INVALID_TOKEN_TYPE = AuthenticationError(
        detail="Invalid token type",
        error_code="INVALID_TOKEN_TYPE"
    )
    
    USER_NOT_FOUND = AuthenticationError(
        detail="User not found",
        error_code="USER_NOT_FOUND"
    )
    
    ACCOUNT_DEACTIVATED = AuthenticationError(
        detail="Account deactivated",
        error_code="ACCOUNT_DEACTIVATED"
    )
    
    INVALID_REFRESH_TOKEN = AuthenticationError(
        detail="Invalid refresh token",
        error_code="INVALID_REFRESH_TOKEN"
    )


def create_error_response(status_code: int, detail: str, error_code: str) -> JSONResponse:
    """Create a properly formatted error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "error_code": error_code
        }
    )


def api_exception_handler(request, exc: APIException) -> JSONResponse:
    """Custom exception handler for APIException instances."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": exc.error_code
        },
        headers=exc.headers
    )