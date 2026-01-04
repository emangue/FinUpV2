"""
Dependências simples para preparação futura de multi-usuário
Por enquanto, sempre retorna user_id = 1
"""
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

def get_current_user_id() -> int:
    """
    Retorna o ID do usuário atual
    
    Por enquanto fixo em 1 (admin padrão)
    No futuro será substituído por lógica de autenticação real (JWT)
    """
    return 1

def get_current_user(db: Session) -> User:
    """
    Retorna o usuário atual completo
    Por enquanto sempre retorna user_id = 1
    """
    user = db.query(User).filter(User.id == 1).first()
    return user
