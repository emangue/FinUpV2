"""
Repository do domínio Auth.
Usa UserRepository internamente.
"""
from sqlalchemy.orm import Session
from app.domains.users.repository import UserRepository


class AuthRepository:
    """Repository para operações de autenticação"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_by_email(self, email: str):
        """Busca usuário por email (para login)"""
        return self.user_repo.get_by_email(email)

    def get_user_by_id(self, user_id: int):
        """Busca usuário por ID (para /me)"""
        return self.user_repo.get_by_id(user_id)
