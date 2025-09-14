"""
Custom security classes that return proper error formats.
"""

from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from utils.exceptions import AuthErrors


class CustomHTTPBearer(HTTPBearer):
    """
    Custom HTTPBearer that returns properly formatted errors with error_code field.
    """
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise AuthErrors.MISSING_TOKEN
            else:
                return None
        
        if not credentials:
            if self.auto_error:
                raise AuthErrors.INVALID_TOKEN
            else:
                return None
                
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)