"""
Configurações da aplicação Flask
"""
import os

class Config:
    """Configurações da aplicação"""
    
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2025'
    
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///financas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_EXTENSIONS = {'.csv', '.xls', '.xlsx'}
    # Nota: Com detecção automática de colunas, qualquer arquivo CSV/XLSX é aceito
    
    # Sessão
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Paginação
    ITEMS_PER_PAGE = 20
    
    # Debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
