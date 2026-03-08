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
from app.domains.plano.service import PlanoService
from app.domains.investimentos.service import InvestimentoService
from .schemas import (
    DashboardMetrics, 
    ChartDataResponse, 
    CategoryExpense,
    BudgetVsActualResponse,
    CreditCardExpense,
    IncomeSourcesResponse,
    OrcamentoInvestimentosResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/last-month-with-data")
def get_last_month_with_data(
    source: str = Query(default="transactions", description="transactions ou patrimonio"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna o último mês com dados (ano e mês) para o usuário.
    source: transactions=journal_entries, patrimonio=investimentos_historico
    """
    service = DashboardService(db)
    return service.get_last_month_with_data(user_id, source)


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: Optional[int] = Query(default=None, description="Mês (1-12) ou None = ano todo / YTD)"),
    ytd_month: Optional[int] = Query(default=None, description="YTD: mês limite (1-12). Se informado com month=None, soma Jan..ytd_month"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas principais do dashboard.
    Se month=None e ytd_month informado: soma Jan..ytd_month (YTD).
    Se month=None e ytd_month=None: ano inteiro.
    """
    now = datetime.now()
    year = year or now.year
    
    service = DashboardService(db)
    return service.get_metrics(user_id, year, month, ytd_month)


@router.get("/chart-data", response_model=ChartDataResponse)
def get_chart_data(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: atual)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna dados para gráfico de área:
    - Receitas e despesas por mês (12 meses até o mês especificado)
    """
    # Usar mês/ano atual se não informado
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    
    service = DashboardService(db)
    return service.get_chart_data(user_id, year, month)


@router.get("/chart-data-yearly", response_model=ChartDataResponse)
def get_chart_data_yearly(
    years: str = Query(..., description="Anos separados por vírgula (ex: 2023,2024,2025)"),
    ytd_month: Optional[int] = Query(None, description="Mês limite para YTD (1-12). Se None, ano inteiro"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna dados para gráfico por ano:
    - years: lista de anos (ex: 2023,2024,2025)
    - ytd_month: se informado, soma Jan..ytd_month de cada ano (YTD)
    - Se ytd_month=None, soma o ano inteiro
    """
    year_list = [int(y.strip()) for y in years.split(",") if y.strip()]
    if not year_list:
        raise HTTPException(status_code=400, detail="years é obrigatório")
    
    service = DashboardService(db)
    return service.get_chart_data_yearly(user_id, year_list, ytd_month)


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


@router.get("/subgrupos-by-tipo")
def get_subgrupos_by_tipo(
    year: int = Query(..., description="Ano"),
    month: Optional[int] = Query(None, description="Mês (1-12) ou None para YTD"),
    grupo: str = Query(..., description="Grupo"),
    ytd: bool = Query(False, description="Year to Date - soma de todos os meses do ano"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna subgrupos de um grupo específico com valores e percentuais.
    """
    service = DashboardService(db)
    
    # Se ytd=True, passar None como month para buscar ano todo
    if ytd:
        month = None
    
    return service.get_subgrupos_by_tipo(user_id, year, month, grupo)


@router.get("/credit-cards", response_model=list[CreditCardExpense])
def get_credit_card_expenses(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: None = ano todo)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna gastos agrupados por cartão de crédito:
    - Nome do cartão
    - Total gasto
    - Percentual do total
    - Número de transações
    
    Se month=None, retorna soma do ano inteiro.
    Apenas transações com NomeCartao não nulo.
    """
    # Usar ano atual se não informado
    now = datetime.now()
    year = year or now.year
    # month pode ser None (ano todo) ou número específico
    
    service = DashboardService(db)
    return service.get_credit_card_expenses(user_id, year, month)


@router.get("/orcamento-investimentos", response_model=OrcamentoInvestimentosResponse)
def get_orcamento_investimentos(
    year: int = Query(..., description="Ano"),
    month: Optional[int] = Query(None, description="Mês (1-12) ou None = ano/YTD"),
    ytd_month: Optional[int] = Query(None, description="YTD: mês limite (1-12). Se month=None e ytd_month informado, soma Jan..ytd_month"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Investimentos vs Plano: total investido (journal) e planejado (budget).
    month=None e ytd_month informado: YTD (Jan..ytd_month).
    month=None e ytd_month=None: ano inteiro.
    """
    service = DashboardService(db)
    return service.get_orcamento_investimentos(user_id, year, month, ytd_month)


@router.get("/income-sources", response_model=IncomeSourcesResponse)
def get_income_sources(
    year: int = Query(default=None, description="Ano (default: atual)"),
    month: int = Query(default=None, description="Mês (default: None = ano todo)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna breakdown de receitas por fonte (grupo):
    - Nome da fonte (grupo)
    - Total de receitas
    - Percentual do total
    - Número de transações
    
    Se month=None, retorna soma do ano inteiro.
    Apenas transações com CategoriaGeral='Receita'.
    """
    # Usar ano atual se não informado
    now = datetime.now()
    year = year or now.year
    # month pode ser None (ano todo) ou número específico
    
    service = DashboardService(db)
    return service.get_income_sources(user_id, year, month)


@router.get("/summary")
def dashboard_summary(
    year: int = Query(..., description="Ano"),
    month: int = Query(..., description="Mês (1-12)"),
    ytd_month: Optional[int] = Query(None, description="YTD: mês limite (1-12). Se informado com month, usado em seções que suportam YTD"),
    sections: Optional[str] = Query(
        default="metrics,chart,income-sources,budget-vs-actual,credit-cards,orcamento-investimentos,cashflow-mes,aporte-mes",
        description="Seções a incluir, separadas por vírgula",
    ),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Endpoint agregado: consolida múltiplos dados do dashboard em 1 request.

    Aceita ?sections= para retornar apenas o necessário (subset do padrão).
    Seções disponíveis: metrics, chart, chart-yearly, income-sources,
    budget-vs-actual, credit-cards, orcamento-investimentos, cashflow-mes, aporte-mes.

    Campos ausentes na resposta = seção não solicitada (nunca null).
    """
    requested = set(sections.split(",")) if sections else set()
    result: dict = {}

    dashboard_svc = DashboardService(db)

    if "metrics" in requested:
        result["metrics"] = dashboard_svc.get_metrics(user_id, year, month, ytd_month)

    if "chart" in requested:
        result["chart"] = dashboard_svc.get_chart_data(user_id, year, month)

    if "chart-yearly" in requested:
        current_year = datetime.now().year
        years = [current_year - 2, current_year - 1, current_year]
        result["chart_yearly"] = dashboard_svc.get_chart_data_yearly(user_id, years, ytd_month)

    if "income-sources" in requested:
        result["income_sources"] = dashboard_svc.get_income_sources(user_id, year, month)

    if "budget-vs-actual" in requested:
        result["budget_vs_actual"] = dashboard_svc.get_budget_vs_actual(user_id, year, month)

    if "credit-cards" in requested:
        result["credit_cards"] = dashboard_svc.get_credit_card_expenses(user_id, year, month)

    if "orcamento-investimentos" in requested:
        result["orcamento_investimentos"] = dashboard_svc.get_orcamento_investimentos(
            user_id, year, month, ytd_month
        )

    if "cashflow-mes" in requested:
        try:
            plano_svc = PlanoService(db)
            cashflow = plano_svc.get_cashflow(user_id, year)
            meses = cashflow.get("meses", []) if isinstance(cashflow, dict) else []
            mes_ref = f"{year}-{str(month).zfill(2)}"
            result["cashflow_mes"] = next(
                (m for m in meses if m.get("mes_referencia") == mes_ref), None
            )
        except Exception:
            result["cashflow_mes"] = None

    if "aporte-mes" in requested:
        try:
            inv_svc = InvestimentoService(db)
            aporte = inv_svc.get_aporte_principal_por_mes(user_id, year, month)
            result["aporte_mes"] = {"aporte": aporte or 0}
        except Exception:
            result["aporte_mes"] = {"aporte": 0}

    return result

