"""
Flask Application Factory - Sistema de Gestão Financeira

Versão: 2.1.0
Data: 27/12/2025
Status: stable

Módulo principal do sistema que implementa o Application Factory Pattern.
Responsável por criar e configurar a aplicação Flask com todos os blueprints,
extensões e configurações necessárias.
"""
from flask import Flask
import os

__version__ = "2.1.0"

from app.config import Config
from app.models import init_db
from app.extensions import init_extensions
from app.filters import register_filters


def create_app(config_class=Config):
    """
    Application Factory Pattern
    Cria e configura a aplicação Flask com todos os blueprints
    """
    app = Flask(__name__,
                template_folder='../templates',  # Templates compartilhados na raiz
                static_folder='../static')        # Static files na raiz
    
    # Configuração
    app.config.from_object(config_class)
    app.secret_key = app.config['SECRET_KEY']
    
    # Criar diretórios necessários
    os.makedirs('uploads_temp', exist_ok=True)
    os.makedirs('static/logos', exist_ok=True)
    app.config['LOGOS_FOLDER'] = 'static/logos'
    app.config['MAX_LOGO_SIZE'] = 2 * 1024 * 1024  # 2MB
    
    # Inicializar extensões
    init_extensions(app)
    
    # Inicializar banco de dados
    init_db()
    
    # Registrar template filters globais
    register_filters(app)
    
    # Registrar Blueprints
    from app.blueprints.admin import admin_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.upload import upload_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    # Rota raiz redireciona para dashboard
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))
    
    return app
