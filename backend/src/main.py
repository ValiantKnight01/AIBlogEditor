"""
Personal Blog Backend API

This is the main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from src.config import Settings

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


# API Router will be added here later
# app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("DEBUG", "false").lower() == "true" else False,
    )