"""
Budget Planning Models
Modelo para planejamento orçamentário mensal

CHANGELOG 13/02/2026:
- ✅ Consolidação completa: budget_geral, budget_categoria_config, budget_geral_historico REMOVIDOS
- ✅ Apenas BudgetPlanning ativo
- ✅ Migration: 635e060a2434_consolidate_budget_tables
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from app.core.database import Base


class BudgetPlanning(Base):
    """
    Planejamento orçamentário mensal por Grupo
    Permite comparação Realizado vs Planejado no dashboard
    
    **ÚNICO modelo ativo após consolidação (13/02/2026)**
    """
    __tablename__ = "budget_planning"
    
    # PK
    id = Column(Integer, primary_key=True, index=True)
    
    # FK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Classificação
    grupo = Column(String(100), nullable=False)  # Casa, Cartão de Crédito, Saúde, etc
    
    # Período
    mes_referencia = Column(String(7), nullable=False, index=True)  # Formato: YYYY-MM
    
    # Valor
    valor_planejado = Column(Float, nullable=False)
    valor_medio_3_meses = Column(Float, nullable=False, default=0.0)  # Média dos últimos 3 meses
    
    # Cor no gráfico donut (hex, ex: #3b82f6)
    cor = Column(String(7), nullable=True)
    
    # Status
    ativo = Column(Integer, nullable=False, default=1)  # 0=inativo, 1=ativo (SQLite boolean as int)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<BudgetPlanning(id={self.id}, user_id={self.user_id}, grupo={self.grupo}, mes={self.mes_referencia}, valor={self.valor_planejado})>"


# ═══════════════════════════════════════════════════════════════════════════════
# REMOVIDO EM 13/02/2026 - Consolidação completa
# ═══════════════════════════════════════════════════════════════════════════════
# Tabelas deletadas via migration 635e060a2434_consolidate_budget_tables:
# - BudgetGeral → consolidado em BudgetPlanning
# - BudgetCategoriaConfig → não usado (0 registros)
# - BudgetGeralHistorico → não usado (0 registros)
#
# Se precisar acessar código antigo, veja:
# git show HEAD~1:app_dev/backend/app/domains/budget/models.py
# ═══════════════════════════════════════════════════════════════════════════════


