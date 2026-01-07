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
    mes_fatura: Optional[str] = None
    nome_arquivo: str
    created_at: Optional[datetime] = None
    
    # Campos de identificação (Fase 2)
    id_transacao: Optional[str] = None
    id_parcela: Optional[str] = None
    estabelecimento_base: Optional[str] = None
    parcela_atual: Optional[int] = None
    total_parcelas: Optional[int] = None
    valor_positivo: Optional[float] = None
    
    # Campos de classificação (Fase 3)
    grupo: Optional[str] = None
    subgrupo: Optional[str] = None
    tipo_gasto: Optional[str] = None
    categoria_geral: Optional[str] = None
    origem_classificacao: Optional[str] = None
    
    # Campos de deduplicação (Fase 4)
    is_duplicate: Optional[bool] = False
    duplicate_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class ClassificationStats(BaseModel):
    """Estatísticas de classificação"""
    total: int
    base_parcelas: int = 0
    base_padroes: int = 0
    journal_entries: int = 0
    marcas_gerais: int = 0
    nao_classificado: int = 0


class UploadPreviewResponse(BaseModel):
    """Schema de resposta de upload/preview"""
    success: bool
    sessionId: str
    totalRegistros: int
    stats: Optional[ClassificationStats] = None

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
