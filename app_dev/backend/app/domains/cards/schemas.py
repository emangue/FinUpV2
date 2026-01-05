"""
Domínio Cards - Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class CardBase(BaseModel):
    """Schema base de cartão"""
    nome_cartao: str
    final_cartao: str = Field(..., min_length=4, max_length=4)
    banco: str

class CardCreate(CardBase):
    """Schema para criar cartão"""
    pass

class CardUpdate(BaseModel):
    """Schema para atualizar cartão"""
    nome_cartao: Optional[str] = None
    final_cartao: Optional[str] = Field(None, min_length=4, max_length=4)
    banco: Optional[str] = None
    ativo: Optional[int] = None

class CardResponse(CardBase):
    """Schema de resposta de cartão"""
    id: int
    user_id: int
    ativo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CardListResponse(BaseModel):
    """Schema de resposta de lista de cartões"""
    cards: list[CardResponse]
    total: int

class CardByBankResponse(BaseModel):
    """Schema de cartões agrupados por banco"""
    banco: str
    cartoes: list[CardResponse]
