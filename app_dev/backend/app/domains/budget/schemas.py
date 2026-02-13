"""
Budget Planning Schemas
Pydantic schemas para validação e serialização

CHANGELOG 13/02/2026:
- ✅ Removidos schemas obsoletos: BudgetGeral*, BudgetCategoriaConfig*
- ✅ Apenas BudgetPlanning schemas ativos
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re


class BudgetBase(BaseModel):
    """Schema base para Budget"""
    grupo: str = Field(..., description="Grupo (Casa, Cartão, Saúde, etc)")
    mes_referencia: str = Field(..., description="Mês de referência no formato YYYY-MM")
    valor_planejado: float = Field(..., ge=0, description="Valor planejado (pode ser >= 0)")
    valor_medio_3_meses: float = Field(default=0.0, description="Média calculada dos últimos 3 meses")
    ativo: int = Field(default=1, description="0=inativo, 1=ativo")
    
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
    grupo: Optional[str] = Field(None, description="Grupo (casa, cartão, etc)")
    mes_referencia: Optional[str] = Field(None, description="Mês de referência")
    valor_planejado: Optional[float] = Field(None, ge=0, description="Novo valor planejado")

    @validator('mes_referencia')
    def validate_mes_referencia(cls, v):
        if v is None: return v
        """Valida formato YYYY-MM"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('mes_referencia deve estar no formato YYYY-MM (ex: 2025-11)')
        
        year, month = v.split('-')
        if not (1 <= int(month) <= 12):
            raise ValueError('Mês deve estar entre 01 e 12')
        
        return v


class BudgetResponse(BudgetBase):
    """Schema de resposta de budget"""
    id: int
    user_id: int
    valor_medio_3_meses: float
    ativo: int  # Adicionar explicitamente
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
    budgets: List[dict] = Field(..., description="Lista de {grupo: str, valor_planejado: float}")
    
    @validator('mes_referencia')
    def validate_mes_referencia(cls, v):
        """Valida formato YYYY-MM"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('mes_referencia deve estar no formato YYYY-MM')
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# REMOVIDO EM 13/02/2026 - Consolidação completa
# ═══════════════════════════════════════════════════════════════════════════════
# Schemas deletados (tabelas não existem mais):
# - BudgetGeralBulkUpsert
# - BudgetGeralResponse
# - BudgetGeralListResponse
# - BudgetCategoriaConfigCreate/Update/Response
#
# Se precisar, veja:
# git show HEAD~1:app_dev/backend/app/domains/budget/schemas.py
# ═══════════════════════════════════════════════════════════════════════════════


# ===== SCHEMAS PARA DETALHAMENTO DE MÉDIA =====

class SubgrupoDetalhamento(BaseModel):
    """Detalhamento de um subgrupo individual"""
    subgrupo: Optional[str] = Field(None, description="Nome do subgrupo (None para sem subgrupo)")
    valor_total: float = Field(..., description="Valor total do subgrupo")
    quantidade_transacoes: int = Field(..., description="Quantidade de transações")


class MesDetalhamento(BaseModel):
    """Detalhamento de um mês individual"""
    mes_referencia: str = Field(..., description="Mês no formato YYYY-MM")
    mes_nome: str = Field(..., description="Nome do mês (ex: Janeiro 2026)")
    valor_total: float = Field(..., description="Valor total do mês")
    quantidade_transacoes: int = Field(..., description="Quantidade de transações")
    subgrupos: Optional[List[SubgrupoDetalhamento]] = Field(None, description="Lista de subgrupos do mês")


class DetalhamentoMediaResponse(BaseModel):
    """Resposta com detalhamento dos 3 meses da média"""
    grupo: str
    mes_planejado: str
    meses_considerados: List[MesDetalhamento]
    media_calculada: float
    total_geral: float
