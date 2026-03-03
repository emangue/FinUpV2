"""
Domínio Users - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import require_admin
from .service import UserService
from .schemas import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserListResponse,
    UserStatsResponse,
    SystemStatsResponse,
    PurgeConfirmacao,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/stats/summary", response_model=SystemStatsResponse)
def get_system_stats(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """🔐 ADMIN ONLY - Estatísticas gerais do sistema."""
    return UserService(db).get_system_stats()


@router.get("/", response_model=UserListResponse)
def list_users(
    apenas_ativos: bool = Query(True, description="Listar apenas usuários ativos"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 Apenas admin
):
    """
    🔐 ADMIN ONLY - Lista todos os usuários.
    Use apenas_ativos=false para incluir usuários inativos.
    """
    service = UserService(db)
    return service.list_users(apenas_ativos)


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Estatísticas do usuário (transações, uploads, grupos, etc)."""
    return UserService(db).get_stats(user_id)


@router.post("/{user_id}/reativar")
def reativar_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Reativa usuário inativo."""
    return UserService(db).reativar(user_id)


@router.delete("/{user_id}/purge")
def purge_user(
    user_id: int,
    body: PurgeConfirmacao,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Remove permanentemente usuário e todos os seus dados. user_id=1 protegido."""
    if user_id == 1:
        raise HTTPException(403, "Admin principal não pode ser purgado")
    if body.confirmacao != "EXCLUIR PERMANENTEMENTE":
        raise HTTPException(400, "Confirmação inválida")
    from .models import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    if body.email_usuario.lower() != user.email.lower():
        raise HTTPException(400, "E-mail não confere")
    return UserService(db).purge_user(user_id, executado_por=admin.id)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Busca usuário por ID."""
    service = UserService(db)
    return service.get_user(user_id)

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Cria novo usuário."""
    service = UserService(db)
    return service.create_user(user, admin_id=admin.id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Atualiza usuário."""
    service = UserService(db)
    return service.update_user(user_id, update_data, admin_id=admin.id)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Desativa usuário (soft delete)."""
    service = UserService(db)
    return service.delete_user(user_id, admin_id=admin.id)

@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    body: ResetPasswordRequest,  # senha no body, não na query string
    db: Session = Depends(get_db),
    admin = Depends(require_admin)  # 🔐 Apenas admin
):
    """🔐 ADMIN ONLY - Reseta a senha de um usuário."""
    service = UserService(db)
    return service.reset_password(user_id, body.nova_senha, admin_id=admin.id)

# TODO: Adicionar endpoints de perfil após completar plano de autenticação
# @router.put("/profile") - Requer get_current_user_from_jwt
# @router.post("/change-password") - Requer get_current_user_from_jwt


