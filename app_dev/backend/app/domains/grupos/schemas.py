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
    
    class Config:
        from_attributes = True


class GrupoUpdate(BaseModel):
    nome_grupo: Optional[str] = Field(None, description="Nome do grupo", min_length=1, max_length=100)
    tipo_gasto_padrao: Optional[str] = Field(None, description="Tipo de gasto padrão")
    categoria_geral: Optional[str] = Field(None, description="Categoria geral")
    
    class Config:
        from_attributes = True


class GrupoResponse(BaseModel):
    id: int
    nome_grupo: str
    tipo_gasto_padrao: str
    categoria_geral: str
    
    class Config:
        from_attributes = True


class GrupoListResponse(BaseModel):
    grupos: list[GrupoResponse]
    total: int