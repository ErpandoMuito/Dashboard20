import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Config
    API_V2_STR = "/api/v2"
    PROJECT_NAME = "Dashboard Estoque"
    
    # Redis
    REDIS_URL = os.getenv("VALKEY_PUBLIC_URL", "redis://localhost:6379")
    
    # Tiny API
    TINY_API_TOKEN = os.getenv("TINY_API_TOKEN", "")
    TINY_API_BASE_URL = "https://api.tiny.com.br/api2"
    
    # CORS
    BACKEND_CORS_ORIGINS = ["http://localhost:3000"]

config = Config()