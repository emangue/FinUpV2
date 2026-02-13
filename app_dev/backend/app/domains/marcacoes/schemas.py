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
        """Converte modelo do banco (campos maiúsculos) para schema"""
        return cls(
            id=db_model.id,
            grupo=db_model.GRUPO,
            subgrupo=db_model.SUBGRUPO,
            tipo_gasto=db_model.TipoGasto,
            categoria_geral=db_model.CategoriaGeral
        )


class MarcacaoListResponse(BaseModel):
    """Schema de resposta para lista de marcações"""
    marcacoes: list[MarcacaoResponse]
    total: int


class SubgrupoCreate(BaseModel):
    """Schema para criar subgrupo (grupo_pai vem da URL)"""
    subgrupo: str = Field(..., description="Nome do subgrupo", min_length=1, max_length=100)
    tipo_gasto: str = Field(..., description="Tipo de gasto")
    categoria_geral: Optional[str] = Field("Despesa", description="Categoria geral")
    
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
