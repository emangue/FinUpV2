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
    change_percentage: Optional[float] = None  # Despesas vs mês anterior
    receitas_change_percentage: Optional[float] = None  # Receitas vs mês anterior
    despesas_vs_plano_percent: Optional[float] = None  # Despesas vs plano (quando há orçamento)
    ativos_mes: Optional[float] = None
    passivos_mes: Optional[float] = None
    patrimonio_liquido_mes: Optional[float] = None
    ativos_change_percentage: Optional[float] = None
    passivos_change_percentage: Optional[float] = None
    patrimonio_change_percentage: Optional[float] = None
    patrimonio_vs_plano_percent: Optional[float] = None


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


class OrcamentoInvestimentosItem(BaseModel):
    """Item de Investimentos vs Plano"""
    grupo: str
    valor: float  # investido (realizado)
    plano: float  # planejado


class OrcamentoInvestimentosResponse(BaseModel):
    """Resposta de orçamento investimentos vs plano"""
    total_investido: float
    total_planejado: float
    items: List[OrcamentoInvestimentosItem]
