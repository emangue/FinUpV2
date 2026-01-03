"""
Models do banco de dados SQLAlchemy

Versão: 2.1.1
Data: 28/12/2025
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

Define todas as tabelas do banco de dados e seus relacionamentos.
Qualquer mudança no schema deve seguir o workflow de versionamento:
1. python scripts/version_manager.py start app/models.py
2. Fazer modificações
3. python scripts/version_manager.py finish app/models.py "descrição"

Tabelas:
- JournalEntry: Transações finais processadas
- BaseParcelas: Controle de parcelas de compras
- BasePadrao: Padrões de classificação automática
- BaseMarcacao: Validação de classificações
- DuplicadoTemp: Detecção de duplicatas
- AuditLog: Log de operações
- GrupoConfig: Grupos de categorização
- EstabelecimentoLogo: Logos de estabelecimentos

Histórico:
- 2.2.0 (27/12/2025): Adiciona colunas banco e tipodocumento em JournalEntry
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base, UserMixin):
    """Modelo de usuários do sistema"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nome = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True)
    role = Column(String(20), default='user')  # admin/user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    transacoes = relationship('JournalEntry', back_populates='user', lazy='dynamic')
    parcelas = relationship('BaseParcelas', back_populates='user', lazy='dynamic')
    padroes_personalizados = relationship('BasePadrao', back_populates='user', lazy='dynamic')
    
    # Relacionamentos com outras contas (contas conectadas)
    relacionamentos_iniciados = relationship(
        'UserRelationship',
        foreign_keys='UserRelationship.user_id',
        back_populates='usuario_principal',
        lazy='dynamic'
    )
    relacionamentos_recebidos = relationship(
        'UserRelationship',
        foreign_keys='UserRelationship.connected_user_id',
        back_populates='usuario_conectado',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Define senha hasheada"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte para dicionário (sem senha)"""
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'ativo': self.ativo,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserRelationship(Base):
    """Relacionamento entre usuários (contas conectadas para visão consolidada)"""
    __tablename__ = 'user_relationships'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)  # Usuário principal
    connected_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)  # Usuário conectado
    status = Column(String(20), default='pending')  # pending, accepted, rejected
    view_consolidated = Column(Boolean, default=False)  # Se True, pode ver visão consolidada
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    usuario_principal = relationship('User', foreign_keys=[user_id], back_populates='relacionamentos_iniciados')
    usuario_conectado = relationship('User', foreign_keys=[connected_user_id], back_populates='relacionamentos_recebidos')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'connected_user_id': self.connected_user_id,
            'status': self.status,
            'view_consolidated': self.view_consolidated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }


class JournalEntry(Base):
    """Transações finais processadas e validadas"""
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable para migração
    IdTransacao = Column(String(64), unique=True, nullable=False, index=True)
    IdParcela = Column(String(64), nullable=True, index=True)  # Vincula parcelas da mesma compra
    Data = Column(String(10), nullable=False)  # DD/MM/AAAA
    Estabelecimento = Column(Text, nullable=False)
    Valor = Column(Float, nullable=False)
    ValorPositivo = Column(Float, nullable=False)
    TipoTransacao = Column(String(50))
    TipoTransacaoAjuste = Column(String(50))
    TipoGasto = Column(String(100))
    GRUPO = Column(String(100))
    SUBGRUPO = Column(String(100))
    Ano = Column(Integer)
    DT_Fatura = Column(String(6))  # AAAAMM
    NomeTitular = Column(String(200))
    DataPostagem = Column(String(10))  # DD/MM/AAAA
    origem = Column(String(50), nullable=False, index=True)
    banco = Column(String(50), nullable=True, index=True)  # Itaú, BTG, Mercado Pago, Genérico
    tipodocumento = Column(String(50), nullable=True)  # Extrato, Fatura Cartão de Crédito
    forma_classificacao = Column(String(50), nullable=True, index=True)  # Automática-BasePadrao, Automática-MarcacaoIA, Semi-Automática, Manual
    MarcacaoIA = Column(String(100))
    ValidarIA = Column(String(10))
    CartaoCodigo8 = Column(String(20))
    FinalCartao = Column(String(4))
    TipoLancamento = Column(String(20))
    TransacaoFutura = Column(String(3))
    IdOperacao = Column(String(20))  # Mercado Pago
    IgnorarDashboard = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    user = relationship('User', back_populates='transacoes')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'IdTransacao': self.IdTransacao,
            'Data': self.Data,
            'Estabelecimento': self.Estabelecimento,
            'Valor': self.Valor,
            'ValorPositivo': self.ValorPositivo,
            'TipoTransacao': self.TipoTransacao,
            'TipoTransacaoAjuste': self.TipoTransacaoAjuste,
            'TipoGasto': self.TipoGasto,
            'GRUPO': self.GRUPO,
            'SUBGRUPO': self.SUBGRUPO,
            'Ano': self.Ano,
            'DT_Fatura': self.DT_Fatura,
            'NomeTitular': self.NomeTitular,
            'DataPostagem': self.DataPostagem,
            'origem': self.origem,
            'banco': self.banco,
            'tipodocumento': self.tipodocumento,
            'forma_classificacao': self.forma_classificacao,
            'MarcacaoIA': self.MarcacaoIA,
            'ValidarIA': self.ValidarIA,
            'CartaoCodigo8': self.CartaoCodigo8,
            'FinalCartao': self.FinalCartao,
            'TipoLancamento': self.TipoLancamento,
            'TransacaoFutura': self.TransacaoFutura,
            'IdOperacao': self.IdOperacao,
            'IgnorarDashboard': self.IgnorarDashboard,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BaseParcelas(Base):
    """Base de dados de compras parceladas (contratos)"""
    __tablename__ = 'base_parcelas'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable para migração
    id_parcela = Column(String(64), unique=True, nullable=False, index=True)  # Hash único do contrato
    estabelecimento_base = Column(Text, nullable=False)  # Nome normalizado
    valor_parcela = Column(Float, nullable=False)
    qtd_parcelas = Column(Integer, nullable=False)
    
    # Classificação
    grupo_sugerido = Column(String(100))
    subgrupo_sugerido = Column(String(100))
    tipo_gasto_sugerido = Column(String(100))
    
    # Estado
    qtd_pagas = Column(Integer, default=0)
    valor_total_plano = Column(Float)
    data_inicio = Column(String(10))
    status = Column(String(20), default='ativo')  # ativo/finalizado
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = relationship('User', back_populates='parcelas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'id_parcela': self.id_parcela,
            'estabelecimento_base': self.estabelecimento_base,
            'valor_parcela': self.valor_parcela,
            'qtd_parcelas': self.qtd_parcelas,
            'grupo_sugerido': self.grupo_sugerido,
            'subgrupo_sugerido': self.subgrupo_sugerido,
            'tipo_gasto_sugerido': self.tipo_gasto_sugerido,
            'qtd_pagas': self.qtd_pagas,
            'status': self.status
        }


class BasePadrao(Base):
    """Padrões de classificação aprendidos automaticamente - Separados por usuário"""
    __tablename__ = 'base_padroes'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)  # Obrigatório - cada usuário tem seus padrões
    padrao_estabelecimento = Column(Text, nullable=False, index=True)  # UNIQUE com user_id
    padrao_num = Column(String(64), unique=True, nullable=False)
    contagem = Column(Integer, nullable=False)
    valor_medio = Column(Float, nullable=False)
    valor_min = Column(Float)
    valor_max = Column(Float)
    desvio_padrao = Column(Float)
    coef_variacao = Column(Float)
    percentual_consistencia = Column(Integer, nullable=False)
    confianca = Column(String(10), nullable=False)  # alta/media/baixa
    grupo_sugerido = Column(String(100))
    subgrupo_sugerido = Column(String(100))
    tipo_gasto_sugerido = Column(String(100))
    faixa_valor = Column(String(20))
    segmentado = Column(Boolean, default=False)
    exemplos = Column(Text)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    status = Column(String(10), default='ativo')  # ativo/inativo
    
    # Relacionamento
    user = relationship('User', back_populates='padroes_personalizados')
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'padrao_estabelecimento': self.padrao_estabelecimento,
            'padrao_num': self.padrao_num,
            'contagem': self.contagem,
            'valor_medio': self.valor_medio,
            'valor_min': self.valor_min,
            'valor_max': self.valor_max,
            'desvio_padrao': self.desvio_padrao,
            'coef_variacao': self.coef_variacao,
            'percentual_consistencia': self.percentual_consistencia,
            'confianca': self.confianca,
            'grupo_sugerido': self.grupo_sugerido,
            'subgrupo_sugerido': self.subgrupo_sugerido,
            'tipo_gasto_sugerido': self.tipo_gasto_sugerido,
            'faixa_valor': self.faixa_valor,
            'segmentado': self.segmentado,
            'exemplos': self.exemplos,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'status': self.status
        }


class BaseMarcacao(Base):
    """Marcações válidas (combinações de GRUPO/SUBGRUPO/TipoGasto)"""
    __tablename__ = 'base_marcacoes'
    
    id = Column(Integer, primary_key=True)
    GRUPO = Column(String(100), nullable=False)
    SUBGRUPO = Column(String(100), nullable=False)
    TipoGasto = Column(String(100), nullable=False)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'GRUPO': self.GRUPO,
            'SUBGRUPO': self.SUBGRUPO,
            'TipoGasto': self.TipoGasto
        }


class DuplicadoTemp(Base):
    """Duplicados temporários detectados durante o upload"""
    __tablename__ = 'duplicados_temp'
    
    id = Column(Integer, primary_key=True)
    IdTransacao = Column(String(64), nullable=False, index=True)
    Data = Column(String(10))
    Estabelecimento = Column(Text)
    Valor = Column(Float)
    origem = Column(String(50))
    motivo_duplicacao = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'IdTransacao': self.IdTransacao,
            'Data': self.Data,
            'Estabelecimento': self.Estabelecimento,
            'Valor': self.Valor,
            'origem': self.origem,
            'motivo_duplicacao': self.motivo_duplicacao,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    """Log de auditoria de modificações"""
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    acao = Column(String(20), nullable=False)  # INSERT/UPDATE/DELETE
    tabela = Column(String(50), nullable=False)
    registro_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Quem fez a ação
    dados_antes = Column(Text)  # JSON
    dados_depois = Column(Text)  # JSON
    ip_address = Column(String(45))
    session_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'acao': self.acao,
            'tabela': self.tabela,
            'registro_id': self.registro_id,
            'user_id': self.user_id,
            'dados_antes': self.dados_antes,
            'dados_depois': self.dados_depois,
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class GrupoConfig(Base):
    """Configuração de grupos (ícones e cores)"""
    __tablename__ = 'grupo_config'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    icone = Column(String(50), default='fa-tag')  # Classe do Font Awesome
    cor = Column(String(7), default='#6c757d')  # Hex color
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    ordem = Column(Integer, default=0)  # Para ordenação
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'icone': self.icone,
            'cor': self.cor,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'ordem': self.ordem,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EstabelecimentoLogo(Base):
    """Logos de estabelecimentos específicos"""
    __tablename__ = 'estabelecimento_logo'
    
    id = Column(Integer, primary_key=True)
    nome_busca = Column(String(200), unique=True, nullable=False, index=True)  # Nome para buscar (ex: "UBER", "Z DELI")
    nome_exibicao = Column(String(200))  # Nome para exibir (ex: "Uber", "Z Deli")
    arquivo_logo = Column(String(255), nullable=False)  # Nome do arquivo na pasta static/logos
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome_busca': self.nome_busca,
            'nome_exibicao': self.nome_exibicao,
            'arquivo_logo': self.arquivo_logo,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Criar engine e session
def get_db_session(db_path='financas.db'):
    """Retorna uma sessão do banco de dados"""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(db_path='financas.db'):
    """Inicializa o banco de dados"""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    print(f"✅ Banco de dados inicializado: {db_path}")
