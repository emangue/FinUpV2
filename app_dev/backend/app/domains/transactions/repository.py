"""
Domínio Transactions - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from .models import JournalEntry
from .schemas import TransactionFilters

class TransactionRepository:
    """
    Repository pattern para transações
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, transaction_id: str, user_id: int) -> Optional[JournalEntry]:
        """Busca transação por ID"""
        return self.db.query(JournalEntry).filter(
            JournalEntry.IdTransacao == transaction_id,
            JournalEntry.user_id == user_id
        ).first()
    
    def list_all(self, user_id: int, skip: int = 0, limit: int = 100) -> List[JournalEntry]:
        """Lista todas as transações do usuário"""
        return self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def list_with_filters(
        self,
        user_id: int,
        filters: TransactionFilters,
        skip: int = 0,
        limit: int = 100
    ) -> List[JournalEntry]:
        """Lista transações com filtros"""
        query = self.db.query(JournalEntry).filter(JournalEntry.user_id == user_id)
        
        if filters.year and filters.month:
            # Mês específico: usa MesFatura exato
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            # Ano inteiro: filtra MesFatura começando com o ano
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        
        if filters.estabelecimento:
            query = query.filter(
                JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%")
            )
        
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        
        if filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(self, user_id: int, filters: TransactionFilters) -> int:
        """Conta transações com filtros"""
        query = self.db.query(func.count(JournalEntry.id)).filter(
            JournalEntry.user_id == user_id
        )
        
        # Aplicar mesmos filtros
        if filters.year and filters.month:
            # Mês específico: usa MesFatura exato
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            # Ano inteiro: filtra MesFatura começando com o ano
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        if filters.estabelecimento:
            query = query.filter(
                JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%")
            )
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        if filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        if filters.search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"),
                    JournalEntry.GRUPO.ilike(f"%{filters.search}%"),
                    JournalEntry.SUBGRUPO.ilike(f"%{filters.search}%")
                )
            )
        
        return query.scalar()
    
    def create(self, transaction: JournalEntry) -> JournalEntry:
        """Cria nova transação"""
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def update(self, transaction: JournalEntry) -> JournalEntry:
        """Atualiza transação existente"""
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def delete(self, transaction: JournalEntry) -> None:
        """Deleta transação"""
        self.db.delete(transaction)
        self.db.commit()
    
    def get_total_by_filters(self, user_id: int, filters: TransactionFilters) -> float:
        """Soma total de valores com filtros"""
        query = self.db.query(func.sum(JournalEntry.Valor)).filter(
            JournalEntry.user_id == user_id
        )
        
        # Aplicar filtros
        if filters.year and filters.month:
            # Mês específico: usa MesFatura exato
            mes_fatura = f"{filters.year}{filters.month:02d}"
            query = query.filter(JournalEntry.MesFatura == mes_fatura)
        elif filters.year:
            # Ano inteiro: filtra MesFatura começando com o ano
            query = query.filter(JournalEntry.MesFatura.like(f"{filters.year}%"))
        if filters.tipo:
            query = query.filter(JournalEntry.TipoTransacao == filters.tipo)
        if filters.categoria_geral:
            query = query.filter(JournalEntry.CategoriaGeral == filters.categoria_geral)
        if filters.tipo_gasto:
            if isinstance(filters.tipo_gasto, list):
                query = query.filter(JournalEntry.TipoGasto.in_(filters.tipo_gasto))
            else:
                query = query.filter(JournalEntry.TipoGasto == filters.tipo_gasto)
        if filters.grupo:
            query = query.filter(JournalEntry.GRUPO == filters.grupo)
        if filters.subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == filters.subgrupo)
        if filters.estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.estabelecimento}%"))
        if filters.search:
            query = query.filter(JournalEntry.Estabelecimento.ilike(f"%{filters.search}%"))
        if filters.cartao:
            query = query.filter(JournalEntry.NomeCartao == filters.cartao)
        
        result = query.scalar()
        return result or 0.0
