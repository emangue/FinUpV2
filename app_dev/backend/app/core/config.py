"""
Configurações do Backend FastAPI
Usa variáveis de ambiente do arquivo .env
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    """Configurações da aplicação com suporte a .env"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # App
    APP_NAME: str = "Sistema de Finanças API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database - CAMINHO ABSOLUTO
    # ⚠️ IMPORTANTE: Este é o ÚNICO banco usado por TODA a aplicação
    # Backend FastAPI e Frontend Next.js SEMPRE usam este arquivo
    DATABASE_PATH: str = Field(
        default="/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db"
    )
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DATABASE_PATH}"
    
    # JWT Authentication
    # ⚠️ CRÍTICO: SECRET_KEY deve vir do .env (gerada com openssl rand -hex 32)
    SECRET_KEY: str = Field(default="default-dev-key-INSECURE-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - será parseado de string para lista
    BACKEND_CORS_ORIGINS_STR: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="BACKEND_CORS_ORIGINS"
    )
    
    @computed_field
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS_STR.split(",")]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 60  # Aumentado para testes (1 req/sec)
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

settings = Settings()
