"""
Budget Service
Lógica de negócio para budget planning
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from .repository import BudgetRepository
from .repository_geral import BudgetGeralRepository
from .schemas import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse


class BudgetService:
    """Service com lógica de negócio para budget"""
    
    def __init__(self, db: Session):
        self.repository = BudgetRepository(db)
        self.repository_geral = BudgetGeralRepository(db)
    
    def get_budget(self, budget_id: int, user_id: int) -> BudgetResponse:
        """Busca budget por ID"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        return BudgetResponse.from_orm(budget)
    
    def get_budgets_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetResponse]:
        """Lista budgets de um mês específico"""
        budgets = self.repository.get_by_month(user_id, mes_referencia)
        return [BudgetResponse.from_orm(b) for b in budgets]
    
    def get_all_budgets(self, user_id: int) -> BudgetListResponse:
        """Lista todos os budgets do usuário"""
        budgets = self.repository.get_all(user_id)
        return BudgetListResponse(
            budgets=[BudgetResponse.from_orm(b) for b in budgets],
            total=len(budgets)
        )
    
    def create_budget(self, user_id: int, data: BudgetCreate) -> BudgetResponse:
        """Cria novo budget"""
        # Verificar se já existe budget para este tipo_gasto/mês
        existing = self.repository.get_by_tipo_gasto_and_month(
            user_id, 
            data.tipo_gasto, 
            data.mes_referencia
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe budget para {data.tipo_gasto} em {data.mes_referencia}. Use PUT para atualizar."
            )
        
        budget = self.repository.create(user_id, data.dict())
        return BudgetResponse.from_orm(budget)
    
    def update_budget(self, budget_id: int, user_id: int, data: BudgetUpdate) -> BudgetResponse:
        """Atualiza budget existente"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        updated = self.repository.update(budget, data.dict(exclude_unset=True))
        return BudgetResponse.from_orm(updated)
    
    def delete_budget(self, budget_id: int, user_id: int) -> None:
        """Deleta budget"""
        budget = self.repository.get_by_id(budget_id, user_id)
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget não encontrado"
            )
        
        self.repository.delete(budget)
    
    def bulk_upsert_budgets(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[BudgetResponse]:
        """Cria ou atualiza múltiplos budgets de uma vez"""
        # Validar dados
        for budget_data in budgets:
            if "tipo_gasto" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget deve ter 'tipo_gasto' e 'valor_planejado'"
                )
            
            if budget_data["valor_planejado"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="valor_planejado deve ser maior que zero"
                )
        
        result = self.repository.bulk_upsert(user_id, mes_referencia, budgets)
        return [BudgetResponse.from_orm(b) for b in result]
    
    # ===== MÉTODOS PARA BUDGET GERAL =====
    
    def get_budget_geral_by_month(self, user_id: int, mes_referencia: str) -> List[BudgetResponse]:
        """Lista budgets gerais de um mês específico"""
        budgets = self.repository_geral.get_by_month(user_id, mes_referencia)
        return [BudgetResponse.from_orm(b) for b in budgets]
    
    def get_all_budget_geral(self, user_id: int) -> BudgetListResponse:
        """Lista todos os budgets gerais do usuário"""
        budgets = self.repository_geral.get_all(user_id)
        return BudgetListResponse(
            budgets=[BudgetResponse.from_orm(b) for b in budgets],
            total=len(budgets)
        )
    
    def bulk_upsert_budget_geral(
        self, 
        user_id: int, 
        mes_referencia: str, 
        budgets: List[dict]
    ) -> List[BudgetResponse]:
        """Cria ou atualiza múltiplos budgets gerais de uma vez"""
        # Validar dados
        for budget_data in budgets:
            if "categoria_geral" not in budget_data or "valor_planejado" not in budget_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada budget geral deve ter 'categoria_geral' e 'valor_planejado'"
                )
            
            if budget_data["valor_planejado"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="valor_planejado deve ser maior que zero"
                )
        
        result = self.repository_geral.bulk_upsert(user_id, mes_referencia, budgets)
        return [BudgetResponse.from_orm(b) for b in result]

