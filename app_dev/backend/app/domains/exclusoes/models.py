from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class TransacaoExclusao(Base):
    __tablename__ = "transacoes_exclusao"

    id = Column(Integer, primary_key=True, index=True)
    nome_transacao = Column(String, nullable=False, index=True)
    banco = Column(String, nullable=True)
    descricao = Column(String, nullable=True)
    user_id = Column(Integer, nullable=False, index=True)
    ativo = Column(Integer, default=1)
    tipo_documento = Column(String, nullable=True)  # 'cartao', 'extrato', 'ambos'
    acao = Column(String, nullable=False, default="EXCLUIR")  # 'EXCLUIR' ou 'IGNORAR'
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
