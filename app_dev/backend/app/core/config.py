"""
Configurações do Backend FastAPI
"""
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
    
    # Database - CAMINHO ABSOLUTO FIXO
    # ⚠️ IMPORTANTE: Este é o ÚNICO banco usado por TODA a aplicação
    # Backend FastAPI e Frontend Next.js SEMPRE usam este arquivo
    DATABASE_PATH: Path = Path("/Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV4/app_dev/backend/database/financas_dev.db")
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"
    
    # CORS - Aceita tanto lista quanto string separada por vírgulas
    BACKEND_CORS_ORIGINS: Union[list[str], str] = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna CORS origins sempre como lista"""
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
