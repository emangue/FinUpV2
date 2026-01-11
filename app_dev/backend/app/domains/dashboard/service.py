"""
Domínio Dashboard - Service
Lógica de negócio para dashboard
"""
from sqlalchemy.orm import Session
from datetime import datetime

from .repository import DashboardRepository
from .schemas import (
    DashboardMetrics, 
    ChartDataResponse, 
    CategoryExpense, 
    ChartDataPoint,
    BudgetVsActualResponse,
    BudgetVsActualItem
)


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)
    
    def get_metrics(self, user_id: int, year: int, month: int = None) -> DashboardMetrics:
        """Retorna métricas principais do dashboard
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        data = self.repository.get_metrics(user_id, year, month)
        return DashboardMetrics(**data)
    
    def get_chart_data(self, user_id: int, year: int, month: int) -> ChartDataResponse:
        """Retorna dados para gráfico de área"""
        data = self.repository.get_chart_data(user_id, year, month)
        chart_points = [ChartDataPoint(**point) for point in data]
        return ChartDataResponse(data=chart_points)
    
    def get_category_expenses(self, user_id: int, year: int, month: int = None) -> list[CategoryExpense]:
        """Retorna despesas por categoria
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        data = self.repository.get_category_expenses(user_id, year, month)
        return [CategoryExpense(**expense) for expense in data]
    
    def get_budget_vs_actual(self, user_id: int, year: int, month: int) -> BudgetVsActualResponse:
        """Retorna comparação Realizado vs Planejado por TipoGasto"""
        data = self.repository.get_budget_vs_actual(user_id, year, month)
        
        items = [BudgetVsActualItem(**item) for item in data["items"]]
        
        return BudgetVsActualResponse(
            items=items,
            total_realizado=data["total_realizado"],
            total_planejado=data["total_planejado"],
            percentual_geral=data["percentual_geral"]
        )
