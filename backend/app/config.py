"""
Configuration management for Viro-AI Backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path

# Get project root (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "Viroai_DataBase" / "viroai.db"


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH.absolute()}"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_BASE_URL: str = "http://localhost:8000"
    API_V1_STR: str = "/api"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # ML Models
    MODEL_DIR: str = "models/saved_models"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "projects"), exist_ok=True)

