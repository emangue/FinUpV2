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
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetGeral(id={self.id}, user_id={self.user_id}, categoria={self.categoria_geral}, mes={self.mes_referencia}, valor={self.valor_planejado})>"

