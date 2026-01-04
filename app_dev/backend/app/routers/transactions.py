"""
Router para gerenciamento de transações financeiras
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import JournalEntry
from ..dependencies import get_current_user_id
from sqlalchemy import func, and_, or_

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

@router.get("/list")
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
    tipo_transacao: Optional[str] = Query(None),
    tipo_gasto: Optional[str] = Query(None),
    grupo: Optional[str] = Query(None),
    subgrupo: Optional[str] = Query(None),
    estabelecimento: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista transações com paginação e filtros"""
    try:
        # Query base
        query = db.query(JournalEntry)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.contains(search),
                    JournalEntry.GRUPO.contains(search),
                    JournalEntry.SUBGRUPO.contains(search)
                )
            )
        
        if tipo_transacao:
            query = query.filter(JournalEntry.TipoTransacao == tipo_transacao)
            
        if tipo_gasto:
            query = query.filter(JournalEntry.TipoGasto == tipo_gasto)
            
        if grupo:
            query = query.filter(JournalEntry.GRUPO == grupo)
            
        if subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == subgrupo)
            
        if estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento == estabelecimento)
            
        if year:
            query = query.filter(JournalEntry.Ano == year)
            
        if month:
            # Extrair mês da coluna Data (DD/MM/YYYY)
            query = query.filter(
                func.substr(JournalEntry.Data, 4, 2) == f"{month:02d}"
            )
        
        # Filtrar por ignorar dashboard se necessário
        # query = query.filter(JournalEntry.IgnorarDashboard == 0)
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * limit
        transactions = query.order_by(JournalEntry.id.desc()).offset(offset).limit(limit).all()
        
        # Converter para dict
        result = []
        for t in transactions:
            result.append({
                "id": t.id,
                "Data": t.Data,
                "Estabelecimento": t.Estabelecimento,
                "Valor": t.Valor,
                "ValorPositivo": t.ValorPositivo,
                "TipoTransacao": t.TipoTransacao,
                "TipoGasto": t.TipoGasto,
                "GRUPO": t.GRUPO,
                "SUBGRUPO": t.SUBGRUPO,
                "IdTransacao": t.IdTransacao,
                "MesFatura": t.MesFatura,
                "Ano": t.Ano,
                "arquivo_origem": t.arquivo_origem,
                "banco_origem": t.banco_origem,
                "NomeCartao": t.NomeCartao,
                "CategoriaGeral": t.CategoriaGeral,
                "IgnorarDashboard": t.IgnorarDashboard
            })
        
        return {
            "transactions": result,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_transaction_stats(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Estatísticas de transações"""
    try:
        query = db.query(JournalEntry)
        
        if year:
            query = query.filter(JournalEntry.Ano == year)
            
        if month:
            query = query.filter(
                func.substr(JournalEntry.Data, 4, 2) == f"{month:02d}"
            )
        
        # Contar por tipo
        total = query.count()
        receitas = query.filter(JournalEntry.TipoTransacao == "Receitas").count()
        despesas = query.filter(JournalEntry.TipoTransacao == "Despesas").count()
        
        # Somas
        soma_receitas = query.filter(JournalEntry.TipoTransacao == "Receitas").with_entities(func.sum(JournalEntry.Valor)).scalar() or 0
        soma_despesas = query.filter(JournalEntry.TipoTransacao == "Despesas").with_entities(func.sum(func.abs(JournalEntry.Valor))).scalar() or 0
        
        return {
            "total_transactions": total,
            "receitas_count": receitas,
            "despesas_count": despesas,
            "soma_receitas": float(soma_receitas),
            "soma_despesas": float(soma_despesas),
            "saldo": float(soma_receitas) - float(soma_despesas)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filtered-total")
async def get_filtered_total(
    search: Optional[str] = Query(None),
    tipo_transacao: Optional[str] = Query(None),
    tipo_gasto: Optional[str] = Query(None),
    grupo: Optional[str] = Query(None),
    subgrupo: Optional[str] = Query(None),
    estabelecimento: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna o total de todas as transações que atendem aos filtros"""
    try:
        # Query base (mesma lógica do /list)
        query = db.query(JournalEntry)
        
        # Aplicar os mesmos filtros da listagem
        if search:
            query = query.filter(
                or_(
                    JournalEntry.Estabelecimento.contains(search),
                    JournalEntry.GRUPO.contains(search),
                    JournalEntry.SUBGRUPO.contains(search)
                )
            )
        
        if tipo_transacao:
            query = query.filter(JournalEntry.TipoTransacao == tipo_transacao)
            
        if tipo_gasto:
            query = query.filter(JournalEntry.TipoGasto == tipo_gasto)
            
        if grupo:
            query = query.filter(JournalEntry.GRUPO == grupo)
            
        if subgrupo:
            query = query.filter(JournalEntry.SUBGRUPO == subgrupo)
            
        if estabelecimento:
            query = query.filter(JournalEntry.Estabelecimento == estabelecimento)
            
        if year:
            query = query.filter(JournalEntry.Ano == year)
            
        if month:
            # Extrair mês da coluna Data (DD/MM/YYYY)
            query = query.filter(
                func.substr(JournalEntry.Data, 4, 2) == f"{month:02d}"
            )
        
        # Calcular total filtrado
        total_filtrado = query.with_entities(func.sum(JournalEntry.Valor)).scalar() or 0
        count_filtrado = query.count()
        
        return {
            "total_filtrado": float(total_filtrado),
            "count_filtrado": count_filtrado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    updates: dict,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza uma transação específica"""
    try:
        # Buscar transação
        transaction = db.query(JournalEntry).filter(JournalEntry.IdTransacao == transaction_id).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transação não encontrada")
        
        # Aplicar atualizações
        for field, value in updates.items():
            if hasattr(transaction, field):
                setattr(transaction, field, value)
        
        db.commit()
        db.refresh(transaction)
        
        return {"message": "Transação atualizada com sucesso", "transaction_id": transaction_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/totals")
async def get_transaction_totals(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna totais globais de todas as transações"""
    try:
        # Totais sem filtros (todas as transações)
        total_receitas = db.query(func.sum(JournalEntry.Valor)).filter(JournalEntry.TipoTransacao == "Receitas").scalar() or 0
        total_despesas = db.query(func.sum(func.abs(JournalEntry.Valor))).filter(JournalEntry.TipoTransacao == "Despesas").scalar() or 0
        total_transacoes = db.query(JournalEntry).count()
        
        return {
            "total_receitas": float(total_receitas),
            "total_despesas": float(total_despesas), 
            "saldo": float(total_receitas) - float(total_despesas),
            "total_transacoes": total_transacoes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))