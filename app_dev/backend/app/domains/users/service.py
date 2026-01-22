"""
Domínio Users - Service
Lógica de negócio isolada
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime

from .repository import UserRepository
from .models import User
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    ProfileUpdate,
    PasswordChange
)
from ..auth.password_utils import hash_password, verify_password  # bcrypt

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
    
    def update_profile(
        self,
        user_id: int,
        profile_data: ProfileUpdate
    ) -> UserResponse:
        """
        Atualiza perfil do usuário autenticado
        
        Lógica de negócio:
        - Usuário só pode alterar seu próprio perfil
        - Valida se email não está em uso por outro usuário
        
        Raises:
            HTTPException: Se usuário não encontrado ou email duplicado
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se email já está em uso por outro usuário
        if profile_data.email != user.email:
            if self.repository.email_exists(profile_data.email, user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{profile_data.email}' já está cadastrado"
                )
        
        # Atualizar campos
        user.nome = profile_data.nome
        user.email = profile_data.email
        user.updated_at = datetime.now()
        
        updated = self.repository.update(user)
        return UserResponse.from_orm(updated)
    
    def change_password(
        self,
        user_id: int,
        password_data: PasswordChange
    ) -> dict:
        """
        Altera a senha do usuário autenticado
        
        Lógica de negócio:
        - Verifica se senha atual está correta
        - Hash da nova senha
        - Atualiza timestamp
        
        Raises:
            HTTPException: Se usuário não encontrado ou senha atual incorreta
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar senha atual
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Atualizar senha
        user.password_hash = hash_password(password_data.new_password)
        user.updated_at = datetime.now()
        
        self.repository.update(user)
        return {"message": "Senha alterada com sucesso"}

