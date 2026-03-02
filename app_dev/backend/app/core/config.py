"""
Configurações do Backend FastAPI
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
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
    
    # Database — PostgreSQL (Docker fornece via DATABASE_URL)
    # Formato: postgresql://user:password@host:port/database
    DATABASE_URL: str  # OBRIGATÓRIO — via .env

    @property
    def is_postgres(self) -> bool:
        """True — apenas PostgreSQL é suportado"""
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

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY deve ter no mínimo 32 caracteres. Gere com: openssl rand -hex 32")
        return v
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna CORS origins sempre como lista"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
