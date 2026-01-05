"""
Domínio Cards - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional, List
from .models import Cartao

class CardRepository:
    """
    Repository pattern para cartões
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, card_id: int, user_id: int) -> Optional[Cartao]:
        """Busca cartão por ID"""
        return self.db.query(Cartao).filter(
            Cartao.id == card_id,
            Cartao.user_id == user_id
        ).first()
    
    def list_all(self, user_id: int, apenas_ativos: bool = True) -> List[Cartao]:
        """Lista todos os cartões do usuário"""
        query = self.db.query(Cartao).filter(Cartao.user_id == user_id)
        
        if apenas_ativos:
            query = query.filter(Cartao.ativo == 1)
        
        return query.order_by(Cartao.banco, Cartao.nome_cartao).all()
    
    def list_by_bank(
        self,
        user_id: int,
        banco: str,
        apenas_ativos: bool = True
    ) -> List[Cartao]:
        """Lista cartões de um banco específico"""
        query = self.db.query(Cartao).filter(
            Cartao.user_id == user_id,
            Cartao.banco == banco
        )
        
        if apenas_ativos:
            query = query.filter(Cartao.ativo == 1)
        
        return query.order_by(Cartao.nome_cartao).all()
    
    def get_distinct_banks(self, user_id: int) -> List[str]:
        """Retorna lista de bancos únicos do usuário"""
        result = self.db.query(distinct(Cartao.banco)).filter(
            Cartao.user_id == user_id,
            Cartao.ativo == 1
        ).all()
        return [r[0] for r in result]
    
    def count_all(self, user_id: int, apenas_ativos: bool = True) -> int:
        """Conta total de cartões do usuário"""
        query = self.db.query(func.count(Cartao.id)).filter(
            Cartao.user_id == user_id
        )
        
        if apenas_ativos:
            query = query.filter(Cartao.ativo == 1)
        
        return query.scalar()
    
    def find_duplicate(
        self,
        user_id: int,
        banco: str,
        final_cartao: str,
        exclude_id: Optional[int] = None
    ) -> Optional[Cartao]:
        """Busca cartão duplicado (mesmo banco e final)"""
        query = self.db.query(Cartao).filter(
            Cartao.user_id == user_id,
            Cartao.banco == banco,
            Cartao.final_cartao == final_cartao,
            Cartao.ativo == 1
        )
        
        if exclude_id:
            query = query.filter(Cartao.id != exclude_id)
        
        return query.first()
    
    def create(self, card: Cartao) -> Cartao:
        """Cria novo cartão"""
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def update(self, card: Cartao) -> Cartao:
        """Atualiza cartão existente"""
        self.db.commit()
        self.db.refresh(card)
        return card
    
    def delete(self, card: Cartao) -> None:
        """Deleta cartão (hard delete)"""
        self.db.delete(card)
        self.db.commit()
    
    def soft_delete(self, card: Cartao) -> Cartao:
        """Desativa cartão (soft delete)"""
        card.ativo = 0
        return self.update(card)
