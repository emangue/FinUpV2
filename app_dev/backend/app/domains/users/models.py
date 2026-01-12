"""
Domínio Users - Model
Contém modelos User e RefreshToken isolados
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    """
    Modelo de usuário
    
    Representa um usuário do sistema
    Isolado do resto do sistema para facilitar manutenção
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)
    ativo = Column(Integer, default=1)
    role = Column(String(20), default="user")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Relationship com refresh tokens
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """
    Modelo de Refresh Token para autenticação JWT
    
    Armazena refresh tokens válidos para renovar access tokens
    - Access token expira rápido (15min) = mais seguro
    - Refresh token expira lento (7 dias) = menos re-logins
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Integer, default=0)  # 0=ativo, 1=revogado
    
    # Relationship com user
    user = relationship("User", back_populates="refresh_tokens")

