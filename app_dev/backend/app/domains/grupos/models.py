"""
Domínio Grupos - Models
Definições de modelo para configuração de grupos
"""
from sqlalchemy import Column, Integer, String
from app.core.database import Base


class BaseGruposConfig(Base):
    __tablename__ = "base_grupos_config"

    id = Column(Integer, primary_key=True, index=True)
    nome_grupo = Column(String, unique=True, nullable=False, index=True)
    tipo_gasto_padrao = Column(String, nullable=False)
    categoria_geral = Column(String, nullable=False)
    cor = Column(String(7), nullable=True)  # Sprint C: hex para paleta (ex: #001D39)

    def __repr__(self):
        return f"<BaseGruposConfig(nome_grupo='{self.nome_grupo}', categoria_geral='{self.categoria_geral}')>"