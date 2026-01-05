"""
Domínio Upload - Models
Contém o modelo PreviewTransacao e helpers
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

class PreviewTransacao(Base):
    """
    Modelo de preview de transação para upload
    
    Armazena transações temporariamente antes da confirmação
    Isolado do resto do sistema para facilitar manutenção
    """
    __tablename__ = "preview_transacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    banco = Column(String, nullable=False)
    cartao = Column(String)
    nome_arquivo = Column(String, nullable=False)
    mes_fatura = Column(String, nullable=False)  # Formato YYYY-MM
    data = Column(String, nullable=False)  # Data da transação
    lancamento = Column(String, nullable=False)  # Descrição
    valor = Column(Float, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
