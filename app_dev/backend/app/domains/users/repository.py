"""
Domínio Users - Repository
Camada de acesso a dados - TODAS as queries SQL isoladas aqui
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from .models import User

class UserRepository:
    """
    Repository pattern para usuários
    Isola TODAS as queries SQL do resto do sistema
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def list_all(self, apenas_ativos: bool = True) -> List[User]:
        """Lista todos os usuários"""
        query = self.db.query(User)
        
        if apenas_ativos:
            query = query.filter(User.ativo == 1)
        
        return query.order_by(User.nome).all()
    
    def count_all(self, apenas_ativos: bool = True) -> int:
        """Conta total de usuários"""
        query = self.db.query(func.count(User.id))
        
        if apenas_ativos:
            query = query.filter(User.ativo == 1)
        
        return query.scalar()
    
    def create(self, user: User) -> User:
        """Cria novo usuário"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """Atualiza usuário existente"""
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Deleta usuário (hard delete)"""
        self.db.delete(user)
        self.db.commit()
    
    def soft_delete(self, user: User) -> User:
        """Desativa usuário (soft delete)"""
        user.ativo = 0
        return self.update(user)
    
    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica se email já existe"""
        query = self.db.query(User).filter(User.email == email)
        
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        
        return query.first() is not None
