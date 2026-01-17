"""
Modelos de dados do domínio Investimentos.

Gerencia portfólio de investimentos, histórico mensal, cenários e planejamento.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Numeric, Boolean, DateTime, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class InvestimentoPortfolio(Base):
    """
    Representa um produto de investimento no portfólio do usuário.
    """
    __tablename__ = "investimentos_portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Identificação única
    balance_id = Column(String(100), unique=True, nullable=False, index=True)
    nome_produto = Column(String(255), nullable=False)
    corretora = Column(String(100), nullable=False)
    
    # Temporal - mês de referência do registro
    ano = Column(Integer, nullable=True, index=True)
    anomes = Column(Integer, nullable=True, index=True)  # YYYYMM para facilitar queries
    
    # Classificação
    tipo_investimento = Column(String(50), nullable=False, index=True)  # FII, Renda Fixa, Ação, etc.
    classe_ativo = Column(String(50))  # Ativo/Passivo
    emissor = Column(String(100))
    
    # Características do produto
    percentual_cdi = Column(Float)  # Para produtos atrelados ao CDI
    data_aplicacao = Column(Date)
    data_vencimento = Column(Date)
    
    # Valores iniciais
    quantidade = Column(Float, default=1.0)
    valor_unitario_inicial = Column(Numeric(15, 2))
    valor_total_inicial = Column(Numeric(15, 2))
    
    # Controle
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relacionamentos
    historico = relationship("InvestimentoHistorico", back_populates="investimento", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[user_id])
    
    # Índices compostos para otimização
    __table_args__ = (
        Index('idx_user_tipo', 'user_id', 'tipo_investimento'),
        Index('idx_user_ativo', 'user_id', 'ativo'),
        Index('idx_user_anomes', 'user_id', 'anomes'),
    )


class InvestimentoHistorico(Base):
    """
    Histórico mensal de valores de um investimento.
    Armazena a evolução do investimento mês a mês.
    """
    __tablename__ = "investimentos_historico"

    id = Column(Integer, primary_key=True, index=True)
    investimento_id = Column(Integer, ForeignKey('investimentos_portfolio.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Temporal
    ano = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    anomes = Column(Integer, nullable=False, index=True)  # YYYYMM para facilitar queries
    data_referencia = Column(Date, nullable=False)  # Último dia do mês
    
    # Valores do mês
    quantidade = Column(Float)
    valor_unitario = Column(Numeric(15, 2))
    valor_total = Column(Numeric(15, 2))
    aporte_mes = Column(Numeric(15, 2), default=0)  # Valor aplicado no mês
    
    # Métricas calculadas
    rendimento_mes = Column(Numeric(15, 2))
    rendimento_acumulado = Column(Numeric(15, 2))
    
    # Controle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relacionamentos
    investimento = relationship("InvestimentoPortfolio", back_populates="historico")
    
    # Índices compostos
    __table_args__ = (
        Index('idx_investimento_anomes', 'investimento_id', 'anomes'),
        Index('idx_anomes', 'anomes'),
    )


class InvestimentoCenario(Base):
    """
    Cenários de simulação de crescimento patrimonial.
    Permite criar diferentes projeções com parâmetros customizáveis.
    """
    __tablename__ = "investimentos_cenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Identificação
    nome_cenario = Column(String(100), nullable=False)
    descricao = Column(String(500))
    ativo = Column(Boolean, default=True, index=True)
    
    # Parâmetros base
    patrimonio_inicial = Column(Numeric(15, 2), nullable=False)
    rendimento_mensal_pct = Column(Numeric(6, 4), nullable=False)  # Ex: 0.0080 = 0.8%
    aporte_mensal = Column(Numeric(15, 2), default=0)
    periodo_meses = Column(Integer, default=120)  # 10 anos padrão
    
    # Controle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relacionamentos
    aportes_extraordinarios = relationship("AporteExtraordinario", back_populates="cenario", cascade="all, delete-orphan")
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_user_ativo_cenario', 'user_id', 'ativo'),
    )


class AporteExtraordinario(Base):
    """
    Aportes extraordinários dentro de um cenário.
    Exemplos: 13º salário, bônus anual, venda de ativo.
    """
    __tablename__ = "investimentos_aportes_extraordinarios"

    id = Column(Integer, primary_key=True, index=True)
    cenario_id = Column(Integer, ForeignKey('investimentos_cenarios.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Temporal
    mes_referencia = Column(Integer, nullable=False)  # Mês 1, 2, 3... (relativo ao início do cenário)
    
    # Valores
    valor = Column(Numeric(15, 2), nullable=False)
    descricao = Column(String(255))  # Ex: "13º salário", "Bonus anual"
    
    # Controle
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cenario = relationship("InvestimentoCenario", back_populates="aportes_extraordinarios")


class InvestimentoPlanejamento(Base):
    """
    Planejamento e metas mensais de investimentos.
    Compara metas vs. realizações.
    """
    __tablename__ = "investimentos_planejamento"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Temporal
    ano = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)
    anomes = Column(Integer, nullable=False, index=True)  # YYYYMM
    
    # Metas
    meta_aporte_mensal = Column(Numeric(15, 2))
    meta_rendimento_pct = Column(Numeric(6, 4))  # Percentual esperado
    meta_patrimonio = Column(Numeric(15, 2))
    
    # Realizações
    aporte_realizado = Column(Numeric(15, 2))
    rendimento_realizado = Column(Numeric(15, 2))
    patrimonio_realizado = Column(Numeric(15, 2))
    
    # Controle
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_user_anomes_plan', 'user_id', 'anomes'),
    )
