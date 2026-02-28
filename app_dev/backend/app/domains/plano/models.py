"""
Domínio Plano - Models
user_financial_profile, plano_metas_categoria
(plano_compromissos removido — volta ao legado, metas via budget_planning)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class UserFinancialProfile(Base):
    """Perfil financeiro do usuário - renda, aposentadoria, patrimônio"""
    __tablename__ = "user_financial_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    renda_mensal_liquida = Column(Float, nullable=True)
    idade_atual = Column(Integer, nullable=True)
    idade_aposentadoria = Column(Integer, nullable=True, default=65)
    patrimonio_atual = Column(Float, nullable=True, default=0)
    taxa_retorno_anual = Column(Float, nullable=True, default=0.08)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class PlanoMetaCategoria(Base):
    """Meta de gasto por grupo/categoria"""
    __tablename__ = "plano_metas_categoria"
    __table_args__ = (UniqueConstraint("user_id", "grupo", "ano", "mes", name="uq_plano_metas_user_grupo_ano_mes"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    grupo = Column(String(100), nullable=False)
    valor_meta = Column(Float, nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
