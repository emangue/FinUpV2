"""
Domínio Transactions - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

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
from .schemas_migration import (
    MigrationPreviewRequest,
    MigrationPreviewResponse,
    MigrationExecuteRequest,
    MigrationExecuteResponse,
    GrupoSubgrupoListResponse
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
    
    ⚠️ DEPRECATED: Use /grupos-com-media para nova estrutura
    """
    service = TransactionService(db)
    return service.get_tipos_gasto_com_media(user_id, mes_referencia)

@router.get("/grupos-com-media", response_model=TiposGastoComMediaResponse)
def get_grupos_com_media(
    mes_referencia: str = Query(..., description="Formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna grupos únicos de Despesa com média dos últimos 3 meses
    
    ✅ Nova estrutura usando grupos em vez de tipos de gasto
    """
    service = TransactionService(db)
    return service.get_grupos_com_media(user_id, mes_referencia)

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
    tipo_gasto: Optional[List[str]] = Query(None),  # Aceita múltiplos valores
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
    tipo_gasto: Optional[List[str]] = Query(None),  # Aceita múltiplos valores
    grupo: Optional[str] = None,
    subgrupo: Optional[str] = None,
    estabelecimento: Optional[str] = None,
    search: Optional[str] = None,
    cartao: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna soma total de valores com filtros
    """
    service = TransactionService(db)
    
    filters = TransactionFilters(
        year=year, 
        month=month, 
        tipo=tipo, 
        categoria_geral=categoria_geral, 
        tipo_gasto=tipo_gasto,
        grupo=grupo,
        subgrupo=subgrupo,
        estabelecimento=estabelecimento,
        search=search,
        cartao=cartao
    )
    
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


# ==================== ENDPOINTS DE MIGRAÇÃO EM MASSA ====================

@router.get("/migration/grupos-subgrupos", response_model=GrupoSubgrupoListResponse)
def list_grupos_subgrupos(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todos os grupos/subgrupos disponíveis para migração
    """
    service = TransactionService(db)
    return service.get_grupos_subgrupos_disponiveis(user_id)


@router.post("/migration/preview", response_model=MigrationPreviewResponse)
def preview_migration(
    request: MigrationPreviewRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Preview de quantas transações serão impactadas pela migração
    """
    service = TransactionService(db)
    return service.preview_migration(
        user_id,
        request.grupo_origem,
        request.subgrupo_origem,
        request.grupo_destino,
        request.subgrupo_destino
    )


@router.post("/migration/execute", response_model=MigrationExecuteResponse)
def execute_migration(
    request: MigrationExecuteRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Executa migração em massa de transações
    Atualiza GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral
    Recalcula médias no budget_planning
    """
    service = TransactionService(db)
    return service.execute_migration(
        user_id,
        request.grupo_origem,
        request.subgrupo_origem,
        request.grupo_destino,
        request.subgrupo_destino
    )
