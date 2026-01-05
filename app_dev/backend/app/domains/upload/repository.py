"""
Domínio Upload - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from .models import PreviewTransacao

class UploadRepository:
    """
    Repository pattern para upload/preview
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_session_id(
        self,
        session_id: str,
        user_id: int
    ) -> List[PreviewTransacao]:
        """Busca todos os previews de uma sessão"""
        return self.db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).all()
    
    def count_by_session_id(
        self,
        session_id: str,
        user_id: int
    ) -> int:
        """Conta previews de uma sessão"""
        return self.db.query(func.count(PreviewTransacao.id)).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).scalar()
    
    def delete_all_by_user(self, user_id: int) -> int:
        """
        Deleta TODOS os previews de um usuário
        Usado antes de novo upload para limpar sessões antigas
        """
        deleted = self.db.query(PreviewTransacao).filter(
            PreviewTransacao.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted
    
    def delete_by_session_id(
        self,
        session_id: str,
        user_id: int
    ) -> int:
        """Deleta previews de uma sessão específica"""
        deleted = self.db.query(PreviewTransacao).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted
    
    def create_batch(self, previews: List[PreviewTransacao]) -> List[PreviewTransacao]:
        """Cria múltiplos previews em batch"""
        self.db.add_all(previews)
        self.db.commit()
        return previews
    
    def session_exists(self, session_id: str, user_id: int) -> bool:
        """Verifica se sessão existe"""
        count = self.db.query(func.count(PreviewTransacao.id)).filter(
            PreviewTransacao.session_id == session_id,
            PreviewTransacao.user_id == user_id
        ).scalar()
        return count > 0
