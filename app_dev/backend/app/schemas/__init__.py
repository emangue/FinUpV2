"""
Schemas Pydantic para validação e serialização
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ========== AUTH ==========
class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema de resposta de autenticação"""
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    """Schema de resposta de usuário"""
    id: int
    email: str
    name: str
    role: str
    
    class Config:
        from_attributes = True

# ========== DASHBOARD ==========
class DashboardMetrics(BaseModel):
    """Métricas do dashboard"""
    total_despesas: float
    total_receitas: float
    saldo: float
    total_transacoes: int
    por_tipo_gasto: List[dict]
    evolucao_mensal: List[dict]

class CategoryStats(BaseModel):
    """Estatísticas por categoria"""
    TipoGasto: str
    total: float
    quantidade: int
    percentual: float

# ========== TRANSAÇÕES ==========
class TransacaoBase(BaseModel):
    """Schema base de transação"""
    Data: str
    Estabelecimento: str
    Valor: float
    TipoTransacao: str
    GRUPO: Optional[str] = None
    SUBGRUPO: Optional[str] = None
    TipoGasto: Optional[str] = None
    MesFatura: Optional[str] = None

class TransacaoResponse(TransacaoBase):
    """Schema de resposta de transação"""
    id: int
    IdTransacao: str
    ValorPositivo: float
    CategoriaGeral: Optional[str] = None
    banco_origem: Optional[str] = None
    origem_classificacao: Optional[str] = None
    
    class Config:
        from_attributes = True

class TransacaoListResponse(BaseModel):
    """Lista paginada de transações"""
    total: int
    page: int
    per_page: int
    transacoes: List[TransacaoResponse]

class TransacaoFilter(BaseModel):
    """Filtros para lista de transações"""
    ano: Optional[str] = None
    mes: Optional[str] = None
    grupo: Optional[str] = None
    tipo_gasto: Optional[str] = None
    tipo_transacao: Optional[str] = None
    estabelecimento: Optional[str] = None
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None

# ========== MARCAÇÕES (CONFIGURAÇÕES) ==========
class MarcacaoBase(BaseModel):
    """Schema base de marcação"""
    GRUPO: str
    SUBGRUPO: str
    TipoGasto: str

class MarcacaoCreate(MarcacaoBase):
    """Schema para criar marcação"""
    pass

class MarcacaoUpdate(MarcacaoBase):
    """Schema para atualizar marcação"""
    pass

class MarcacaoResponse(MarcacaoBase):
    """Schema de resposta de marcação"""
    id: int
    
    class Config:
        from_attributes = True

# ========== BANK COMPATIBILITY ==========
class BankCompatibilityResponse(BaseModel):
    """Schema de compatibilidade de bancos"""
    id: int
    bank_name: str
    file_format: str
    status: str
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

# ========== COMMON ==========
class ErrorResponse(BaseModel):
    """Schema de erro padronizado"""
    error: dict = Field(..., example={
        "code": "ERROR_CODE",
        "message": "Mensagem de erro",
        "details": {}
    })

class SuccessResponse(BaseModel):
    """Schema de sucesso padronizado"""
    message: str
    data: Optional[dict] = None
