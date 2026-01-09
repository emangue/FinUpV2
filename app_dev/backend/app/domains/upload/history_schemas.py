"""
Schemas para histórico de uploads
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class UploadHistoryResponse(BaseModel):
    """Response para um registro de histórico"""
    id: int
    session_id: str
    banco: str
    tipo_documento: str
    nome_arquivo: str
    nome_cartao: Optional[str] = None
    final_cartao: Optional[str] = None
    mes_fatura: Optional[str] = None
    status: str
    total_registros: int
    transacoes_importadas: int
    transacoes_duplicadas: int
    classification_stats: Optional[Dict[str, Any]] = None
    balance_validation: Optional[Dict[str, Any]] = None
    data_upload: datetime
    data_confirmacao: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class UploadHistoryListResponse(BaseModel):
    """Response para lista de históricos"""
    success: bool
    total: int
    uploads: list[UploadHistoryResponse]
