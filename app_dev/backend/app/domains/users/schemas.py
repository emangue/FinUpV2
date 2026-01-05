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
