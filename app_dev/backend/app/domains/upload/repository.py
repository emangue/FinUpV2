"""
Domínio Upload - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime
import logging
from .models import PreviewTransacao
from .history_models import UploadHistory

logger = logging.getLogger(__name__)

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
        try:
            deleted = self.db.query(PreviewTransacao).filter(
                PreviewTransacao.session_id == session_id,
                PreviewTransacao.user_id == user_id
            ).delete(synchronize_session=False)
            self.db.commit()
            return deleted
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erro ao deletar sessão {session_id}: {str(e)}")
            return 0
    
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
    
    # ========== MÉTODOS DE UPLOAD_HISTORY ==========
    
    def create_upload_history(self, history: UploadHistory) -> UploadHistory:
        """Cria registro de histórico"""
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def update_upload_history(self, history_id: int, **kwargs) -> Optional[UploadHistory]:
        """Atualiza registro de histórico"""
        history = self.db.query(UploadHistory).filter(UploadHistory.id == history_id).first()
        if history:
            for key, value in kwargs.items():
                setattr(history, key, value)
            self.db.commit()
            self.db.refresh(history)
        return history
    
    def get_upload_history_by_session(self, session_id: str, user_id: int) -> Optional[UploadHistory]:
        """Busca histórico por session_id"""
        return self.db.query(UploadHistory).filter(
            UploadHistory.session_id == session_id,
            UploadHistory.user_id == user_id
        ).first()
    
    def get_history_by_session(self, session_id: str) -> Optional[UploadHistory]:
        """Busca histórico por session_id (sem filtro de user)"""
        return self.db.query(UploadHistory).filter(
            UploadHistory.session_id == session_id
        ).first()
    
    def list_upload_history(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[UploadHistory]:
        """Lista históricos de um usuário (ordem decrescente). status='success' filtra só realizados."""
        q = self.db.query(UploadHistory).filter(UploadHistory.user_id == user_id)
        if status:
            q = q.filter(UploadHistory.status == status)
        return q.order_by(desc(UploadHistory.data_upload)).limit(limit).offset(offset).all()
    
    def count_upload_history(self, user_id: int, status: Optional[str] = None) -> int:
        """Conta total de históricos de um usuário"""
        q = self.db.query(func.count(UploadHistory.id)).filter(UploadHistory.user_id == user_id)
        if status:
            q = q.filter(UploadHistory.status == status)
        return q.scalar()
