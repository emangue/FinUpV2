"""
Domínio Cards - Model
Contém apenas o modelo Cartao isolado
"""
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class Cartao(Base):
    """
    Modelo de cartão de crédito
    
    Representa um cartão de crédito do usuário
    Isolado do resto do sistema para facilitar manutenção
    """
    __tablename__ = "cartoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_cartao = Column(String, nullable=False)
    final_cartao = Column(String(4), nullable=False)
    banco = Column(String, nullable=False)
    user_id = Column(Integer, index=True)
    ativo = Column(Integer, default=1)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
