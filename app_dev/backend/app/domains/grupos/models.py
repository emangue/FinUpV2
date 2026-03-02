"""
Domínio Grupos - Models
Definições de modelo para configuração de grupos
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from app.core.database import Base


class BaseGruposConfig(Base):
    __tablename__ = "base_grupos_config"
    __table_args__ = (UniqueConstraint("user_id", "nome_grupo", name="uq_base_grupos_config_user_nome"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    nome_grupo = Column(String(100), nullable=False, index=True)
    tipo_gasto_padrao = Column(String(50), nullable=False)
    categoria_geral = Column(String(50), nullable=False)
    cor = Column(String(7), nullable=True)
    is_padrao = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<BaseGruposConfig(nome_grupo='{self.nome_grupo}', categoria_geral='{self.categoria_geral}')>"


class BaseGruposTemplate(Base):
    """
    Template global de grupos — base copiada para novos usuários.
    Fonte: generic_classification_rules + complementos. Raramente alterada.
    """
    __tablename__ = "base_grupos_template"

    id = Column(Integer, primary_key=True, index=True)
    nome_grupo = Column(String(100), nullable=False, unique=True)
    tipo_gasto_padrao = Column(String(50), nullable=False)
    categoria_geral = Column(String(50), nullable=False)
    cor = Column(String(7), nullable=True)
