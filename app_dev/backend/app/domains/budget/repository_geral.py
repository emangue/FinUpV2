"""
Budget Geral Repository
Camada de acesso a dados para budget_geral (metas gerais)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from .models import BudgetGeral


class BudgetGeralRepository:
    """Repository para operações de budget geral no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, budget_id: int, user_id: int) -> Optional[BudgetGeral]:
        """Busca budget geral por ID"""
        return self.db.query(BudgetGeral).filter(
            and_(
                BudgetGeral.id == budget_id,
                BudgetGeral.user_id == user_id
            )
        ).first()
    
    def get_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetGeral]:
        """Busca todos os budgets gerais de um mês específico"""
        return self.db.query(BudgetGeral).filter(
            and_(
                BudgetGeral.user_id == user_id,
                BudgetGeral.mes_referencia == mes_referencia
            )
        ).all()
    
    def get_by_categoria_and_month(
        self, 
        user_id: int, 
        categoria_geral: str, 
        mes_referencia: str
    ) -> Optional[BudgetGeral]:
        """Busca budget geral específico por categoria e mês"""
        return self.db.query(BudgetGeral).filter(
            and_(
                BudgetGeral.user_id == user_id,
                BudgetGeral.categoria_geral == categoria_geral,
                BudgetGeral.mes_referencia == mes_referencia
            )
        ).first()
    
    def get_all(self, user_id: int, limit: int = 100) -> List[BudgetGeral]:
        """Lista todos os budgets gerais do usuário"""
        return self.db.query(BudgetGeral).filter(
            BudgetGeral.user_id == user_id
        ).order_by(
            BudgetGeral.mes_referencia.desc(),
            BudgetGeral.categoria_geral
        ).limit(limit).all()
    
    def create(self, user_id: int, data: dict) -> BudgetGeral:
        """Cria novo budget geral"""
        budget = BudgetGeral(
            user_id=user_id,
            **data
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget
    
    def update(self, budget: BudgetGeral, data: dict) -> BudgetGeral:
        """Atualiza budget geral existente"""
        for key, value in data.items():
            setattr(budget, key, value)
        
        budget.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(budget)
        return budget
    
    def delete(self, budget: BudgetGeral) -> None:
        """Deleta budget geral"""
        self.db.delete(budget)
        self.db.commit()
    
    def upsert(
        self, 
        user_id: int, 
        categoria_geral: str, 
        mes_referencia: str, 
        valor_planejado: float
    ) -> BudgetGeral:
        """Cria ou atualiza budget geral (insert or update)"""
        existing = self.get_by_categoria_and_month(user_id, categoria_geral, mes_referencia)
        
        if existing:
            return self.update(existing, {"valor_planejado": valor_planejado})
        else:
            return self.create(user_id, {
                "categoria_geral": categoria_geral,
                "mes_referencia": mes_referencia,
                "valor_planejado": valor_planejado
            })
    
    def bulk_upsert(self, user_id: int, mes_referencia: str, budgets: List[dict]) -> List[BudgetGeral]:
        """Cria ou atualiza múltiplos budgets gerais de uma vez"""
        result = []
        for budget_data in budgets:
            budget = self.upsert(
                user_id=user_id,
                categoria_geral=budget_data["categoria_geral"],
                mes_referencia=mes_referencia,
                valor_planejado=budget_data["valor_planejado"]
            )
            result.append(budget)
        return result
