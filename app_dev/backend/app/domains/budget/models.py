"""
Budget Planning Models
Modelo para planejamento orçamentário mensal
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class BudgetPlanning(Base):
    """
    Planejamento orçamentário mensal por TipoGasto
    Permite comparação Realizado vs Planejado no dashboard
    """
    __tablename__ = "budget_planning"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Classificação
    tipo_gasto = Column(String(50), nullable=False)  # Fixo, Ajustável, Essencial, etc
    
    # Período
    mes_referencia = Column(String(7), nullable=False, index=True)  # Formato: YYYY-MM
    
    # Valor
    valor_planejado = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetPlanning(id={self.id}, user_id={self.user_id}, tipo_gasto={self.tipo_gasto}, mes={self.mes_referencia}, valor={self.valor_planejado})>"


class BudgetGeral(Base):
    """
    Planejamento orçamentário geral por categoria ampla
    Categorias: Casa, Cartão de Crédito, Doações, Saúde, Viagens, Outros
    """
    __tablename__ = "budget_geral"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Classificação
    categoria_geral = Column(String(50), nullable=False)  # Casa, Cartão de Crédito, etc
    
    # Período
    mes_referencia = Column(String(7), nullable=False, index=True)  # Formato: YYYY-MM
    
    # Valor
    valor_planejado = Column(Float, nullable=False)
    total_mensal = Column(Float, nullable=True)  # Budget geral total do mês (teto)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetGeral(id={self.id}, user_id={self.user_id}, categoria={self.categoria_geral}, mes={self.mes_referencia}, valor={self.valor_planejado})>"


class BudgetCategoriaConfig(Base):
    """
    Configuração de categorias de orçamento personalizáveis
    Define ordem (hierarquia), fonte de dados, cores e TipoGasto incluídos
    """
    __tablename__ = "budget_categoria_config"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Configuração
    nome_categoria = Column(String(100), nullable=False)  # Ex: "Casa", "Cartão de Crédito"
    ordem = Column(Integer, nullable=False, default=999)  # Ordem de exibição e hierarquia
    fonte_dados = Column(String(20), nullable=False)  # "GRUPO" ou "TIPO_TRANSACAO"
    filtro_valor = Column(String(100), nullable=False)  # Valor a filtrar (ex: "Moradia" ou "Cartão")
    tipos_gasto_incluidos = Column(String(1000), nullable=True)  # JSON array de TipoGasto
    cor_visualizacao = Column(String(7), nullable=False, default="#94a3b8")  # Hex color
    ativo = Column(Integer, nullable=False, default=1)  # 0=inativo, 1=ativo
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetCategoriaConfig(id={self.id}, user={self.user_id}, nome={self.nome_categoria}, ordem={self.ordem})>"


class BudgetGeralHistorico(Base):
    """
    Histórico de ajustes automáticos no budget geral total
    Registra quando sistema ajustou total automaticamente
    """
    __tablename__ = "budget_geral_historico"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Dados do ajuste
    mes_referencia = Column(String(7), nullable=False, index=True)
    valor_anterior = Column(Float, nullable=False)
    valor_novo = Column(Float, nullable=False)
    motivo = Column(String(500), nullable=False)  # Ex: "Soma das categorias ultrapassou o total"
    soma_categorias = Column(Float, nullable=False)  # Valor que causou o ajuste
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetGeralHistorico(id={self.id}, user={self.user_id}, mes={self.mes_referencia}, {self.valor_anterior}->{self.valor_novo})>"

