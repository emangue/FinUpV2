"""
Budget Repository
Camada de acesso a dados para budget_planning
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from .models import BudgetPlanning


class BudgetRepository:
    """Repository para operações de budget no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, budget_id: int, user_id: int) -> Optional[BudgetPlanning]:
        """Busca budget por ID"""
        return self.db.query(BudgetPlanning).filter(
            and_(
                BudgetPlanning.id == budget_id,
                BudgetPlanning.user_id == user_id
            )
        ).first()
    
    def get_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetPlanning]:
        """Busca todos os budgets de um mês específico"""
        return self.db.query(BudgetPlanning).filter(
            and_(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.mes_referencia == mes_referencia
            )
        ).all()
    
    def get_by_tipo_gasto_and_month(
        self, 
        user_id: int, 
        tipo_gasto: str, 
        mes_referencia: str
    ) -> Optional[BudgetPlanning]:
        """Busca budget específico por tipo_gasto e mês"""
        return self.db.query(BudgetPlanning).filter(
            and_(
                BudgetPlanning.user_id == user_id,
                BudgetPlanning.tipo_gasto == tipo_gasto,
                BudgetPlanning.mes_referencia == mes_referencia
            )
        ).first()
    
    def get_all(self, user_id: int, limit: int = 100) -> List[BudgetPlanning]:
        """Lista todos os budgets do usuário"""
        return self.db.query(BudgetPlanning).filter(
            BudgetPlanning.user_id == user_id
        ).order_by(
            BudgetPlanning.mes_referencia.desc(),
            BudgetPlanning.tipo_gasto
        ).limit(limit).all()
    
    def create(self, user_id: int, data: dict) -> BudgetPlanning:
        """Cria novo budget"""
        budget = BudgetPlanning(
            user_id=user_id,
            **data
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget
    
    def update(self, budget: BudgetPlanning, data: dict) -> BudgetPlanning:
        """Atualiza budget existente"""
        for key, value in data.items():
            setattr(budget, key, value)
        
        budget.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(budget)
        return budget
    
    def delete(self, budget: BudgetPlanning) -> None:
        """Deleta budget"""
        self.db.delete(budget)
        self.db.commit()
    
    def upsert(
        self, 
        user_id: int, 
        tipo_gasto: str, 
        mes_referencia: str, 
        valor_planejado: float
    ) -> BudgetPlanning:
        """Cria ou atualiza budget (insert or update)"""
        existing = self.get_by_tipo_gasto_and_month(user_id, tipo_gasto, mes_referencia)
        
        if existing:
            return self.update(existing, {"valor_planejado": valor_planejado})
        else:
            return self.create(user_id, {
                "tipo_gasto": tipo_gasto,
                "mes_referencia": mes_referencia,
                "valor_planejado": valor_planejado
            })
    
    def bulk_upsert(self, user_id: int, mes_referencia: str, budgets: List[dict]) -> List[BudgetPlanning]:
        """Cria ou atualiza múltiplos budgets de uma vez"""
        result = []
        for budget_data in budgets:
            budget = self.upsert(
                user_id=user_id,
                tipo_gasto=budget_data["tipo_gasto"],
                mes_referencia=mes_referencia,
                valor_planejado=budget_data["valor_planejado"]
            )
            result.append(budget)
        return result
