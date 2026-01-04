"""
Modelos SQLAlchemy para o banco de dados existente
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from ..database import Base

class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)  # Corrigido: nome ao invés de name
    ativo = Column(Integer, default=1)  # Corrigido: ativo (INTEGER) ao invés de active
    role = Column(String(20), default="user")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class JournalEntry(Base):
    """Modelo de transação financeira"""
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    IdTransacao = Column(String, unique=True, index=True)
    Data = Column(String)  # Formato DD/MM/YYYY
    Estabelecimento = Column(String)
    Valor = Column(Float)
    ValorPositivo = Column(Float)
    TipoTransacao = Column(String)
    TipoGasto = Column(String)
    GRUPO = Column(String)
    SUBGRUPO = Column(String)
    Ano = Column(String)
    MesFatura = Column(String)  # Formato YYYYMM
    DT_Fatura = Column(String)  # Formato YYYYMM
    DataPostagem = Column(String)
    IdParcela = Column(String)
    banco_origem = Column(String)
    tipodocumento = Column(String)
    arquivo_origem = Column(String)
    origem_classificacao = Column(String)
    ValidarIA = Column(String)
    MarcacaoIA = Column(String)
    CategoriaGeral = Column(String)
    IgnorarDashboard = Column(Integer, default=0)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BaseMarcacao(Base):
    """Modelo de categoria/marcação"""
    __tablename__ = "base_marcacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    GRUPO = Column(String, nullable=False)
    SUBGRUPO = Column(String, nullable=False)
    TipoGasto = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BankFormatCompatibility(Base):
    """Modelo de compatibilidade de bancos"""
    __tablename__ = "bank_format_compatibility"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    file_format = Column(String, nullable=False)  # CSV, XLS, XLSX, OFX
    status = Column(String, nullable=False)  # OK, WIP, TBD
    notes = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class BaseParcelas(Base):
    """Modelo de contratos parcelados"""
    __tablename__ = "base_parcelas"
    
    id = Column(Integer, primary_key=True, index=True)
    IdParcela = Column(String, unique=True, index=True)
    estabelecimento_base = Column(String)
    total_parcelas = Column(Integer)
    valor_total = Column(Float)
    valor_parcela = Column(Float)
    GRUPO = Column(String)
    SUBGRUPO = Column(String)
    TipoGasto = Column(String)
    origem_classificacao = Column(String)
    user_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
