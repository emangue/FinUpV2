"""
Schemas Pydantic do domínio Auth.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Response com token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: "UserLoginResponse"


class UserLoginResponse(BaseModel):
    """Dados do usuário após login"""
    id: int
    email: str
    nome: str
    role: str

    class Config:
        from_attributes = True


class LogoutRequest(BaseModel):
    """Request para logout (opcional)"""
    pass


class ProfileUpdateRequest(BaseModel):
    """Request para atualizar perfil"""
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    """Request para alterar senha"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
