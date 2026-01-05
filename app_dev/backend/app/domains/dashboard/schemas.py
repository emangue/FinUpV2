"""
Domínio Dashboard - Schemas Pydantic
"""
from pydantic import BaseModel
from typing import List


class DashboardMetrics(BaseModel):
    """Métricas principais do dashboard"""
    total_despesas: float
    total_receitas: float
    total_cartoes: float
    saldo_periodo: float
    num_transacoes: int


class ChartDataPoint(BaseModel):
    """Ponto de dados para gráfico"""
    date: str
    receitas: float
    despesas: float


class ChartDataResponse(BaseModel):
    """Dados para gráfico de área"""
    data: List[ChartDataPoint]


class CategoryExpense(BaseModel):
    """Despesa por categoria"""
    categoria: str
    total: float
    percentual: float
