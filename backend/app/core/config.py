import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Config
    API_V2_STR: str = "/api/v2"
    PROJECT_NAME: str = "Dashboard Estoque"
    
    # Redis
    REDIS_URL: str = os.getenv("VALKEY_PUBLIC_URL", "redis://localhost:6379")
    
    # Tiny API
    TINY_API_TOKEN: str = os.getenv("TINY_API_TOKEN", "")
    TINY_API_BASE_URL: str = "https://api.tiny.com.br/api2"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignorar campos extras

settings = Settings()