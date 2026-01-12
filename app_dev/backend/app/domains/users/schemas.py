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


# ======================================
# Schemas de Autenticação JWT
# ======================================

class LoginRequest(BaseModel):
    """Schema de requisição de login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@financas.com",
                "password": "admin123"
            }
        }


class TokenResponse(BaseModel):
    """
    Schema de resposta de token JWT
    
    access_token: Token JWT de curta duração (15min)
    refresh_token: Token para renovar access_token (7 dias)
    token_type: Sempre 'bearer'
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Segundos até expiração do access_token


class TokenPayload(BaseModel):
    """
    Payload do JWT Token (dados dentro do token)
    
    sub: Subject (user_id)
    exp: Expiration time (timestamp)
    """
    sub: int  # user_id
    exp: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    """Schema de requisição para renovar access token"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de senha"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset de senha"""
    token: str
    new_password: str = Field(..., min_length=8)

