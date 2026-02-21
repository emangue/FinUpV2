"""
Domínio Grupos - Schemas
Schemas Pydantic para validação de dados
"""
from typing import Optional
from pydantic import BaseModel, Field


class GrupoCreate(BaseModel):
    nome_grupo: str = Field(..., description="Nome do grupo", min_length=1, max_length=100)
    tipo_gasto_padrao: str = Field(..., description="Tipo de gasto padrão (Fixo/Ajustável)")
    categoria_geral: str = Field(..., description="Categoria geral (Despesa/Receita/etc)")
    cor: Optional[str] = Field(None, description="Cor hex (ex: #001D39)", max_length=7)
    
    class Config:
        from_attributes = True


class GrupoUpdate(BaseModel):
    nome_grupo: Optional[str] = Field(None, description="Nome do grupo", min_length=1, max_length=100)
    tipo_gasto_padrao: Optional[str] = Field(None, description="Tipo de gasto padrão")
    categoria_geral: Optional[str] = Field(None, description="Categoria geral")
    cor: Optional[str] = Field(None, description="Cor hex (ex: #001D39)", max_length=7)
    
    class Config:
        from_attributes = True


class GrupoResponse(BaseModel):
    id: int
    nome_grupo: str
    tipo_gasto_padrao: str
    categoria_geral: str
    cor: Optional[str] = None
    
    class Config:
        from_attributes = True


class GrupoListResponse(BaseModel):
    grupos: list[GrupoResponse]
    total: int


# ===== SCHEMAS PARA AUTO-CRIAÇÃO (Sprint 2) =====

class SubgrupoCreate(BaseModel):
    """Schema para criar subgrupo (nome apenas, grupo_pai vem da URL)"""
    nome: str = Field(..., description="Nome do subgrupo", min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class SubgrupoResponse(BaseModel):
    """Schema de resposta para subgrupo criado"""
    grupo_pai: str
    subgrupo: str
    message: str = "Subgrupo validado e disponível para uso"
    
    class Config:
        from_attributes = True


class GrupoBatchCreate(BaseModel):
    """Schema para criação em lote de grupos"""
    grupos: list[GrupoCreate] = Field(..., description="Lista de grupos a criar")


class GrupoBatchResponse(BaseModel):
    """Schema de resposta para criação em lote"""
    created: list[GrupoResponse] = Field(default_factory=list, description="Grupos criados")
    skipped: list[dict] = Field(default_factory=list, description="Grupos que já existiam")
    errors: list[dict] = Field(default_factory=list, description="Erros durante criação")