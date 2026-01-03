"""
Configurações da aplicação Flask
"""
import os
from pathlib import Path

# Base path é app/
BASE_DIR = Path(__file__).parent

class Config:
    """Configurações da aplicação"""
    
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2025'
    
    # Banco de dados (dentro de app/)
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "financas.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de arquivos (dentro de app/)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_EXTENSIONS = {'.csv', '.xls', '.xlsx'}
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads_temp')
    # Nota: Com detecção automática de colunas, qualquer arquivo CSV/XLSX é aceito
    
    # Sessão (dentro de app/)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = str(BASE_DIR / 'flask_session')
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Static e Templates (dentro de app/)
    STATIC_FOLDER = str(BASE_DIR / 'static')
    TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
    
    # Paginação
    ITEMS_PER_PAGE = 20
    
    # Debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
