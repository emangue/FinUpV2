"""
Domínio Marcações - Schemas
Schemas Pydantic para validação de dados
"""
from typing import Optional
from pydantic import BaseModel, Field


class MarcacaoCreate(BaseModel):
    """Schema para criar nova marcação (grupo + subgrupo)"""
    grupo: str = Field(..., description="Nome do grupo", min_length=1, max_length=100)
    subgrupo: str = Field(..., description="Nome do subgrupo", min_length=1, max_length=100)
    tipo_gasto: str = Field(..., description="Tipo de gasto (Fixo/Ajustável/etc)")
    categoria_geral: Optional[str] = Field("Despesa", description="Categoria geral (Despesa/Receita/etc)")
    
    class Config:
        from_attributes = True


class MarcacaoResponse(BaseModel):
    """Schema de resposta para marcação"""
    id: int
    grupo: str
    subgrupo: str
    tipo_gasto: str
    categoria_geral: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_db_model(cls, db_model):
        """Converte dict do repository (já com JOIN) para schema"""
        if isinstance(db_model, dict):
            return cls(**db_model)
        # Fallback para modelo SQLAlchemy (não tem mais TipoGasto)
        return cls(
            id=db_model.id,
            grupo=db_model.GRUPO,
            subgrupo=db_model.SUBGRUPO,
            tipo_gasto="",  # Será preenchido via JOIN
            categoria_geral=None
        )


class MarcacaoListResponse(BaseModel):
    """Schema de resposta para lista de marcações"""
    marcacoes: list[MarcacaoResponse]
    total: int


class SubgrupoCreate(BaseModel):
    """Schema para criar subgrupo (herda config do grupo_pai)"""
    subgrupo: str = Field(..., description="Nome do subgrupo", min_length=1, max_length=100)
    
    class Config:
        from_attributes = True


class SubgrupoResponse(BaseModel):
    """Schema de resposta para subgrupo criado"""
    id: int
    grupo: str
    subgrupo: str
    tipo_gasto: str
    categoria_geral: Optional[str] = None
    message: str = "Subgrupo criado com sucesso"
    
    class Config:
        from_attributes = True


class GrupoComSubgrupos(BaseModel):
    """Schema para listar grupos com seus subgrupos"""
    grupo: str
    subgrupos: list[str]
    total_subgrupos: int


class GrupoComSubgrupoCreate(BaseModel):
    """Schema para criar grupo E subgrupo juntos"""
    grupo: str = Field(..., description="Nome do novo grupo", min_length=1, max_length=100)
    subgrupo: str = Field(..., description="Nome do primeiro subgrupo", min_length=1, max_length=100)
    tipo_gasto: str = Field(..., description="Tipo de gasto padrão (Fixo/Ajustável/etc)")
    categoria_geral: str = Field("Despesa", description="Categoria geral (Despesa/Receita/etc)")
    
    class Config:
        from_attributes = True
