"""
Domínio Transactions - Model
Contém apenas o modelo JournalEntry isolado
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base

class JournalEntry(Base):
    """
    Modelo de transação financeira
    
    Representa uma única transação no journal (extrato/fatura)
    Isolado do resto do sistema para facilitar manutenção
    """
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    
    # Dados principais
    Data = Column(String)  # Formato DD/MM/YYYY
    Estabelecimento = Column(String)
    Valor = Column(Float)
    ValorPositivo = Column(Float)
    TipoTransacao = Column(String)  # CREDITO/DEBITO
    
    # Classificação
    TipoGasto = Column(String)
    GRUPO = Column(String)
    SUBGRUPO = Column(String)
    CategoriaGeral = Column(String)
    
    # Identificação
    IdTransacao = Column(String, unique=True, index=True)
    IdParcela = Column(String)
    
    # Origem
    arquivo_origem = Column(String)
    banco_origem = Column(String)
    tipodocumento = Column(String)
    origem_classificacao = Column(String)
    
    # Dados temporais
    MesFatura = Column(String)  # Formato YYYYMM
    Ano = Column(Integer)
    created_at = Column(DateTime)
    
    # Cartão
    NomeCartao = Column(String)
    
    # Flags
    IgnorarDashboard = Column(Integer, default=0)
