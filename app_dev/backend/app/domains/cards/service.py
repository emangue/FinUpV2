"""
Domínio Cards - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
from datetime import datetime

from .repository import CardRepository
from .models import Cartao
from .schemas import (
    CardCreate,
    CardUpdate,
    CardResponse,
    CardListResponse,
    CardByBankResponse
)

class CardService:
    """
    Service layer para cartões
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = CardRepository(db)
    
    def get_card(self, card_id: int, user_id: int) -> CardResponse:
        """
        Busca um cartão por ID
        
        Raises:
            HTTPException: Se cartão não encontrado
        """
        card = self.repository.get_by_id(card_id, user_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cartão com ID {card_id} não encontrado"
            )
        return CardResponse.from_orm(card)
    
    def list_cards(
        self,
        user_id: int,
        apenas_ativos: bool = True
    ) -> CardListResponse:
        """
        Lista todos os cartões do usuário
        """
        cards = self.repository.list_all(user_id, apenas_ativos)
        total = self.repository.count_all(user_id, apenas_ativos)
        
        return CardListResponse(
            cards=[CardResponse.from_orm(c) for c in cards],
            total=total
        )
    
    def list_cards_by_bank(
        self,
        user_id: int,
        banco: str,
        apenas_ativos: bool = True
    ) -> List[CardResponse]:
        """
        Lista cartões de um banco específico
        """
        cards = self.repository.list_by_bank(user_id, banco, apenas_ativos)
        return [CardResponse.from_orm(c) for c in cards]
    
    def list_cards_grouped_by_bank(
        self,
        user_id: int,
        apenas_ativos: bool = True
    ) -> List[CardByBankResponse]:
        """
        Lista cartões agrupados por banco
        """
        banks = self.repository.get_distinct_banks(user_id)
        
        result = []
        for banco in banks:
            cards = self.repository.list_by_bank(user_id, banco, apenas_ativos)
            result.append(CardByBankResponse(
                banco=banco,
                cartoes=[CardResponse.from_orm(c) for c in cards]
            ))
        
        return result
    
    def create_card(
        self,
        user_id: int,
        card_data: CardCreate
    ) -> CardResponse:
        """
        Cria novo cartão
        
        Lógica de negócio:
        - Valida final do cartão (4 dígitos numéricos)
        - Verifica duplicatas
        - Define timestamps
        
        Raises:
            HTTPException: Se dados inválidos ou cartão duplicado
        """
        # Validar final do cartão
        if not card_data.final_cartao.isdigit() or len(card_data.final_cartao) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Final do cartão deve ter exatamente 4 dígitos"
            )
        
        # Verificar duplicata
        existing = self.repository.find_duplicate(
            user_id,
            card_data.banco,
            card_data.final_cartao
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um cartão ativo do {card_data.banco} com final {card_data.final_cartao}"
            )
        
        # Criar modelo
        now = datetime.now()
        card = Cartao(
            nome_cartao=card_data.nome_cartao.strip(),
            final_cartao=card_data.final_cartao,
            banco=card_data.banco.strip(),
            user_id=user_id,
            ativo=1,
            created_at=now,
            updated_at=now
        )
        
        # Salvar
        created = self.repository.create(card)
        return CardResponse.from_orm(created)
    
    def update_card(
        self,
        card_id: int,
        user_id: int,
        update_data: CardUpdate
    ) -> CardResponse:
        """
        Atualiza cartão
        
        Raises:
            HTTPException: Se cartão não encontrado ou dados inválidos
        """
        # Buscar cartão
        card = self.repository.get_by_id(card_id, user_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cartão com ID {card_id} não encontrado"
            )
        
        # Validar final do cartão se fornecido
        if update_data.final_cartao:
            if not update_data.final_cartao.isdigit() or len(update_data.final_cartao) != 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Final do cartão deve ter exatamente 4 dígitos"
                )
        
        # Aplicar mudanças (apenas campos não-None)
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field in ["nome_cartao", "banco"] and value:
                setattr(card, field, value.strip())
            else:
                setattr(card, field, value)
        
        card.updated_at = datetime.now()
        
        # Salvar
        updated = self.repository.update(card)
        return CardResponse.from_orm(updated)
    
    def delete_card(self, card_id: int, user_id: int) -> dict:
        """
        Desativa cartão (soft delete)
        
        Raises:
            HTTPException: Se cartão não encontrado
        """
        card = self.repository.get_by_id(card_id, user_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cartão com ID {card_id} não encontrado"
            )
        
        card.updated_at = datetime.now()
        self.repository.soft_delete(card)
        return {"message": "Cartão desativado com sucesso"}
