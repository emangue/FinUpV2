"""
Budget Planning Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime
import re


class BudgetBase(BaseModel):
    """Schema base para Budget"""
    tipo_gasto: str = Field(..., description="Tipo de gasto (Fixo, Ajustável, Essencial, etc)")
    mes_referencia: str = Field(..., description="Mês de referência no formato YYYY-MM")
    valor_planejado: float = Field(..., gt=0, description="Valor planejado (deve ser > 0)")
    
    @validator('mes_referencia')
    def validate_mes_referencia(cls, v):
        """Valida formato YYYY-MM"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('mes_referencia deve estar no formato YYYY-MM (ex: 2025-11)')
        
        year, month = v.split('-')
        if not (1 <= int(month) <= 12):
            raise ValueError('Mês deve estar entre 01 e 12')
        
        return v


class BudgetCreate(BudgetBase):
    """Schema para criação de budget"""
    pass


class BudgetUpdate(BaseModel):
    """Schema para atualização de budget"""
    valor_planejado: float = Field(..., gt=0, description="Novo valor planejado")


class BudgetResponse(BudgetBase):
    """Schema de resposta de budget"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    """Schema de resposta para lista de budgets"""
    budgets: List[BudgetResponse]
    total: int


class BudgetBulkUpsert(BaseModel):
    """Schema para criar/atualizar múltiplos budgets de uma vez"""
    mes_referencia: str = Field(..., description="Mês de referência no formato YYYY-MM")
    budgets: List[dict] = Field(..., description="Lista de {tipo_gasto: str, valor_planejado: float}")
    
    @validator('mes_referencia')
    def validate_mes_referencia(cls, v):
        """Valida formato YYYY-MM"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('mes_referencia deve estar no formato YYYY-MM')
        return v


class BudgetGeralBulkUpsert(BaseModel):
    """Schema para criar/atualizar múltiplos budgets gerais de uma vez"""
    mes_referencia: str = Field(..., description="Mês de referência no formato YYYY-MM")
    budgets: List[dict] = Field(..., description="Lista de {categoria_geral: str, valor_planejado: float}")
    
    @validator('mes_referencia')
    def validate_mes_referencia(cls, v):
        """Valida formato YYYY-MM"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('mes_referencia deve estar no formato YYYY-MM')
        return v
