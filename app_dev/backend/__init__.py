"""
Backend API Flask - Versão DEV
Sistema de Gestão Financeira v4.0.0-dev

API REST para frontend React moderno
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Inicializa extensões
db = SQLAlchemy()
jwt = JWTManager()

def create_app_dev():
    """Factory para criar aplicação Flask API"""
    app = Flask(__name__)
    
    # Carrega configurações
    from .config_dev import ConfigDev
    app.config.from_object(ConfigDev)
    
    # Inicializa extensões
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Range", "X-Content-Range"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })
    
    # Registra blueprints API
    from .api.blueprints import auth_dev, dashboard_dev, transactions_dev, test_dev
    
    api_prefix = app.config['API_PREFIX']
    app.register_blueprint(auth_dev.bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(dashboard_dev.bp, url_prefix=f'{api_prefix}/dashboard')
    app.register_blueprint(transactions_dev.bp, url_prefix=f'{api_prefix}/transactions')
    app.register_blueprint(test_dev.bp, url_prefix=f'{api_prefix}/test')
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'version': '4.0.0-dev'}, 200
    
    return app
