"""
Domínio Patterns - Model
Modelo de padrões de classificação automática
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, UniqueConstraint
from app.core.database import Base


class BasePadroes(Base):
    """
    Modelo de padrão de classificação automática
    
    Armazena padrões aprendidos para classificação automática de transações
    baseados em histórico e consistência de classificações
    """
    __tablename__ = "base_padroes"
    __table_args__ = (
        UniqueConstraint('user_id', 'padrao_num', name='base_padroes_user_id_padrao_num_key'),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Identificação do padrão
    padrao_estabelecimento = Column(Text, nullable=False)  # Ex: "CONTA VIVO [50-100]"
    padrao_num = Column(Text, nullable=False)  # Hash FNV-1a — único por (user_id, padrao_num)
    
    # Estatísticas
    contagem = Column(Integer, nullable=False)  # Quantas ocorrências
    valor_medio = Column(Float, nullable=False)
    valor_min = Column(Float)
    valor_max = Column(Float)
    desvio_padrao = Column(Float)
    coef_variacao = Column(Float)
    percentual_consistencia = Column(Integer, nullable=False)  # % de consistência da classificação
    
    # Confiança e classificação sugerida
    confianca = Column(Text, nullable=False)  # 'alta', 'media', 'baixa'
    grupo_sugerido = Column(Text)
    subgrupo_sugerido = Column(Text)
    tipo_gasto_sugerido = Column(Text)
    categoria_geral_sugerida = Column(Text)  # CategoriaGeral derivada de base_grupos_config
    
    # Segmentação
    faixa_valor = Column(Text)  # Ex: "50-100", "FIXO 57.00"
    segmentado = Column(Integer, default=0)  # Boolean: 0 ou 1
    
    # Metadados
    exemplos = Column(Text)  # Lista de exemplos separados por "; "
    data_criacao = Column(DateTime)
    status = Column(Text, default='ativo')  # 'ativo', 'inativo'
