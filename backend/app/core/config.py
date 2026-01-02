from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./order_tracker.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    ETSY_API_KEY: Optional[str] = None
    ETSY_API_SECRET: Optional[str] = None
    TIKTOK_SHOP_API_KEY: Optional[str] = None
    TIKTOK_SHOP_API_SECRET: Optional[str] = None
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

