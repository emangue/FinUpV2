"""
Screen Visibility Repository
Camada de acesso aos dados - TODAS as queries SQL aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
from .models import ScreenVisibility
from .schemas import ScreenVisibilityCreate, ScreenVisibilityUpdate


class ScreenVisibilityRepository:
    """Repository para operações de banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[ScreenVisibility]:
        """Retorna todas as telas ordenadas por display_order"""
        return self.db.query(ScreenVisibility).order_by(ScreenVisibility.display_order).all()
    
    def get_by_key(self, screen_key: str) -> Optional[ScreenVisibility]:
        """Busca tela por screen_key"""
        return self.db.query(ScreenVisibility).filter(ScreenVisibility.screen_key == screen_key).first()
    
    def get_by_id(self, id: int) -> Optional[ScreenVisibility]:
        """Busca tela por ID"""
        return self.db.query(ScreenVisibility).filter(ScreenVisibility.id == id).first()
    
    def get_visible_for_user(self, is_admin: bool = False) -> List[ScreenVisibility]:
        """
        Retorna telas visíveis para o usuário
        - Admin vê: P, A, D (todas)
        - User regular vê: P (só produção)
        """
        if is_admin:
            # Admin vê tudo
            return self.get_all()
        else:
            # User regular vê só P
            return self.db.query(ScreenVisibility).filter(
                ScreenVisibility.status == 'P'
            ).order_by(ScreenVisibility.display_order).all()
    
    def create(self, data: ScreenVisibilityCreate) -> ScreenVisibility:
        """Cria nova tela"""
        db_screen = ScreenVisibility(**data.model_dump())
        self.db.add(db_screen)
        self.db.commit()
        self.db.refresh(db_screen)
        return db_screen
    
    def update(self, id: int, data: ScreenVisibilityUpdate) -> Optional[ScreenVisibility]:
        """Atualiza tela existente"""
        db_screen = self.get_by_id(id)
        if not db_screen:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_screen, field, value)
        
        self.db.commit()
        self.db.refresh(db_screen)
        return db_screen
    
    def delete(self, id: int) -> bool:
        """Remove tela"""
        db_screen = self.get_by_id(id)
        if not db_screen:
            return False
        
        self.db.delete(db_screen)
        self.db.commit()
        return True
    
    def bulk_update_order(self, order_updates: dict) -> bool:
        """
        Atualiza ordem de múltiplas telas de uma vez
        order_updates: {screen_key: new_order}
        """
        try:
            for screen_key, new_order in order_updates.items():
                self.db.query(ScreenVisibility).filter(
                    ScreenVisibility.screen_key == screen_key
                ).update({"display_order": new_order})
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
