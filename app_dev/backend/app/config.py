"""
Configurações do Backend FastAPI
"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # App
    APP_NAME: str = "Sistema de Finanças API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./database/financas_dev.db"
    DATABASE_PATH: Path = Path(__file__).parent.parent / "database" / "financas_dev.db"
    
    # JWT
    SECRET_KEY: str = "seu-secret-key-super-secreto-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
