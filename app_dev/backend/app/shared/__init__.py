"""
Shared - Exports
Módulo shared contém dependências e utils compartilhados
"""
from .dependencies import get_current_user_id, require_admin, get_current_user

__all__ = [
    "get_current_user_id",
    "require_admin",
    "get_current_user",
]
