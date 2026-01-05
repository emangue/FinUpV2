"""
Domínio Upload - Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UploadPreviewRequest(BaseModel):
    """Schema de requisição de upload/preview"""
    banco: str
    cartao: Optional[str] = None
    mesFatura: str = Field(..., description="Formato YYYY-MM")
    tipoDocumento: str = "fatura"  # fatura ou extrato
    formato: str = "csv"  # csv, xls, xlsx

class PreviewTransacaoResponse(BaseModel):
    """Schema de resposta de transação de preview"""
    id: int
    data: str
    lancamento: str
    valor: float
    banco: str
    cartao: Optional[str] = None
    mes_fatura: str
    nome_arquivo: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UploadPreviewResponse(BaseModel):
    """Schema de resposta de upload/preview"""
    success: bool
    sessionId: str
    totalRegistros: int

class GetPreviewResponse(BaseModel):
    """Schema de resposta de dados de preview"""
    success: bool
    sessionId: str
    totalRegistros: int
    dados: List[PreviewTransacaoResponse]

class ConfirmUploadResponse(BaseModel):
    """Schema de resposta de confirmação de upload"""
    success: bool
    sessionId: str
    transacoesCriadas: int
    transacoesDuplicadas: int = 0
    total: int

class DeletePreviewResponse(BaseModel):
    """Schema de resposta de exclusão de preview"""
    success: bool
    sessionId: str
    deletedCount: int

class ProcessorResult(BaseModel):
    """Schema de resultado de processamento"""
    data: str
    lancamento: str
    valor: float
