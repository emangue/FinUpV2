"""
Domínio Plano - Models
user_financial_profile, plano_metas_categoria, base_expectativas
(plano_compromissos removido — volta ao legado, metas via budget_planning)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

from app.core.database import Base


class BaseExpectativa(Base):
    """
    Camada de projeção — sazonais, parcelas futuras, ganhos extras.
    tipo_expectativa: 'sazonal_plano' | 'renda_plano' | 'parcela_futura'
    """
    __tablename__ = "base_expectativas"
    __table_args__ = (
        UniqueConstraint("user_id", "id_parcela", "parcela_seq", name="uq_expectativa_parcela"),
        Index("idx_expectativas_user_mes", "user_id", "mes_referencia"),
        Index("idx_expectativas_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    descricao = Column(String(200), nullable=True)
    valor = Column(Float, nullable=False)
    grupo = Column(String(100), nullable=True)
    subgrupo = Column(String(100), nullable=True)
    metadata_json = Column(String(2000), nullable=True)
    tipo_lancamento = Column(String(10), default="debito")  # debito | credito
    mes_referencia = Column(String(7), nullable=False, index=True)  # YYYY-MM
    tipo_expectativa = Column(String(30), nullable=False)
    origem = Column(String(20), nullable=False)  # usuario | sistema
    id_parcela = Column(String(64), index=True, nullable=True)
    parcela_seq = Column(Integer, nullable=True)
    parcela_total = Column(Integer, nullable=True)
    status = Column(String(20), default="pendente", index=True)  # pendente | realizado | divergente | cancelado
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)
    valor_realizado = Column(Float, nullable=True)
    realizado_em = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ExpectativaMes(Base):
    """
    Materialização dos extraordinários expandidos por mês.
    Usada para leitura rápida em get_cashflow, get_orcamento, get_resumo.
    Total planejado = budget_planning.valor_planejado + SUM(expectativas_mes.valor) por grupo/mês.
    """
    __tablename__ = "expectativas_mes"
    __table_args__ = (
        Index("idx_expectativas_mes_user_mes", "user_id", "mes_referencia"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mes_referencia = Column(String(7), nullable=False, index=True)  # YYYY-MM
    grupo = Column(String(100), nullable=True)
    subgrupo = Column(String(100), nullable=True)
    tipo = Column(String(10), default="debito")  # debito | credito
    valor = Column(Float, nullable=False)
    origem_expectativa_id = Column(Integer, ForeignKey("base_expectativas.id"), nullable=True)


class UserFinancialProfile(Base):
    """Perfil financeiro do usuário - renda, aposentadoria, patrimônio"""
    __tablename__ = "user_financial_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    renda_mensal_liquida = Column(Float, nullable=True)
    aporte_planejado = Column(Float, nullable=True, default=0)
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
