"""
Schemas para Migração em Massa de Transações
"""
from pydantic import BaseModel, Field
from typing import Optional


class MigrationPreviewRequest(BaseModel):
    """Request para preview de migração"""
    grupo_origem: str = Field(..., description="Grupo de origem")
    subgrupo_origem: Optional[str] = Field(None, description="Subgrupo de origem (opcional)")
    grupo_destino: str = Field(..., description="Grupo de destino")
    subgrupo_destino: Optional[str] = Field(None, description="Subgrupo de destino (opcional)")


class MigrationPreviewResponse(BaseModel):
    """Response do preview de migração"""
    total_transacoes: int
    grupo_origem: str
    subgrupo_origem: Optional[str]
    grupo_destino: str
    subgrupo_destino: Optional[str]
    tipo_gasto_destino: str
    categoria_geral_destino: str


class MigrationExecuteRequest(BaseModel):
    """Request para executar migração"""
    grupo_origem: str = Field(..., description="Grupo de origem")
    subgrupo_origem: Optional[str] = Field(None, description="Subgrupo de origem (opcional)")
    grupo_destino: str = Field(..., description="Grupo de destino")
    subgrupo_destino: Optional[str] = Field(None, description="Subgrupo de destino (opcional)")


class MigrationExecuteResponse(BaseModel):
    """Response da execução de migração"""
    success: bool
    total_transacoes_atualizadas: int
    grupo_origem: str
    subgrupo_origem: Optional[str]
    grupo_destino: str
    subgrupo_destino: Optional[str]
    tipo_gasto_destino: str
    categoria_geral_destino: str
    grupos_recalculados: list[str]


class GrupoSubgrupoOption(BaseModel):
    """Opção de grupo/subgrupo"""
    grupo: str
    subgrupo: Optional[str]
    total_transacoes: int


class GrupoSubgrupoListResponse(BaseModel):
    """Lista de grupos/subgrupos disponíveis"""
    opcoes: list[GrupoSubgrupoOption]
