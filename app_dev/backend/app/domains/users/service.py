"""
Domínio Users - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime
from passlib.context import CryptContext

from .repository import UserRepository
from .models import User
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)

# Configuração do bcrypt para hash de senhas
# cost=12 = ~250ms de hash (equilibra segurança e performance)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash de senha usando bcrypt com salt automático
    
    Bcrypt é padrão da indústria:
    - Salt automático único para cada senha
    - Cost factor ajustável (12 = ~250ms)
    - Resistente a rainbow tables e brute force
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica senha em texto plano contra hash bcrypt
    
    Usado no login para validar credenciais
    
    IMPORTANTE: Apenas bcrypt é aceito. Hashes antigos (SHA256, pbkdf2) retornam False
    para forçar migração.
    """
    # Detecta senha antiga SHA256 (64 caracteres hex)
    if len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password):
        # SHA256 antiga - forçar migração
        return False
    
    # Detecta pbkdf2 (Flask-Bcrypt antigo)
    if hashed_password.startswith('pbkdf2:'):
        # pbkdf2 antigo - forçar migração
        return False
    
    # Verificar que é bcrypt válido ($2b$, $2a$, $2y$)
    if not (hashed_password.startswith('$2b$') or 
            hashed_password.startswith('$2a$') or 
            hashed_password.startswith('$2y$')):
        # Hash desconhecido - rejeitar
        return False
    
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # Se senha > 72 bytes (caso bcrypt antigo mal formatado)
        if "72 bytes" in str(e):
            return False
        raise

class UserService:
    """
    Service layer para usuários
    Contém TODA a lógica de negócio
    """
    
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def get_user(self, user_id: int) -> UserResponse:
        """
        Busca um usuário por ID
        
        Raises:
            HTTPException: Se usuário não encontrado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        return UserResponse.from_orm(user)
    
    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Busca um usuário por email
        
        Returns:
            UserResponse ou None se não encontrado
        """
        user = self.repository.get_by_email(email)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    def list_users(self, apenas_ativos: bool = True) -> UserListResponse:
        """
        Lista todos os usuários
        """
        users = self.repository.list_all(apenas_ativos)
        total = self.repository.count_all(apenas_ativos)
        
        return UserListResponse(
            users=[UserResponse.from_orm(u) for u in users],
            total=total
        )
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Cria novo usuário
        
        Lógica de negócio:
        - Verifica se email já existe
        - Hash da senha
        - Define timestamps
        
        Raises:
            HTTPException: Se email já existe
        """
        # Verificar se email já existe
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' já está cadastrado"
            )
        
        # Criar modelo
        now = datetime.now()
        user = User(
            email=user_data.email,
            nome=user_data.nome,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            ativo=1,
            created_at=now,
            updated_at=now
        )
        
        # Salvar
        created = self.repository.create(user)
        return UserResponse.from_orm(created)
    
    def update_user(
        self,
        user_id: int,
        update_data: UserUpdate
    ) -> UserResponse:
        """
        Atualiza usuário
        
        Raises:
            HTTPException: Se usuário não encontrado ou email duplicado
        """
        # Buscar usuário
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        # Verificar email duplicado
        if update_data.email and update_data.email != user.email:
            if self.repository.email_exists(update_data.email, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{update_data.email}' já está cadastrado"
                )
        
        # Aplicar mudanças (apenas campos não-None)
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "password":
                user.password_hash = hash_password(value)
            else:
                setattr(user, field, value)
        
        user.updated_at = datetime.now()
        
        # Salvar
        updated = self.repository.update(user)
        return UserResponse.from_orm(updated)
    
    def delete_user(self, user_id: int) -> dict:
        """
        Desativa usuário (soft delete)
        
        Raises:
            HTTPException: Se usuário não encontrado ou é admin principal
        """
        if user_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não é possível desativar o usuário administrador principal"
            )
        
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        user.updated_at = datetime.now()
        self.repository.soft_delete(user)
        return {"message": "Usuário desativado com sucesso"}
    
    def reset_password(self, user_id: int, nova_senha: str) -> dict:
        """
        Reseta a senha de um usuário
        
        Raises:
            HTTPException: Se usuário não encontrado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário com ID {user_id} não encontrado"
            )
        
        user.password_hash = hash_password(nova_senha)
        user.updated_at = datetime.now()
        
        self.repository.update(user)
        return {"message": "Senha alterada com sucesso"}
