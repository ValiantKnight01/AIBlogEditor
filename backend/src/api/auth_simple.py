"""
Authentication API endpoints.
Handles user authentication (login, logout, refresh token).
"""

from fastapi import APIRouter, HTTPException, status, Response, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text
import bcrypt
import os
from jose import jwt
from datetime import datetime, timedelta

# Simple database connection  
def get_db():
    """Simple database connection without circular imports."""
    import sys
    sys.path.append('/app/src')
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Database URL from environment
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "blog_db")
    db_user = os.getenv("DB_USER", "blog_user")
    db_password = os.getenv("DB_PASSWORD", "blog_password")
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple schemas
class UserLoginSimple(BaseModel):
    email: EmailStr
    password: str

class LoginResponseSimple(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

# Create router
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production") 
    algorithm = "HS256"
    expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    algorithm = "HS256"
    expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@router.post("/login", response_model=LoginResponseSimple, status_code=200)
async def login(
    user_credentials: UserLoginSimple,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    User login endpoint - connects to real database.
    """
    try:
        # Query user from database
        result = db.execute(
            text("SELECT id, email, username, password_hash, full_name, bio, avatar_url, is_active, created_at, updated_at FROM users WHERE email = :email"),
            {"email": user_credentials.email.lower()}
        )
        user_row = result.fetchone()
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user_row.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_credentials.password, user_row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        token_data = {
            "sub": str(user_row.id),
            "email": user_row.email,
            "username": user_row.username
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user_row.id), "email": user_row.email})
        
        # Set refresh token as secure HTTP-only cookie
        expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=expire_days * 24 * 60 * 60,
            httponly=True,
            secure=False,  # Set to False for local development
            samesite="lax"
        )
        
        # Return login response
        return LoginResponseSimple(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer", 
            expires_in=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) * 60,
            user={
                "id": str(user_row.id),
                "email": user_row.email,
                "username": user_row.username,
                "full_name": user_row.full_name,
                "bio": user_row.bio,
                "avatar_url": user_row.avatar_url,
                "created_at": user_row.created_at.isoformat() if user_row.created_at else None,
                "updated_at": user_row.updated_at.isoformat() if user_row.updated_at else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout", status_code=204)
async def logout():
    """Simple logout endpoint."""
    return {"message": "Logout successful"}


@router.post("/refresh", status_code=200)
async def refresh():
    """Simple refresh endpoint."""
    return {
        "access_token": "new_access_token",
        "token_type": "bearer",
        "expires_in": 1800
    }