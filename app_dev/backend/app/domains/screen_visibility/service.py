"""
Screen Visibility Service
Lógica de negócio - validações e regras
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException
from .repository import ScreenVisibilityRepository
from .models import ScreenVisibility
from .schemas import ScreenVisibilityCreate, ScreenVisibilityUpdate, ScreenVisibilityResponse


class ScreenVisibilityService:
    """Service com lógica de negócio"""
    
    def __init__(self, db: Session):
        self.repository = ScreenVisibilityRepository(db)
    
    def list_all(self) -> List[ScreenVisibilityResponse]:
        """Lista todas as telas (para admin)"""
        screens = self.repository.get_all()
        return [ScreenVisibilityResponse.model_validate(screen) for screen in screens]
    
    def list_for_user(self, is_admin: bool = False) -> List[ScreenVisibilityResponse]:
        """
        Lista telas visíveis para o usuário
        - Admin: todas (P, A, D)
        - Regular: só P
        """
        screens = self.repository.get_visible_for_user(is_admin)
        return [ScreenVisibilityResponse.model_validate(screen) for screen in screens]
    
    def get_by_key(self, screen_key: str) -> Optional[ScreenVisibilityResponse]:
        """Busca tela por chave"""
        screen = self.repository.get_by_key(screen_key)
        if not screen:
            return None
        return ScreenVisibilityResponse.model_validate(screen)
    
    def create(self, data: ScreenVisibilityCreate) -> ScreenVisibilityResponse:
        """Cria nova tela"""
        # Validar se screen_key já existe
        existing = self.repository.get_by_key(data.screen_key)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Screen key '{data.screen_key}' already exists"
            )
        
        # Validar status
        if data.status not in ['P', 'A', 'D']:
            raise HTTPException(
                status_code=400,
                detail="Status must be 'P', 'A', or 'D'"
            )
        
        screen = self.repository.create(data)
        return ScreenVisibilityResponse.model_validate(screen)
    
    def update(self, id: int, data: ScreenVisibilityUpdate) -> ScreenVisibilityResponse:
        """Atualiza tela existente"""
        # Validar status se fornecido
        if data.status and data.status not in ['P', 'A', 'D']:
            raise HTTPException(
                status_code=400,
                detail="Status must be 'P', 'A', or 'D'"
            )
        
        screen = self.repository.update(id, data)
        if not screen:
            raise HTTPException(
                status_code=404,
                detail=f"Screen with id {id} not found"
            )
        
        return ScreenVisibilityResponse.model_validate(screen)
    
    def delete(self, id: int) -> dict:
        """Remove tela"""
        success = self.repository.delete(id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Screen with id {id} not found"
            )
        return {"message": "Screen deleted successfully"}
    
    def update_orders(self, order_updates: dict) -> dict:
        """Atualiza ordem de múltiplas telas"""
        success = self.repository.bulk_update_order(order_updates)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update display orders"
            )
        return {"message": "Display orders updated successfully"}
