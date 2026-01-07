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
    - Fase 2 (Marking): id_transacao, id_parcela, estabelecimento_base, parcela_atual, total_parcelas, valor_positivo
    - Fase 3 (Classification): grupo, subgrupo, tipo_gasto, categoria_geral, origem_classificacao
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
    
    # Fase 2: IDs e Normalização
    id_transacao = Column(String, index=True)  # FNV-1a hash
    id_parcela = Column(String, index=True)  # MD5 para parcelas
    estabelecimento_base = Column(String)  # Sem XX/YY
    parcela_atual = Column(Integer)  # Ex: 1
    total_parcelas = Column(Integer)  # Ex: 12
    valor_positivo = Column(Float)  # abs(valor)
    
    # Fase 3: Classificação
    grupo = Column(String)
    subgrupo = Column(String)
    tipo_gasto = Column(String)
    categoria_geral = Column(String)
    origem_classificacao = Column(String)  # Base Parcelas, Base Padrões, etc
    
    # Fase 4: Deduplicação (futura)
    is_duplicate = Column(Boolean, default=False)
    duplicate_reason = Column(Text)
