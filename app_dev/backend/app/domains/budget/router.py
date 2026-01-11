"""
Budget Router
Endpoints FastAPI para gestão de orçamento
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import BudgetService
from .schemas import (
    BudgetCreate, 
    BudgetUpdate, 
    BudgetResponse, 
    BudgetListResponse,
    BudgetBulkUpsert,
    BudgetGeralBulkUpsert
)

router = APIRouter()


@router.get("/budget", response_model=BudgetListResponse, summary="Listar budgets")
def list_budgets(
    mes_referencia: str = Query(None, description="Filtrar por mês (formato YYYY-MM)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista budgets do usuário
    
    - Se mes_referencia for informado, retorna apenas daquele mês
    - Se não, retorna todos os budgets
    """
    service = BudgetService(db)
    
    if mes_referencia:
        budgets = service.get_budgets_by_month(user_id, mes_referencia)
        return {"budgets": budgets, "total": len(budgets)}
    else:
        return service.get_all_budgets(user_id)


@router.get("/budget/month/{mes_referencia}", response_model=List[BudgetResponse], summary="Budgets por mês")
def get_budgets_by_month(
    mes_referencia: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista budgets de um mês específico
    
    - **mes_referencia**: Formato YYYY-MM (ex: 2025-11)
    """
    service = BudgetService(db)
    return service.get_budgets_by_month(user_id, mes_referencia)


@router.get("/budget/{budget_id}", response_model=BudgetResponse, summary="Buscar budget")
def get_budget(
    budget_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Busca budget por ID"""
    service = BudgetService(db)
    return service.get_budget(budget_id, user_id)


@router.post("/budget", response_model=BudgetResponse, status_code=201, summary="Criar budget")
def create_budget(
    data: BudgetCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cria novo budget"""
    service = BudgetService(db)
    return service.create_budget(user_id, data)


@router.put("/budget/{budget_id}", response_model=BudgetResponse, summary="Atualizar budget")
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Atualiza budget existente"""
    service = BudgetService(db)
    return service.update_budget(budget_id, user_id, data)


@router.delete("/budget/{budget_id}", status_code=204, summary="Deletar budget")
def delete_budget(
    budget_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deleta budget"""
    service = BudgetService(db)
    service.delete_budget(budget_id, user_id)
    return None


@router.post("/budget/bulk-upsert", response_model=List[BudgetResponse], summary="Criar/atualizar múltiplos budgets")
def bulk_upsert_budgets(
    data: BudgetBulkUpsert,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza múltiplos budgets de uma vez
    
    Útil para salvar todo o orçamento de um mês de uma só vez
    """
    service = BudgetService(db)
    return service.bulk_upsert_budgets(user_id, data.mes_referencia, data.budgets)


# ===== ROTAS PARA META GERAL =====

@router.get("/budget/geral", response_model=BudgetListResponse, summary="Listar metas gerais")
def list_budget_geral(
    mes_referencia: str = Query(None, description="Filtrar por mês (formato YYYY-MM)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista metas gerais do usuário por categoria ampla
    
    - Se mes_referencia for informado, retorna apenas daquele mês
    - Se não, retorna todas as metas gerais
    """
    service = BudgetService(db)
    
    if mes_referencia:
        budgets = service.get_budget_geral_by_month(user_id, mes_referencia)
        return {"budgets": budgets, "total": len(budgets)}
    else:
        return service.get_all_budget_geral(user_id)


@router.post("/budget/geral/bulk-upsert", response_model=List[BudgetResponse], summary="Criar/atualizar múltiplas metas gerais")
def bulk_upsert_budget_geral(
    data: BudgetGeralBulkUpsert,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza múltiplas metas gerais de uma vez
    
    Útil para salvar todo o orçamento geral de um mês
    """
    service = BudgetService(db)
    return service.bulk_upsert_budget_geral(user_id, data.mes_referencia, data.budgets)

