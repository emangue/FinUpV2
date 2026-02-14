"""
Domínio Categories - Model
Contém apenas o modelo BaseMarcacao isolado

IMPORTANTE (Sprint 2.0 - 23/01/2026):
- TipoGasto e CategoriaGeral foram REMOVIDOS da tabela
- Esses dados agora vêm de base_grupos_config via JOIN
- Chave única: GRUPO + SUBGRUPO
"""
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class BaseMarcacao(Base):
    """
    Modelo de categoria/marcação (grupos e subgrupos)
    
    Representa uma categoria de classificação de transações.
    Chave única: GRUPO + SUBGRUPO
    
    Para TipoGasto e CategoriaGeral, fazer JOIN com base_grupos_config:
        SELECT m.*, g.tipo_gasto_padrao, g.categoria_geral
        FROM base_marcacoes m
        JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo
    """
    __tablename__ = "base_marcacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)

