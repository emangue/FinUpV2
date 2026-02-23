"""
Configurações do Backend FastAPI
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Union

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding='utf-8'
    )
    
    # App
    APP_NAME: str = "Sistema de Finanças API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # ✅ False por padrão (segurança)
    
    # Database — PostgreSQL obrigatório (Docker fornece via DATABASE_URL)
    # Formato: postgresql://user:password@host:port/database
    # Definido no docker-compose.yml → container backend
    # ❌ SQLite não é mais suportado neste projeto
    DATABASE_URL: str  # OBRIGATÓRIO — sem fallback SQLite

    @property
    def is_postgres(self) -> bool:
        """Sempre True — apenas PostgreSQL é suportado"""
        return self.DATABASE_URL.startswith("postgresql")
    
    # CORS - Aceita tanto lista quanto string separada por vírgulas
    # 3000=BAU frontend | 3001=app_admin
    BACKEND_CORS_ORIGINS: Union[list[str], str] = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # JWT Authentication
    JWT_SECRET_KEY: str  # ✅ OBRIGATÓRIO via .env (sem fallback inseguro)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hora
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna CORS origins sempre como lista"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
