"""Schemas do domínio Plano"""
from pydantic import BaseModel, Field
from typing import Optional


class RendaUpdate(BaseModel):
    renda_mensal_liquida: float = Field(..., ge=0)


class OrcamentoItem(BaseModel):
    grupo: str
    gasto: float
    meta: Optional[float]
    percentual: Optional[float]
    status: str  # ok, alerta, excedido


class MetaCreate(BaseModel):
    valor_meta: float = Field(..., ge=0)
    ano: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)
