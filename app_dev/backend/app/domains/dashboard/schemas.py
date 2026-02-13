"""
Domínio Dashboard - Schemas Pydantic
"""
from pydantic import BaseModel
from typing import List, Optional


class DashboardMetrics(BaseModel):
    """Métricas principais do dashboard"""
    total_despesas: float
    total_receitas: float
    total_cartoes: float
    saldo_periodo: float
    num_transacoes: int
    change_percentage: Optional[float] = None  # Variação % vs mês anterior (se disponível)


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


class BudgetVsActualItem(BaseModel):
    """Comparação Realizado vs Planejado por Grupo"""
    grupo: str
    realizado: float
    planejado: float
    percentual: float  # (realizado / planejado) * 100
    diferenca: float   # realizado - planejado


class BudgetVsActualResponse(BaseModel):
    """Resposta completa de Budget vs Actual"""
    items: List[BudgetVsActualItem]
    total_realizado: float
    total_planejado: float
    percentual_geral: float  # (total_realizado / total_planejado) * 100


class CreditCardExpense(BaseModel):
    """Despesa por cartão de crédito"""
    cartao: str
    total: float
    percentual: float
    num_transacoes: int


class IncomeSource(BaseModel):
    """Receita por fonte (grupo)"""
    fonte: str
    total: float
    percentual: float
    num_transacoes: int


class IncomeSourcesResponse(BaseModel):
    """Lista de fontes de receita"""
    sources: List[IncomeSource]
    total_receitas: float
