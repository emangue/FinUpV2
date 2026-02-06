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
    BudgetGeralBulkUpsert,
    BudgetGeralResponse,
    BudgetGeralListResponse,
    BudgetCategoriaConfigCreate,
    BudgetCategoriaConfigUpdate,
    BudgetCategoriaConfigResponse,
    DetalhamentoMediaResponse
)

router = APIRouter()


# ===== ROTAS ESPECÍFICAS (strings fixas) - SEMPRE ANTES DAS PARAMETRIZADAS =====

# ----- ROTAS DE CONFIGURAÇÃO DE CATEGORIAS -----
@router.get("/budget/categorias-config", summary="Listar configuração de categorias")
def list_categorias_config(
    apenas_ativas: bool = Query(True, description="Retornar apenas categorias ativas"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista categorias configuradas do usuário ordenadas por hierarquia
    
    Retorna configuração de categorias personalizáveis com ordem, cores, etc
    """
    service = BudgetService(db)
    return {"categorias": service.get_categorias_config(user_id, apenas_ativas)}


@router.post("/budget/categorias-config", summary="Criar nova categoria")
def create_categoria_config(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria nova categoria configurada
    
    Body:
    - nome_categoria: str
    - ordem: int (opcional, default 999)
    - fonte_dados: "GRUPO" | "TIPO_TRANSACAO"
    - filtro_valor: str (ex: "Moradia", "Cartão")
    - tipos_gasto_incluidos: List[str] (opcional)
    - cor_visualizacao: str (hex, opcional, default "#94a3b8")
    """
    service = BudgetService(db)
    return service.create_categoria_config(user_id, data)


@router.put("/budget/categorias-config/reordenar", summary="Reordenar categorias")
def reordenar_categorias(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Reordena múltiplas categorias em batch (drag & drop)
    
    Body: {"reordenar": [{"id": 1, "nova_ordem": 3}, {"id": 2, "nova_ordem": 1}, ...]}
    """
    service = BudgetService(db)
    return {"categorias": service.reordenar_categorias(user_id, data.get("reordenar", []))}


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


@router.post("/budget/geral/bulk-upsert", response_model=List[BudgetGeralResponse], summary="Criar/atualizar múltiplas metas gerais")
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


@router.post("/budget/geral/bulk-upsert-validado", summary="Criar/atualizar com validação")
def bulk_upsert_budget_geral_validado(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza metas gerais com validação e auto-ajuste
    
    Body:
    - mes_referencia: str (YYYY-MM)
    - budgets: List[{categoria_geral, valor_planejado}]
    - total_mensal: float (opcional, teto de gastos)
    
    Retorna:
    - budgets: List
    - total_ajustado: bool (se foi ajustado automaticamente)
    - novo_total: float
    - valor_anterior: float
    - soma_categorias: float
    """
    service = BudgetService(db)
    return service.bulk_upsert_budget_geral_com_validacao(
        user_id=user_id,
        mes_referencia=data["mes_referencia"],
        budgets=data["budgets"],
        total_mensal=data.get("total_mensal")
    )


# ----- ROTAS DE META GERAL -----
@router.post("/budget/geral/copy-to-year", summary="Copiar metas para ano inteiro")
def copy_budget_to_year(
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Copia metas de um mês para todos os meses de um ano
    
    Body:
    - mes_origem: str (YYYY-MM) - Mês de origem das metas
    - ano_destino: int - Ano de destino (ex: 2026)
    - substituir_existentes: bool - Se deve sobrescrever metas existentes
    
    Returns:
    - sucesso: bool
    - meses_criados: int
    - metas_copiadas: int
    - mensagem: str
    """
    service = BudgetService(db)
    return service.copy_budget_to_year(
        user_id=user_id,
        mes_origem=data["mes_origem"],
        ano_destino=data["ano_destino"],
        substituir_existentes=data.get("substituir_existentes", False)
    )


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


@router.get("/budget/geral/grupos-disponiveis", response_model=List[str], summary="Listar grupos disponíveis")
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


@router.get("/budget/geral", response_model=BudgetGeralListResponse, summary="Listar metas gerais")
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


@router.patch("/budget/categorias-config/{config_id}", summary="Atualizar categoria")
def update_categoria_config(
    config_id: int,
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza configuração de categoria existente
    
    Aceita atualização parcial de campos
    """
    service = BudgetService(db)
    return service.update_categoria_config(config_id, user_id, data)


@router.patch("/budget/categorias-config/{config_id}/tipos-gasto", summary="Atualizar TipoGasto")
def update_tipos_gasto(
    config_id: int,
    data: dict,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza lista de TipoGasto incluídos em uma categoria
    
    Body: {"tipos_gasto": ["Ajustável", "Fixo", ...]}
    """
    service = BudgetService(db)
    return service.update_tipos_gasto_categoria(config_id, user_id, data.get("tipos_gasto", []))


@router.delete("/budget/categorias-config/{config_id}", status_code=204, summary="Deletar categoria")
def delete_categoria_config(
    config_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Deleta (desativa) uma configuração de categoria"""
    service = BudgetService(db)
    service.delete_categoria_config(config_id, user_id)
    return None


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
