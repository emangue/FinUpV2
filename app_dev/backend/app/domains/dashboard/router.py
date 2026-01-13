"""
Domínio Dashboard - Router
Endpoints HTTP para métricas e estatísticas
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import DashboardService
from .schemas import (
    DashboardMetrics, 
    ChartDataResponse, 
    CategoryExpense,
    BudgetVsActualResponse
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: None = ano todo)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas principais do dashboard:
    - Total de despesas
    - Total de receitas
    - Total de cartões
    - Saldo do período
    - Número de transações
    
    Se month=None, retorna soma do ano inteiro.
    """
    # Usar ano atual se não informado
    now = datetime.now()
    year = year or now.year
    # month pode ser None (ano todo) ou número específico
    
    service = DashboardService(db)
    return service.get_metrics(user_id, year, month)


@router.get("/chart-data", response_model=ChartDataResponse)
def get_chart_data(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: atual)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna dados para gráfico de área:
    - Receitas e despesas por dia do mês
    """
    # Usar mês/ano atual se não informado
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    
    service = DashboardService(db)
    return service.get_chart_data(user_id, year, month)


@router.get("/categories", response_model=list[CategoryExpense])
def get_category_expenses(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: None = ano todo)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna despesas agrupadas por categoria:
    - Nome da categoria
    - Total gasto
    - Percentual do total
    
    Se month=None, retorna soma do ano inteiro.
    """
    # Usar ano atual se não informado
    now = datetime.now()
    year = year or now.year
    # month pode ser None (ano todo) ou número específico
    
    service = DashboardService(db)
    return service.get_category_expenses(user_id, year, month)


@router.get("/budget-vs-actual", response_model=BudgetVsActualResponse)
def get_budget_vs_actual(
    year: int = Query(..., description="Ano"),
    month: Optional[int] = Query(None, description="Mês (1-12) ou None para YTD"),
    ytd: bool = Query(False, description="Year to Date - soma de todos os meses do ano"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna comparação Realizado vs Planejado por TipoGasto:
    - tipo_gasto
    - realizado (valor gasto)
    - planejado (valor orçado)
    - percentual (realizado/planejado * 100)
    - diferenca (realizado - planejado)
    
    Se ytd=True, retorna soma de todo o ano até a data atual.
    Também retorna totais gerais e percentual geral.
    """
    service = DashboardService(db)
    
    # Se ytd=True, passar None como month para buscar ano todo
    if ytd:
        return service.get_budget_vs_actual(user_id, year, None)
    
    # Se month não for fornecido, retornar erro
    if month is None:
        raise HTTPException(status_code=400, detail="month é obrigatório quando ytd=False")
    
    return service.get_budget_vs_actual(user_id, year, month)
