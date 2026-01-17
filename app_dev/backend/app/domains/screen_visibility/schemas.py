"""
Screen Visibility Schemas
Schemas Pydantic para validação e serialização
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ScreenVisibilityBase(BaseModel):
    """Schema base com campos comuns"""
    screen_key: str = Field(..., description="Chave única da tela (ex: 'dashboard')")
    screen_name: str = Field(..., description="Nome exibido (ex: 'Dashboard')")
    status: Literal['P', 'A', 'D'] = Field(default='P', description="P=Production, A=Admin, D=Development")
    icon: Optional[str] = Field(None, description="Nome do ícone lucide-react")
    display_order: int = Field(default=0, description="Ordem de exibição")
    parent_key: Optional[str] = Field(None, description="Chave do item pai (hierarquia)")
    url: Optional[str] = Field(None, description="URL completa da rota")


class ScreenVisibilityCreate(ScreenVisibilityBase):
    """Schema para criação de nova tela"""
    pass


class ScreenVisibilityUpdate(BaseModel):
    """Schema para atualização - todos os campos são opcionais"""
    screen_name: Optional[str] = None
    status: Optional[Literal['P', 'A', 'D']] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    parent_key: Optional[str] = None
    url: Optional[str] = None


class ScreenVisibilityResponse(ScreenVisibilityBase):
    """Schema de resposta com campos adicionais"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Permite conversão de SQLAlchemy model


class ScreenVisibilityBadge(BaseModel):
    """Schema simplificado para badges na sidebar"""
    screen_key: str
    screen_name: str
    status: Literal['P', 'A', 'D']
    icon: Optional[str] = None
    display_order: int = 0
    parent_key: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True
