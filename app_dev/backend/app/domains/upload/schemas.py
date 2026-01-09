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
    
    # Campos de identificação (Fase 2) - CamelCase para compatibilidade com banco
    IdTransacao: Optional[str] = Field(None, alias="id_transacao")
    IdParcela: Optional[str] = Field(None, alias="id_parcela")
    EstabelecimentoBase: Optional[str] = Field(None, alias="estabelecimento_base")
    ParcelaAtual: Optional[int] = Field(None, alias="parcela_atual")
    TotalParcelas: Optional[int] = Field(None, alias="total_parcelas")
    ValorPositivo: Optional[float] = Field(None, alias="valor_positivo")
    
    # Campos de classificação (Fase 3) - CamelCase para compatibilidade com banco
    GRUPO: Optional[str] = Field(None, alias="grupo")
    SUBGRUPO: Optional[str] = Field(None, alias="subgrupo")
    TipoGasto: Optional[str] = Field(None, alias="tipo_gasto")
    CategoriaGeral: Optional[str] = Field(None, alias="categoria_geral")
    origem_classificacao: Optional[str] = None
    padrao_buscado: Optional[str] = None  # Debug: padrão montado usado na busca
    MarcacaoIA: Optional[str] = Field(None, alias="marcacao_ia")  # Sugestão da base_marcacoes
    
    # Campos de deduplicação (Fase 4)
    is_duplicate: Optional[bool] = False
    duplicate_reason: Optional[str] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True  # Permite usar tanto campo original quanto alias


class ClassificationStats(BaseModel):
    """Estatísticas de classificação"""
    total: int
    base_parcelas: int = 0
    base_padroes: int = 0
    journal_entries: int = 0
    regras_genericas: int = 0
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
