"""
Domínio Dashboard - Service
Lógica de negócio para dashboard
"""
from sqlalchemy.orm import Session
from datetime import datetime

from .repository import DashboardRepository
from .schemas import DashboardMetrics, ChartDataResponse, CategoryExpense, ChartDataPoint


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)
    
    def get_metrics(self, user_id: int, year: int, month: int) -> DashboardMetrics:
        """Retorna métricas principais do dashboard"""
        data = self.repository.get_metrics(user_id, year, month)
        return DashboardMetrics(**data)
    
    def get_chart_data(self, user_id: int, year: int, month: int) -> ChartDataResponse:
        """Retorna dados para gráfico de área"""
        data = self.repository.get_chart_data(user_id, year, month)
        chart_points = [ChartDataPoint(**point) for point in data]
        return ChartDataResponse(data=chart_points)
    
    def get_category_expenses(self, user_id: int, year: int, month: int) -> list[CategoryExpense]:
        """Retorna despesas por categoria"""
        data = self.repository.get_category_expenses(user_id, year, month)
        return [CategoryExpense(**expense) for expense in data]
