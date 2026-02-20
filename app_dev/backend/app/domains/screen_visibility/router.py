"""
Screen Visibility Router
Endpoints FastAPI para gerenciamento de visibilidade de telas
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.shared.dependencies import get_current_user_id, require_admin
from .service import ScreenVisibilityService
from .schemas import (
    ScreenVisibilityResponse,
    ScreenVisibilityCreate,
    ScreenVisibilityUpdate
)


router = APIRouter()


@router.get("/list", response_model=List[ScreenVisibilityResponse])
def list_screens(
    is_admin: bool = False,  # TODO: Pegar do token/session do usuário
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Lista telas visíveis para o usuário
    - Admin (is_admin=True): vê todas as telas (P, A, D)
    - User regular (is_admin=False): vê só telas em produção (P)
    """
    service = ScreenVisibilityService(db)
    return service.list_for_user(is_admin=is_admin)


@router.get("/admin/all", response_model=List[ScreenVisibilityResponse])
def list_all_screens_admin(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    admin=Depends(require_admin),
):
    """
    Lista TODAS as telas (endpoint admin)
    Usado na tela de configuração de visibilidade
    """
    service = ScreenVisibilityService(db)
    return service.list_all()


@router.get("/{screen_key}", response_model=ScreenVisibilityResponse)
def get_screen(
    screen_key: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca tela por screen_key"""
    service = ScreenVisibilityService(db)
    screen = service.get_by_key(screen_key)
    if not screen:
        raise HTTPException(status_code=404, detail=f"Screen '{screen_key}' not found")
    return screen


@router.post("/", response_model=ScreenVisibilityResponse)
def create_screen(
    data: ScreenVisibilityCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    admin=Depends(require_admin),
):
    """Cria nova tela (admin only)"""
    service = ScreenVisibilityService(db)
    return service.create(data)


@router.patch("/{id}", response_model=ScreenVisibilityResponse)
def update_screen(
    id: int,
    data: ScreenVisibilityUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    admin=Depends(require_admin),
):
    """Atualiza tela existente (admin only)"""
    service = ScreenVisibilityService(db)
    return service.update(id, data)


@router.delete("/{id}")
def delete_screen(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    admin=Depends(require_admin),
):
    """Remove tela (admin only)"""
    service = ScreenVisibilityService(db)
    return service.delete(id)


@router.post("/reorder")
def reorder_screens(
    order_updates: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    admin=Depends(require_admin),
):
    """
    Atualiza ordem de exibição de múltiplas telas
    Body: {"dashboard": 1, "transactions": 2, ...}
    """
    service = ScreenVisibilityService(db)
    return service.update_orders(order_updates)
