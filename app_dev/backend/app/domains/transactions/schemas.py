"""
Domínio Transactions - Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel, Field
from typing import Optional, Union, List
from datetime import datetime

class TransactionBase(BaseModel):
    """Schema base de transação"""
    Data: str
    Estabelecimento: str
    Valor: float
    TipoTransacao: str
    GRUPO: Optional[str] = None
    SUBGRUPO: Optional[str] = None
    TipoGasto: Optional[str] = None
    NomeCartao: Optional[str] = None

class TransactionCreate(TransactionBase):
    """Schema para criar transação"""
    user_id: int
    IdTransacao: str
    arquivo_origem: Optional[str] = None
    banco_origem: Optional[str] = None
    tipodocumento: Optional[str] = None

class TransactionUpdate(BaseModel):
    """Schema para atualizar transação"""
    GRUPO: Optional[str] = None
    SUBGRUPO: Optional[str] = None
    TipoGasto: Optional[str] = None
    Estabelecimento: Optional[str] = None
    Valor: Optional[float] = None
    IgnorarDashboard: Optional[int] = None

class TransactionResponse(TransactionBase):
    """Schema de resposta de transação"""
    id: int
    IdTransacao: str
    user_id: int
    ValorPositivo: Optional[float] = None
    IdParcela: Optional[str] = None
    MesFatura: Optional[str] = None
    Ano: Optional[int] = None
    arquivo_origem: Optional[str] = None
    banco_origem: Optional[str] = None
    tipodocumento: Optional[str] = None
    origem_classificacao: Optional[str] = None
    IgnorarDashboard: int = 0
    CategoriaGeral: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    """Schema de resposta de lista de transações"""
    transactions: list[TransactionResponse]
    total: int
    page: int
    limit: int

class TransactionFilters(BaseModel):
    """Schema de filtros de transação"""
    year: Optional[int] = None
    month: Optional[int] = None
    estabelecimento: Optional[str] = None
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    tipo: Optional[str] = None
    categoria_geral: Optional[str] = None
    tipo_gasto: Optional[Union[str, List[str]]] = None  # Aceita string ou lista
    cartao: Optional[str] = None
    search: Optional[str] = None

class TipoGastoComMedia(BaseModel):
    """Schema de tipo de gasto com média dos últimos 3 meses"""
    tipo_gasto: str
    media_3_meses: float

class TiposGastoComMediaResponse(BaseModel):
    """Schema de resposta de tipos de gasto com média"""
    tipos_gasto: list[TipoGastoComMedia]
    mes_referencia: str
