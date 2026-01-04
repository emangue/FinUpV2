"""
Extensões Flask compartilhadas entre blueprints
"""
from flask_session import Session
from flask_login import LoginManager

# Inicializar extensões
session_manager = Session()
login_manager = LoginManager()

def init_extensions(app):
    """Inicializa todas as extensões Flask"""
    session_manager.init_app(app)
    
    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carrega usuário por ID"""
        from app.models import User, get_db_session
        db = get_db_session()
        return db.query(User).get(int(user_id))
