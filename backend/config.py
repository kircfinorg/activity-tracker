from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Firebase Configuration
    firebase_credentials_path: Optional[str] = None
    firebase_project_id: Optional[str] = None
    
    # API Configuration
    allowed_origins: str = "http://localhost:3000"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
