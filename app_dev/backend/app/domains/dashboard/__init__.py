"""
Domínio Dashboard
Métricas e estatísticas agregadas
"""
from .schemas import DashboardMetrics, ChartDataResponse, CategoryExpense
from .service import DashboardService
from .router import router

__all__ = [
    "DashboardMetrics",
    "ChartDataResponse",
    "CategoryExpense",
    "DashboardService",
    "router",
]
