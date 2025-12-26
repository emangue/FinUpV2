"""
Extensões Flask compartilhadas entre blueprints
"""
from flask_session import Session

# Inicializar extensões
session_manager = Session()

def init_extensions(app):
    """Inicializa todas as extensões Flask"""
    session_manager.init_app(app)
