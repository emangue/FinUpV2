"""
Router de Dashboard
Endpoints para métricas e estatísticas
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from typing import Optional, List
from collections import defaultdict
from datetime import datetime

from ..database import get_db
from ..models import JournalEntry, User
from ..schemas import DashboardMetrics, CategoryStats
from .auth import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    year: int = Query(2025),
    month: Optional[str] = Query("all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas do dashboard
    
    Params:
        year: Ano (2025)
        month: Mês (01-12 ou 'all')
    """
    # Query base
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.IgnorarDashboard == 0
    )
    
    # Filtro de ano
    if year:
        query = query.filter(JournalEntry.MesFatura.like(f"{year}%"))
    
    # Filtro de mês
    if month and month != "all":
        mes_fatura = f"{year}{month.zfill(2)}"
        query = query.filter(JournalEntry.MesFatura == mes_fatura)
    
    transacoes = query.all()
    
    # Calcular métricas
    total_despesas = 0.0
    total_receitas = 0.0
    por_tipo_gasto = defaultdict(lambda: {"total": 0.0, "quantidade": 0})
    evolucao_mensal = defaultdict(lambda: {"despesas": 0.0, "receitas": 0.0})
    
    for t in transacoes:
        # Despesas vs Receitas
        if t.TipoTransacao in ["Despesas", "Cartão de Crédito"]:
            total_despesas += abs(t.Valor)
            evolucao_mensal[t.MesFatura]["despesas"] += abs(t.Valor)
        elif t.TipoTransacao == "Receitas":
            total_receitas += abs(t.Valor)
            evolucao_mensal[t.MesFatura]["receitas"] += abs(t.Valor)
        
        # Por tipo de gasto
        if t.TipoGasto:
            por_tipo_gasto[t.TipoGasto]["total"] += abs(t.Valor)
            por_tipo_gasto[t.TipoGasto]["quantidade"] += 1
    
    # Formatar por_tipo_gasto
    tipos_formatados = [
        {
            "TipoGasto": tipo,
            "total": dados["total"],
            "quantidade": dados["quantidade"]
        }
        for tipo, dados in sorted(
            por_tipo_gasto.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
    ]
    
    # Formatar evolução mensal
    evolucao_formatada = [
        {
            "mes": mes,
            "mes_nome": f"{mes[4:6]}/{mes[:4]}",  # MM/YYYY
            "despesas": dados["despesas"],
            "receitas": dados["receitas"]
        }
        for mes, dados in sorted(evolucao_mensal.items())
    ]
    
    return {
        "total_despesas": total_despesas,
        "total_receitas": total_receitas,
        "saldo": total_receitas - total_despesas,
        "total_transacoes": len(transacoes),
        "por_tipo_gasto": tipos_formatados,
        "evolucao_mensal": evolucao_formatada
    }

@router.get("/categories")
def get_categories_stats(
    year: int = Query(2025),
    month: Optional[str] = Query("all"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas por categoria (TipoGasto)
    
    Compatível com o endpoint atual do Next.js
    """
    # Query base
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.IgnorarDashboard == 0,
        JournalEntry.TipoGasto.isnot(None),
        JournalEntry.TipoTransacao.in_(["Despesas", "Cartão de Crédito"])
    )
    
    # Filtros
    if year:
        query = query.filter(JournalEntry.MesFatura.like(f"{year}%"))
    
    if month and month != "all":
        mes_fatura = f"{year}{month.zfill(2)}"
        query = query.filter(JournalEntry.MesFatura == mes_fatura)
    
    # Agrupar por TipoGasto
    results = db.query(
        JournalEntry.TipoGasto,
        func.sum(func.abs(JournalEntry.Valor)).label("total"),
        func.count(JournalEntry.id).label("quantidade")
    ).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.IgnorarDashboard == 0,
        JournalEntry.TipoGasto.isnot(None),
        JournalEntry.TipoTransacao.in_(["Despesas", "Cartão de Crédito"]),
        JournalEntry.MesFatura.like(f"{year}%") if year else True
    )
    
    if month and month != "all":
        mes_fatura = f"{year}{month.zfill(2)}"
        results = results.filter(JournalEntry.MesFatura == mes_fatura)
    
    results = results.group_by(JournalEntry.TipoGasto).all()
    
    # Calcular total geral
    total_geral = sum(r.total for r in results)
    
    # Formatar resposta
    categorias = [
        {
            "TipoGasto": r.TipoGasto,
            "total": round(r.total, 2),
            "quantidade": r.quantidade,
            "percentual": round((r.total / total_geral * 100) if total_geral > 0 else 0, 1)
        }
        for r in sorted(results, key=lambda x: x.total, reverse=True)
    ]
    
    return categorias

@router.get("/chart/receitas-despesas")
def get_receitas_despesas_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados para o gráfico de evolução de receitas e despesas
    
    Últimos 6 meses
    """
    # Busca últimos 6 meses de transações
    query = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id,
        JournalEntry.IgnorarDashboard == 0
    ).order_by(JournalEntry.MesFatura.desc())
    
    transacoes = query.all()
    
    # Agrupar por mês
    meses_data = defaultdict(lambda: {"despesas": 0.0, "receitas": 0.0})
    
    for t in transacoes:
        mes = t.MesFatura
        if not mes:
            continue
        
        if t.TipoTransacao in ["Despesas", "Cartão de Crédito"]:
            meses_data[mes]["despesas"] += abs(t.Valor)
        elif t.TipoTransacao == "Receitas":
            meses_data[mes]["receitas"] += abs(t.Valor)
    
    # Formatar para resposta (últimos 6 meses)
    meses_ordenados = sorted(meses_data.keys(), reverse=True)[:6]
    meses_ordenados.reverse()  # Mais antigo → mais recente
    
    resultado = [
        {
            "mes": mes,
            "mes_nome": f"{mes[4:6]}/{mes[:4]}",  # MM/YYYY
            "despesas": round(meses_data[mes]["despesas"], 2),
            "receitas": round(meses_data[mes]["receitas"], 2)
        }
        for mes in meses_ordenados
    ]
    
    return resultado
