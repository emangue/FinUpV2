"""
Configurações do Backend FastAPI
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
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
    DEBUG: bool = True
    
    # Database - Suporta SQLite (dev) e PostgreSQL (prod)
    # ⚠️ IMPORTANTE: Este é o ÚNICO banco usado por TODA a aplicação
    # Backend FastAPI e Frontend Next.js SEMPRE usam este arquivo
    DATABASE_PATH: Path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db")
    
    # PostgreSQL - Lido de variável de ambiente
    # Formato: postgresql://user:password@host:port/database
    # Exemplo: postgresql://finup_user:senha@localhost:5432/finup_db_dev
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATABASE_PATH}"  # Fallback para SQLite
    )
    
    @property
    def is_postgres(self) -> bool:
        """Verifica se está usando PostgreSQL"""
        return self.DATABASE_URL.startswith("postgresql")
    
    # CORS - Aceita tanto lista quanto string separada por vírgulas
    BACKEND_CORS_ORIGINS: Union[list[str], str] = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hora
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna CORS origins sempre como lista"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
