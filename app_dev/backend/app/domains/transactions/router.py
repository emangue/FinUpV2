"""
Domínio Transactions - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import TransactionService
from .schemas import (
    TransactionResponse,
    TransactionCreate,
    TransactionUpdate,
    TransactionListResponse,
    TransactionFilters,
    TiposGastoComMediaResponse
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/tipos-gasto-com-media", response_model=TiposGastoComMediaResponse)
def get_tipos_gasto_com_media(
    mes_referencia: str = Query(..., description="Formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna tipos de gasto únicos de Despesa com média dos últimos 3 meses
    """
    service = TransactionService(db)
    return service.get_tipos_gasto_com_media(user_id, mes_referencia)

@router.get("/list", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    year: Optional[int] = None,
    month: Optional[int] = None,
    estabelecimento: Optional[str] = None,
    grupo: Optional[str] = None,
    subgrupo: Optional[str] = None,
    tipo: Optional[str] = None,
    categoria_geral: Optional[str] = None,
    tipo_gasto: Optional[str] = None,
    cartao: Optional[str] = None,
    search: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista transações com filtros e paginação
    """
    service = TransactionService(db)
    
    filters = TransactionFilters(
        year=year,
        month=month,
        estabelecimento=estabelecimento,
        grupo=grupo,
        subgrupo=subgrupo,
        tipo=tipo,
        categoria_geral=categoria_geral,
        tipo_gasto=tipo_gasto,
        cartao=cartao,
        search=search
    )
    
    return service.list_transactions(user_id, filters, page, limit)

@router.get("/tipos-gasto-com-media", response_model=TiposGastoComMediaResponse)
def get_tipos_gasto_com_media(
    mes_referencia: str = Query(..., description="Formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna tipos de gasto únicos de Despesa com média dos últimos 3 meses
    """
    service = TransactionService(db)
    return service.get_tipos_gasto_com_media(user_id, mes_referencia)

@router.get("/filtered-total")
def get_filtered_total(
    year: Optional[int] = None,
    month: Optional[int] = None,
    tipo: Optional[str] = None,
    categoria_geral: Optional[str] = None,
    tipo_gasto: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna soma total de valores com filtros
    """
    service = TransactionService(db)
    
    filters = TransactionFilters(year=year, month=month, tipo=tipo, categoria_geral=categoria_geral, tipo_gasto=tipo_gasto)
    
    return service.get_filtered_total(user_id, filters)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Busca transação por ID
    """
    service = TransactionService(db)
    return service.get_transaction(transaction_id, user_id)

@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """
    Cria nova transação
    """
    service = TransactionService(db)
    return service.create_transaction(transaction)

@router.patch("/update/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza transação
    """
    service = TransactionService(db)
    return service.update_transaction(transaction_id, user_id, update_data)

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Deleta transação
    """
    service = TransactionService(db)
    return service.delete_transaction(transaction_id, user_id)
