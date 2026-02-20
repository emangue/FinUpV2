"""
Domínio Transactions - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
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

@router.get("/grupo-breakdown", summary="Breakdown de todos os grupos por período")
def get_grupo_breakdown(
    data_inicio: str = Query(..., description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna breakdown de gastos por grupo em um período
    
    Query params:
    - data_inicio: Data início (ex: "2026-01-01")
    - data_fim: Data fim (ex: "2026-01-31")
    
    Returns:
    - grupos: dict com {grupo: {total, transacoes}}
    """
    service = TransactionService(db)
    return service.get_all_grupos_breakdown(user_id, data_inicio, data_fim)

@router.get("/receitas-despesas", summary="Total de receitas, despesas e investimentos por período")
def get_receitas_despesas(
    data_inicio: str = Query(..., description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna total de receitas, despesas e investimentos em um período
    
    Query params:
    - data_inicio: Data início (ex: "2026-01-01")
    - data_fim: Data fim (ex: "2026-01-31")
    
    Returns:
    - receitas: float (CategoriaGeral = 'Receita')
    - despesas: float (CategoriaGeral = 'Despesa')
    - investimentos: float (CategoriaGeral = 'Investimentos', valores negativos = aplicações)
    - saldo: float (receitas - despesas - investimentos)
    """
    service = TransactionService(db)
    return service.get_receitas_despesas(user_id, data_inicio, data_fim)

@router.get("/grupo-breakdown-single", summary="Breakdown de subgrupos por grupo")
def get_grupo_breakdown_single(
    grupo: str = Query(..., description="Nome do grupo (ex: Cartão de Crédito)"),
    year: int = Query(..., description="Ano"),
    month: int = Query(..., description="Mês"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna breakdown de subgrupos de um grupo específico
    
    Query params:
    - grupo: Nome do grupo (ex: "Cartão de Crédito", "Casa")
    - year: Ano (ex: 2026)
    - month: Mês (ex: 2)
    
    Returns:
    - grupo: str
    - total: float
    - subgrupos: List[{subgrupo, valor, percentual, quantidade_transacoes}]
    """
    service = TransactionService(db)
    return service.get_grupo_breakdown(user_id, grupo, year, month)

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
    subgrupo_null: Optional[bool] = Query(None, description="Filtrar transações sem subgrupo (SUBGRUPO IS NULL)"),
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
        subgrupo_null=subgrupo_null,
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
    subgrupo_null: Optional[bool] = Query(None),
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
        subgrupo_null=subgrupo_null,
        estabelecimento=estabelecimento,
        search=search,
        cartao=cartao
    )
    
    return service.get_filtered_total(user_id, filters)


class PropagateInfoResponse(BaseModel):
    """Info para propagação de grupo/subgrupo"""
    same_parcela_count: int = 0  # Outras transações com mesmo IdParcela (excluindo esta)
    has_padrao: bool = False    # Existe padrão em base_padroes para esta transação
    same_padrao_count: int = 0  # Transações que batem no mesmo padrão (excluindo esta)


@router.get("/propagate-info/{transaction_id}", response_model=PropagateInfoResponse)
def get_propagate_info(
    transaction_id: str,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna quantas transações seriam afetadas ao propagar grupo/subgrupo.
    Usado para exibir opção "Atualizar em todas as X parcelas" ou "Atualizar em todas com este padrão".
    """
    service = TransactionService(db)
    return service.get_propagate_info(transaction_id, user_id)


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
