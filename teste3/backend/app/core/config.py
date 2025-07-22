from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Dashboard API"
    env: str = "development"
    debug: bool = True
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50
    redis_decode_responses: bool = True
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_retry_on_timeout: bool = True
    redis_health_check_interval: int = 30
    
    # Tiny API
    tiny_api_token: str = ""
    tiny_api_base_url: str = "https://api.tiny.com.br/api2"
    tiny_api_timeout: int = 30
    tiny_api_max_retries: int = 3
    tiny_api_retry_delay: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Performance
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()