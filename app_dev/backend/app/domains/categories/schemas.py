"""
Domínio Categories - Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    """Schema base de categoria"""
    GRUPO: str
    SUBGRUPO: str
    TipoGasto: str

class CategoryCreate(CategoryBase):
    """Schema para criar categoria"""
    pass

class CategoryUpdate(BaseModel):
    """Schema para atualizar categoria"""
    GRUPO: Optional[str] = None
    SUBGRUPO: Optional[str] = None
    TipoGasto: Optional[str] = None

class CategoryResponse(CategoryBase):
    """Schema de resposta de categoria"""
    id: int
    
    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    """Schema de resposta de lista de categorias"""
    categories: list[CategoryResponse]
    total: int

class CategoryGrouped(BaseModel):
    """Schema de categorias agrupadas por GRUPO"""
    grupo: str
    subgrupos: list[str]
    tipos_gasto: list[str]
