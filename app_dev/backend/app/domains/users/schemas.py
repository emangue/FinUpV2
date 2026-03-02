"""
Domínio Users - Schemas
Pydantic schemas para validação e serialização
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Schema base de usuário"""
    email: EmailStr
    nome: str

class UserCreate(UserBase):
    """Schema para criar usuário"""
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    """Schema para atualizar usuário"""
    email: Optional[EmailStr] = None
    nome: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    ativo: Optional[int] = None

class ProfileUpdate(BaseModel):
    """Schema para atualizar perfil do usuário"""
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr

class PasswordChange(BaseModel):
    """Schema para alterar senha"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    """Schema de resposta de usuário"""
    id: int
    role: str
    ativo: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Schema de resposta de lista de usuários"""
    users: list[UserResponse]
    total: int


class UserStatsResponse(BaseModel):
    """Schema de resposta de estatísticas do usuário"""
    total_transacoes: int
    total_uploads: int
    ultimo_upload_em: Optional[datetime] = None
    total_grupos: int
    tem_plano: bool
    tem_investimentos: bool


class PurgeConfirmacao(BaseModel):
    """Schema para confirmação de purge de usuário"""
    confirmacao: str  # deve ser "EXCLUIR PERMANENTEMENTE"
    email_usuario: str  # deve bater com user.email


class SystemStatsResponse(BaseModel):
    """Estatísticas gerais do sistema (admin)"""
    total_usuarios: int
    total_usuarios_ativos: int
    total_uploads: int
    total_transacoes: int
    total_planos: int
