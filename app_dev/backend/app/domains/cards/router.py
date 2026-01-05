"""
Domínio Cards - Router
Endpoints HTTP - apenas validação e chamadas de service
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import CardService
from .schemas import (
    CardResponse,
    CardCreate,
    CardUpdate,
    CardListResponse,
    CardByBankResponse
)

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/", response_model=CardListResponse)
def list_cards(
    apenas_ativos: bool = Query(True, description="Listar apenas cartões ativos"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista todos os cartões do usuário
    """
    service = CardService(db)
    return service.list_cards(user_id, apenas_ativos)

@router.get("/grouped-by-bank", response_model=List[CardByBankResponse])
def list_cards_grouped_by_bank(
    apenas_ativos: bool = Query(True, description="Listar apenas cartões ativos"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista cartões agrupados por banco
    """
    service = CardService(db)
    return service.list_cards_grouped_by_bank(user_id, apenas_ativos)

@router.get("/bank/{banco_nome}", response_model=List[CardResponse])
def list_cards_by_bank(
    banco_nome: str,
    apenas_ativos: bool = Query(True, description="Listar apenas cartões ativos"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Lista cartões de um banco específico
    """
    service = CardService(db)
    return service.list_cards_by_bank(user_id, banco_nome, apenas_ativos)

@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Busca cartão por ID
    """
    service = CardService(db)
    return service.get_card(card_id, user_id)

@router.post("/", response_model=CardResponse, status_code=201)
def create_card(
    card: CardCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Cria novo cartão
    """
    service = CardService(db)
    return service.create_card(user_id, card)

@router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    update_data: CardUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Atualiza cartão
    """
    service = CardService(db)
    return service.update_card(card_id, user_id, update_data)

@router.delete("/{card_id}")
def delete_card(
    card_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Desativa cartão (soft delete)
    """
    service = CardService(db)
    return service.delete_card(card_id, user_id)
