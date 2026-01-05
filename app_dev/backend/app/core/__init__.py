"""
Core - Exports
Módulo core contém configurações e database compartilhados
"""
from .config import settings, Settings
from .database import Base, engine, SessionLocal, get_db

__all__ = [
    "settings",
    "Settings",
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]
