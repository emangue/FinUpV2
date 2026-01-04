"""
Configurações do Backend API DEV
Versão: 1.0.0-dev
"""
import os
from datetime import timedelta
from pathlib import Path

# Base path é app_dev/
BASE_DIR = Path(__file__).parent.parent

class ConfigDev:
    """Configuração para desenvolvimento do novo frontend React"""
    
    # Banco de dados SEPARADO (dentro de app_dev/)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'financas_dev.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret Key (gerar nova para produção)
    SECRET_KEY = os.environ.get('SECRET_KEY_DEV') or 'dev-secret-key-change-in-production'
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS (permite frontend React)
    CORS_ORIGINS = [
        "http://localhost:3000",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Fallback
        "http://127.0.0.1:5173"
    ]
    
    # API Settings
    API_PREFIX = '/api/v1'
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Upload Settings (pasta separada dentro de app_dev)
    UPLOAD_FOLDER = str(BASE_DIR / 'uploads_temp')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'ofx'}
    
    # Session Settings (pasta separada dentro de app_dev)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = str(BASE_DIR / 'flask_session')
    
    # Static Files (pasta separada dentro de app_dev)
    STATIC_FOLDER = str(BASE_DIR / 'static')
    
    # Templates (pasta separada dentro de app_dev)
    TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
    
    # Debug
    DEBUG = True
    TESTING = False
