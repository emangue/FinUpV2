"""
Router para gerenciamento de regras de classificação genérica
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import GenericClassificationService
from .schemas import (
    GenericRuleCreate, GenericRuleUpdate, GenericRuleResponse,
    GenericRuleTestRequest, GenericRuleTestResponse,
    GenericRuleImportRequest
)


router = APIRouter(prefix="/classification", tags=["Classification"])


@router.get("/rules", response_model=List[GenericRuleResponse])
def list_rules(
    active_only: bool = Query(None, description="Filtrar apenas regras ativas"),
    search: str = Query(None, description="Buscar em nome, keywords ou descrição"),
    grupo: str = Query(None, description="Filtrar por grupo"),
    sort_by: str = Query("prioridade", pattern="^(prioridade|nome|grupo|uso|created)$"),
    sort_desc: bool = Query(True, description="Ordem decrescente"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista regras de classificação genérica com filtros"""
    service = GenericClassificationService(db)
    rules = service.list_rules(
        active_only=active_only,
        search=search,
        grupo=grupo,
        sort_by=sort_by,
        sort_desc=sort_desc
    )
    
    return [GenericRuleResponse.from_model(rule) for rule in rules]


@router.post("/rules", response_model=GenericRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_data: GenericRuleCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Cria nova regra de classificação genérica"""
    service = GenericClassificationService(db)
    rule = service.create_rule(rule_data, created_by=f"user_{user_id}")
    
    return GenericRuleResponse.from_model(rule)


@router.get("/rules/{rule_id}", response_model=GenericRuleResponse)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Busca regra por ID"""
    service = GenericClassificationService(db)
    rule = service.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    
    return GenericRuleResponse.from_model(rule)


@router.patch("/rules/{rule_id}", response_model=GenericRuleResponse)
def update_rule(
    rule_id: int,
    rule_data: GenericRuleUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Atualiza regra existente"""
    service = GenericClassificationService(db)
    rule = service.update_rule(rule_id, rule_data)
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )
    
    return GenericRuleResponse.from_model(rule)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Deleta regra"""
    service = GenericClassificationService(db)
    success = service.delete_rule(rule_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regra não encontrada"
        )


@router.post("/rules/test", response_model=GenericRuleTestResponse)
def test_rules(
    test_data: GenericRuleTestRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Testa quais regras fazem match com um texto"""
    service = GenericClassificationService(db)
    result = service.test_rule(test_data.texto)
    
    return GenericRuleTestResponse(**result)


@router.post("/rules/import")
def import_hardcoded_rules(
    import_data: GenericRuleImportRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Importa regras hardcoded para a base de dados"""
    service = GenericClassificationService(db)
    result = service.import_hardcoded_rules(sobrescrever=import_data.sobrescrever_existentes)
    
    return {
        "message": "Importação concluída com sucesso",
        "stats": result
    }


@router.get("/groups")
def list_grupos(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista grupos únicos das regras"""
    service = GenericClassificationService(db)
    grupos = service.get_grupos_disponiveis()
    
    return {"grupos": grupos}


@router.get("/groups-with-types")
def list_grupos_with_types(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Lista grupos/subgrupos únicos das transações com seus tipos de gasto"""
    service = GenericClassificationService(db)
    grupos_com_tipos = service.get_grupos_subgrupos_com_tipos()
    
    return {"opcoes": grupos_com_tipos}


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Retorna estatísticas das regras"""
    service = GenericClassificationService(db)
    stats = service.get_stats()
    
    return stats