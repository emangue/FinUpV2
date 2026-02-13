"""
Budget Router
Endpoints FastAPI para gestão de orçamento

CHANGELOG 13/02/2026:
- ✅ Removidos imports obsoletos: BudgetGeral*, BudgetCategoriaConfig*
- ✅ Removidos endpoints /geral/* (consolidados em /planning)
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
    DetalhamentoMediaResponse
)

router = APIRouter()


# ===== ROTAS ESPECÍFICAS (strings fixas) - SEMPRE ANTES DAS PARAMETRIZADAS =====

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS REMOVIDOS EM 13/02/2026 - Consolidação completa
# ═══════════════════════════════════════════════════════════════════════════════
# - POST /budget/geral/bulk-upsert → usar /budget/planning/bulk-upsert
# - POST /budget/geral/bulk-upsert-validado → integrado ao planning
# - GET /budget/geral → usar /budget/planning
# - POST /budget/geral/copy-to-year → funcionalidade removida temporariamente
# - GET /budget/geral/grupos-disponiveis → usar API de grupos
#
# - GET /budget/categorias-config → removido (categorias fixas)
# - POST /budget/categorias-config → removido
# - PUT /budget/categorias-config/reordenar → removido
# - PATCH /budget/categorias-config/{id} → removido
# - PATCH /budget/categorias-config/{id}/tipos-gasto → removido
# - DELETE /budget/categorias-config/{id} → removido
#
# Se precisar restaurar, veja:
# git show HEAD~1:app_dev/backend/app/domains/budget/router.py
# ═══════════════════════════════════════════════════════════════════════════════

# ----- ROTAS DE DETALHAMENTO -----
def get_detalhamento_media(
    grupo: str = Query(..., description="Grupo para detalhamento"),
    mes_referencia: str = Query(..., description="Mês de referência no formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna detalhamento dos 3 meses anteriores que compõem a média
    
    - **grupo**: Nome do grupo (ex: "Casa", "Cartão")
    - **mes_referencia**: Mês planejado no formato YYYY-MM (ex: "2026-01")
    
    Retorna lista com cada um dos 3 meses anteriores contendo:
    - Nome do mês (ex: "Dezembro 2025")
    - Valor total do mês
    - Quantidade de transações
    
    Também retorna média calculada e total geral
    """
    service = BudgetService(db)
    return service.get_detalhamento_media(user_id, grupo, mes_referencia)


# ----- ROTAS DE DETALHAMENTO -----

@router.get("/budget/detalhamento-media", response_model=DetalhamentoMediaResponse, summary="Detalhamento da média dos 3 meses")
def get_detalhamento_media(
    grupo: str = Query(..., description="Grupo para detalhamento"),
    mes_referencia: str = Query(..., description="Mês de referência no formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna detalhamento dos 3 meses anteriores que compõem a média
    
    - **grupo**: Nome do grupo (ex: "Casa", "Cartão")
    - **mes_referencia**: Mês planejado no formato YYYY-MM (ex: "2026-01")
    
    Retorna lista com cada um dos 3 meses anteriores contendo:
    - Nome do mês (ex: "Dezembro 2025")
    - Valor total do mês
    - Quantidade de transações
    
    Também retorna média calculada e total geral
    """
    service = BudgetService(db)
    return service.get_detalhamento_media(user_id, grupo, mes_referencia)


@router.get("/budget/tipos-gasto-disponiveis", summary="Listar tipos de gasto disponíveis")
def listar_tipos_gasto_disponiveis(
    fonte_dados: str = Query(..., description="GRUPO ou TIPO_TRANSACAO"),
    filtro_valor: str = Query(..., description="Nome do grupo ou tipo de transação"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todos os tipos de gasto disponíveis para um grupo ou tipo de transação específico
    
    - **fonte_dados**: "GRUPO" ou "TIPO_TRANSACAO"
    - **filtro_valor**: Nome do grupo (ex: "Casa") ou tipo de transação (ex: "Cartão")
    
    Retorna lista de tipos de gasto únicos encontrados nas transações
    """
    service = BudgetService(db)
    return {"tipos_gasto": service.get_tipos_gasto_disponiveis(user_id, fonte_dados, filtro_valor)}


# ----- ROTAS DE BULK OPERATIONS -----
# ----- ROTAS DE BULK OPERATIONS -----

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


# ----- ROTAS DE BUDGET PLANNING -----
def get_budget_planning(
    mes_referencia: str = Query(..., description="Mês de referência no formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista metas de budget planning (tabela budget_planning, campo grupo)
    
    Diferente de /budget/geral (categoria_geral), este endpoint usa grupos:
    - Alimentação, Moradia, Transporte, etc.
    
    Query params:
    - mes_referencia: str (YYYY-MM)
    
    Returns:
    - mes_referencia: str
    - budgets: List[{grupo, valor_planejado, valor_realizado, percentual}]
    """
    service = BudgetService(db)
    return service.get_budget_planning(user_id, mes_referencia)


@router.post("/budget/planning/bulk-upsert", summary="Criar/atualizar múltiplas metas planning")
def bulk_upsert_budget_planning(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza múltiplas metas de planning de uma vez
    
    Body:
    - mes_referencia: str (YYYY-MM)
    - budgets: List[{grupo, valor_planejado}]
    
    Returns:
    - List[{id, grupo, mes_referencia, valor_planejado}]
    """
    service = BudgetService(db)
    return service.bulk_upsert_budget_planning(
        user_id, 
        data["mes_referencia"], 
        data["budgets"]
    )


# ----- ROTAS DE BUDGET PLANNING -----

@router.get("/budget/planning", summary="Listar metas de planning (grupos)")
def get_budget_planning(
    mes_referencia: str = Query(..., description="Mês de referência no formato YYYY-MM"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista metas de budget planning (tabela budget_planning, campo grupo)
    
    Diferente de /budget/geral (categoria_geral), este endpoint usa grupos:
    - Alimentação, Moradia, Transporte, etc.
    
    Query params:
    - mes_referencia: str (YYYY-MM)
    
    Returns:
    - mes_referencia: str
    - budgets: List[{grupo, valor_planejado, valor_realizado, percentual}]
    """
    service = BudgetService(db)
    return service.get_budget_planning(user_id, mes_referencia)


@router.post("/budget/planning/bulk-upsert", summary="Criar/atualizar múltiplas metas planning")
def bulk_upsert_budget_planning(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza múltiplas metas de planning de uma vez
    
    Body:
    - mes_referencia: str (YYYY-MM)
    - budgets: List[{grupo, valor_planejado}]
    
    Returns:
    - List[{id, grupo, mes_referencia, valor_planejado}]
    """
    service = BudgetService(db)
    return service.bulk_upsert_budget_planning(
        user_id, 
        data["mes_referencia"], 
        data["budgets"]
    )


@router.get("/budget/planning/grupos-disponiveis", response_model=List[str], summary="Listar grupos disponíveis")
def list_grupos_disponiveis(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os grupos disponíveis da base_grupos_config para despesas
    Útil para popular dropdowns de seleção
    """
    from app.domains.grupos.models import BaseGruposConfig
    
    grupos = db.query(BaseGruposConfig.nome_grupo).filter(
        BaseGruposConfig.categoria_geral == 'Despesa'
    ).order_by(BaseGruposConfig.nome_grupo).all()
    
    return [g[0] for g in grupos]


# ----- ROTAS DE BUDGET DETALHADO -----
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


@router.patch("/budget/planning/toggle/{budget_id}", summary="Toggle ativo/inativo de uma meta")
def toggle_budget_ativo(
    budget_id: int,
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Ativa ou desativa uma meta (alterna campo 'ativo')
    
    Body: {"ativo": true/false}
    
    IMPORTANTE: NÃO zera valor_planejado - apenas muda status
    """
    service = BudgetService(db)
    ativo_value = 1 if data.get("ativo") else 0
    return service.toggle_budget_ativo(budget_id, user_id, ativo_value)


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


# ===== ROTAS PARAMETRIZADAS (SEMPRE POR ÚLTIMO) =====

@router.get("/budget/{budget_id}", response_model=BudgetResponse, summary="Buscar budget")
def get_budget(
    budget_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Busca budget por ID"""
    service = BudgetService(db)
    return service.get_budget(budget_id, user_id)
