"""
Domínio Users
Exporta componentes principais
"""
from .models import User
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from .service import UserService
from .repository import UserRepository
# NÃO importar router aqui - causa circular import com require_admin

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "UserService",
    "UserRepository",
]
