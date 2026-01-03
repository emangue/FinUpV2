"""
Models Flask-SQLAlchemy para API DEV
Versão simplificada focada em autenticação
"""
from datetime import datetime
from flask_login import UserMixin
import bcrypt
from app_dev.backend import db

class User(db.Model, UserMixin):
    """Modelo de usuários do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # admin/user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Define senha hasheada com bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verifica senha com bcrypt"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8') if isinstance(self.password_hash, str) else self.password_hash
        )
    
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


class JournalEntry(db.Model):
    """Transações financeiras"""
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    data = db.Column(db.DateTime, nullable=False, index=True)
    estabelecimento = db.Column(db.String(200), index=True)
    descricao = db.Column(db.Text)
    valororiginal = db.Column(db.Float, nullable=False)
    grupo = db.Column(db.String(100), index=True)
    marcacao = db.Column(db.String(100), index=True)
    tipodocumento = db.Column(db.String(50), index=True)  # Débito/Crédito
    banco = db.Column(db.String(100))
    origem = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    hash_unico = db.Column(db.String(64), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'data': self.data.isoformat() if self.data else None,
            'estabelecimento': self.estabelecimento,
            'descricao': self.descricao,
            'valororiginal': self.valororiginal,
            'grupo': self.grupo,
            'marcacao': self.marcacao,
            'tipodocumento': self.tipodocumento,
            'banco': self.banco,
            'origem': self.origem,
            'observacoes': self.observacoes
        }


class GrupoConfig(db.Model):
    """Configuração de grupos"""
    __tablename__ = 'grupo_config'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_grupo = db.Column(db.String(100), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    cor = db.Column(db.String(7))
    icone = db.Column(db.String(50))
    ordem = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_grupo': self.nome_grupo,
            'ativo': self.ativo,
            'cor': self.cor,
            'icone': self.icone,
            'ordem': self.ordem
        }
