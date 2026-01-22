"""
Domínio Upload - Models
Contém o modelo PreviewTransacao e helpers
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from app.core.database import Base

class PreviewTransacao(Base):
    """
    Modelo de preview de transação para upload
    
    Armazena transações temporariamente antes da confirmação
    Isolado do resto do sistema para facilitar manutenção
    
    Campos preenchidos por fase:
    - Fase 1 (Raw): data, lancamento, valor, banco, tipo_documento, nome_cartao, nome_arquivo, data_criacao
    - Fase 2 (Marking): IdTransacao, IdParcela, EstabelecimentoBase, ParcelaAtual, TotalParcelas, ValorPositivo, TipoTransacao, Ano, Mes
    - Fase 3 (Classification): GRUPO, SUBGRUPO, TipoGasto, CategoriaGeral, origem_classificacao, padrao_buscado
    - Fase 4 (Deduplication): is_duplicate, duplicate_reason
    """
    __tablename__ = "preview_transacoes"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # Fase 1: Raw Data
    banco = Column(String, nullable=False)
    tipo_documento = Column(String)  # 'fatura' ou 'extrato'
    cartao = Column(String)  # Final do cartão
    nome_cartao = Column(String)  # Nome do cartão
    nome_arquivo = Column(String, nullable=False)
    mes_fatura = Column(String)  # Formato YYYY-MM
    data = Column(String, nullable=False)  # Data da transação DD/MM/YYYY
    lancamento = Column(String, nullable=False)  # Descrição/Estabelecimento
    valor = Column(Float, nullable=False)
    data_criacao = Column(DateTime)  # Quando arquivo foi processado
    
    # Fase 2: IDs e Normalização (CamelCase para compatibilidade legacy)
    IdTransacao = Column(String, index=True)  # FNV-1a hash
    IdParcela = Column(String, index=True)  # MD5 para parcelas
    EstabelecimentoBase = Column(String)  # Sem XX/YY
    ParcelaAtual = Column(Integer)  # Ex: 1
    TotalParcelas = Column(Integer)  # Ex: 12
    ValorPositivo = Column(Float)  # abs(valor)
    TipoTransacao = Column(String)  # "Cartão de Crédito", "Despesas", "Receitas"
    Ano = Column(Integer)  # 2025, 2026, etc
    Mes = Column(Integer)  # 1 a 12
    
    # Fase 3: Classificação (CamelCase para compatibilidade legacy)
    GRUPO = Column(String)
    SUBGRUPO = Column(String)
    TipoGasto = Column(String)
    CategoriaGeral = Column(String)
    origem_classificacao = Column(String)  # Base Parcelas, Base Padrões, etc
    padrao_buscado = Column(String)  # Debug: padrão montado usado na busca
    MarcacaoIA = Column(String)  # Sugestão da base_marcacoes (sempre preenchido)
    excluir = Column(Integer, default=0)  # 0 = importar, 1 = não importar
    
    # Fase 4: Deduplicação (futura)
    is_duplicate = Column(Boolean, default=False)
    duplicate_reason = Column(Text)
