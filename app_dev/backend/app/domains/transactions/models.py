"""
Domínio Transactions - Model
Contém apenas o modelo JournalEntry isolado
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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
    upload_history_id = Column(Integer, ForeignKey("upload_history.id"), nullable=True, index=True)
    
    # Dados temporais
    MesFatura = Column(String)  # Formato YYYYMM
    Ano = Column(Integer)
    created_at = Column(DateTime)
    
    # Cartão
    NomeCartao = Column(String)
    
    # Flags
    IgnorarDashboard = Column(Integer, default=0)
    
    # Relationships
    upload_history = relationship("UploadHistory", back_populates="transactions")


class BaseParcelas(Base):
    """
    Modelo da tabela base_parcelas
    Contém informações de parcelamentos
    """
    __tablename__ = "base_parcelas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    
    # Identificação
    id_parcela = Column(String, index=True)
    estabelecimento_base = Column(String)
    
    # Dados da parcela
    valor_parcela = Column(Float)
    qtd_parcelas = Column(Integer)
    qtd_pagas = Column(Integer)
    valor_total_plano = Column(Float)
    
    # Classificação sugerida
    grupo_sugerido = Column(String)
    subgrupo_sugerido = Column(String)
    tipo_gasto_sugerido = Column(String)
    
    # Controle
    data_inicio = Column(String)  # Formato DD/MM/YYYY
    status = Column(String)  # ativa, finalizado, cancelada
    
    # Temporal
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
