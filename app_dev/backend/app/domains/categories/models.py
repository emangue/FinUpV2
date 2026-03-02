"""
Domínio Categories - Model
Contém apenas o modelo BaseMarcacao isolado

IMPORTANTE (Sprint 2.0 - 23/01/2026):
- TipoGasto e CategoriaGeral foram REMOVIDOS da tabela
- Esses dados agora vêm de base_grupos_config via JOIN
- Chave única: GRUPO + SUBGRUPO
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from app.core.database import Base


class BaseMarcacaoTemplate(Base):
    """
    Template global de marcações — base copiada para novos usuários.
    Fonte: generic_classification_rules. Raramente alterada.
    """
    __tablename__ = "base_marcacoes_template"
    __table_args__ = (UniqueConstraint("GRUPO", "SUBGRUPO", name="uq_base_marcacoes_template_grupo_sub"),)

    id = Column(Integer, primary_key=True, index=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)


class BaseMarcacao(Base):
    """
    Modelo de categoria/marcação (grupos e subgrupos)
    
    Representa uma categoria de classificação de transações.
    Chave única: user_id + GRUPO + SUBGRUPO
    
    Para TipoGasto e CategoriaGeral, fazer JOIN com base_grupos_config:
        SELECT m.*, g.tipo_gasto_padrao, g.categoria_geral
        FROM base_marcacoes m
        JOIN base_grupos_config g ON m.GRUPO = g.nome_grupo AND m.user_id = g.user_id
    """
    __tablename__ = "base_marcacoes"
    __table_args__ = (UniqueConstraint("user_id", "GRUPO", "SUBGRUPO", name="uq_base_marcacoes_user_grupo_sub"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    upload_history_id = Column(Integer, ForeignKey("upload_history.id"), nullable=True, index=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)

