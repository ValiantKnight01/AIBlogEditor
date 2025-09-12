from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    # Database connection
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="blog_db", alias="DB_NAME")
    db_user: str = Field(default="blog_user", alias="DB_USER")
    db_password: str = Field(default="blog_password", alias="DB_PASSWORD")
    
    # Connection pool settings
    db_pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=0, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, alias="DB_POOL_RECYCLE")
    
    @property
    def database_url(self) -> str:
        """Generate database URL for SQLAlchemy."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def async_database_url(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class AuthSettings(BaseSettings):
    """Authentication configuration settings."""
    
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = Field(
        default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS"
    )


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application
    app_name: str = Field(default="Personal Blog API", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    reload: bool = Field(default=False, alias="RELOAD")
    
    # CORS
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000"], alias="ALLOWED_ORIGINS"
    )
    allowed_credentials: bool = Field(default=True, alias="ALLOWED_CREDENTIALS")
    allowed_methods: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"], alias="ALLOWED_METHODS"
    )
    allowed_headers: list[str] = Field(default=["*"], alias="ALLOWED_HEADERS")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, alias="RATE_LIMIT_PERIOD")  # seconds
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    
    # Database settings
    database: DatabaseSettings = DatabaseSettings()
    
    # Auth settings  
    auth: AuthSettings = AuthSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()