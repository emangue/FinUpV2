"""
Domínio Categories - Model
Contém apenas o modelo BaseMarcacao isolado
"""
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class BaseMarcacao(Base):
    """
    Modelo de categoria/marcação
    
    Representa uma categoria de classificação de transações
    (GRUPO, SUBGRUPO, TipoGasto)
    Isolado do resto do sistema para facilitar manutenção
    """
    __tablename__ = "base_marcacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    GRUPO = Column(String, nullable=False)
    SUBGRUPO = Column(String, nullable=False)
    TipoGasto = Column(String, nullable=False)
