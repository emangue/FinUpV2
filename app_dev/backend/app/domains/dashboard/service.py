"""
Domínio Dashboard - Service
Lógica de negócio para dashboard
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from .repository import DashboardRepository
from .schemas import (
    DashboardMetrics, 
    ChartDataResponse, 
    CategoryExpense, 
    ChartDataPoint,
    BudgetVsActualResponse,
    BudgetVsActualItem,
    CreditCardExpense,
    IncomeSource,
    IncomeSourcesResponse,
    OrcamentoInvestimentosResponse,
    OrcamentoInvestimentosItem,
)


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)
    
    def get_last_month_with_data(self, user_id: int, source: str = "transactions"):
        """Retorna o último mês com dados (ano e mês). source: transactions ou patrimonio"""
        result = self.repository.get_last_month_with_data(user_id, source)
        return result
    
    def get_metrics(
        self,
        user_id: int,
        year: int,
        month: int = None,
        ytd_month: int = None
    ) -> DashboardMetrics:
        """Retorna métricas principais do dashboard
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro / YTD
            ytd_month: Se informado com month=None, soma Jan..ytd_month (YTD)
        """
        data = self.repository.get_metrics(user_id, year, month, ytd_month)
        return DashboardMetrics(**data)
    
    def get_chart_data(self, user_id: int, year: int, month: int) -> ChartDataResponse:
        """Retorna dados para gráfico de área"""
        data = self.repository.get_chart_data(user_id, year, month)
        chart_points = [ChartDataPoint(**point) for point in data]
        return ChartDataResponse(data=chart_points)
    
    def get_chart_data_yearly(
        self,
        user_id: int,
        years: List[int],
        ytd_month: Optional[int] = None
    ) -> ChartDataResponse:
        """Retorna dados para gráfico por ano (YTD ou ano inteiro)"""
        data = self.repository.get_chart_data_yearly(user_id, years, ytd_month)
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
    
    def get_subgrupos_by_tipo(self, user_id: int, year: int, month: int, grupo: str):
        """Retorna subgrupos de um grupo específico"""
        data = self.repository.get_subgrupos_by_tipo(user_id, year, month, grupo)
        total_planejado = self.repository.get_planejado_by_tipo(user_id, year, month, grupo)
        return {
            "subgrupos": data,
            "total_realizado": sum(item["valor"] for item in data),
            "total_planejado": total_planejado
        }
    
    def get_credit_card_expenses(self, user_id: int, year: int, month: int = None) -> list[CreditCardExpense]:
        """Retorna despesas por cartão de crédito
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        data = self.repository.get_credit_card_expenses(user_id, year, month)
        return [CreditCardExpense(**expense) for expense in data]
    
    def get_income_sources(self, user_id: int, year: int, month: int = None) -> IncomeSourcesResponse:
        """Retorna breakdown de receitas por fonte
        
        Args:
            user_id: ID do usuário
            year: Ano a filtrar
            month: Mês específico (1-12) ou None para ano inteiro
        """
        data = self.repository.get_income_sources(user_id, year, month)
        sources = [IncomeSource(**source) for source in data]
        total_receitas = sum(s.total for s in sources)
        
        return IncomeSourcesResponse(
            sources=sources,
            total_receitas=total_receitas
        )

    def get_orcamento_investimentos(
        self,
        user_id: int,
        year: int,
        month: int = None,
        ytd_month: int = None
    ) -> OrcamentoInvestimentosResponse:
        """Investimentos vs Plano: realizado vs planejado (ano, mês ou YTD)"""
        data = self.repository.get_orcamento_investimentos(user_id, year, month, ytd_month)
        items = [OrcamentoInvestimentosItem(**i) for i in data["items"]]
        return OrcamentoInvestimentosResponse(
            total_investido=data["total_investido"],
            total_planejado=data["total_planejado"],
            items=items
        )

