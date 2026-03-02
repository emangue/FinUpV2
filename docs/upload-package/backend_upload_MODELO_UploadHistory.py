"""
Model para histórico de uploads
Rastreabilidade completa de importações
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class UploadHistory(Base):
    """
    Histórico de uploads realizados
    Permite auditoria, troubleshooting e estatísticas
    """
    __tablename__ = "upload_history"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Identificação do upload
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    banco = Column(String(100), nullable=False)
    tipo_documento = Column(String(50), nullable=False)  # extrato/fatura
    nome_arquivo = Column(String(255), nullable=False)
    
    # Dados específicos de fatura
    nome_cartao = Column(String(100), nullable=True)
    final_cartao = Column(String(20), nullable=True)
    mes_fatura = Column(String(10), nullable=True)  # YYYYMM
    
    # Status do processamento
    status = Column(String(20), nullable=False, index=True)  # processing/success/error/cancelled
    
    # Contadores
    total_registros = Column(Integer, default=0)  # Total processado na Fase 1
    transacoes_importadas = Column(Integer, default=0)  # Confirmadas no journal_entries
    transacoes_duplicadas = Column(Integer, default=0)  # Filtradas como duplicatas
    
    # Estatísticas de classificação (JSON)
    classification_stats = Column(JSON, nullable=True)
    # Exemplo: {"base_parcelas": 10, "base_padroes": 5, "journal_entries": 3, ...}
    
    # Validação de saldo (para extratos) (JSON)
    balance_validation = Column(JSON, nullable=True)
    # Exemplo: {"saldo_inicial": 459.73, "saldo_final": 0.0, "soma_transacoes": -485.87, "is_valid": false, "diferenca": 26.14}
    
    # Timestamps
    data_upload = Column(DateTime, default=datetime.now, nullable=False)
    data_confirmacao = Column(DateTime, nullable=True)  # NULL se cancelado/erro
    
    # Erro (se status='error')
    error_message = Column(Text, nullable=True)
    
    # Relationships
    # user = relationship("User", back_populates="uploads")
    transactions = relationship("JournalEntry", back_populates="upload_history", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UploadHistory(id={self.id}, session_id={self.session_id}, banco={self.banco}, status={self.status})>"
