"""
Personal Blog Backend API

This is the main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import HTTPException
import uvicorn
import os
import sys
sys.path.append(os.path.dirname(__file__))
from config import Settings
from utils.exceptions import APIException, api_exception_handler

# Initialize settings
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title="Personal Blog API",
    description="A personal blog platform API built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom exception handler for API errors
app.add_exception_handler(APIException, api_exception_handler)

# Add fallback handler for generic HTTPException to ensure error_code field
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Fallback handler for HTTPException to ensure error_code field."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_EXCEPTION"  # Generic error code for unhandled HTTPExceptions
        },
        headers=getattr(exc, 'headers', None)
    )


@app.get("/")
async def root():
    """Root endpoint that returns basic API information."""
    return {
        "message": "Personal Blog API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and Docker health checks."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "API is running"
        }
    )


# Import API routers  
from api.auth_simple import router as auth_router
from api.users import router as users_router
from api.posts import router as posts_router
from api.projects import router as projects_router
from api.tags import router as tags_router

# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)
app.include_router(projects_router)
app.include_router(tags_router)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("DEBUG", "false").lower() == "true" else False,
    )