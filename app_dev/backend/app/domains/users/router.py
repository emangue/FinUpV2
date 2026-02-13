"""
Domínio Users - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import require_admin
from .service import UserService
from .schemas import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserListResponse
)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=UserListResponse)
def list_users(
    apenas_ativos: bool = Query(True, description="Listar apenas usuários ativos"),
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Lista todos os usuários
    """
    service = UserService(db)
    return service.list_users(apenas_ativos)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca usuário por ID
    """
    service = UserService(db)
    return service.get_user(user_id)

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Cria novo usuário
    """
    service = UserService(db)
    return service.create_user(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Atualiza usuário
    """
    service = UserService(db)
    return service.update_user(user_id, update_data)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Desativa usuário (soft delete)
    """
    service = UserService(db)
    return service.delete_user(user_id)

@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    nova_senha: str,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Reseta a senha de um usuário
    """
    service = UserService(db)
    return service.reset_password(user_id, nova_senha)

# TODO: Adicionar endpoints de perfil após completar plano de autenticação
# @router.put("/profile") - Requer get_current_user_from_jwt
# @router.post("/change-password") - Requer get_current_user_from_jwt


