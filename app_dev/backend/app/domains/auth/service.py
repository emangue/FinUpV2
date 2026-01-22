"""
Service do domínio Auth.
Lógica de negócio isolada.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import AuthRepository
from .schemas import LoginRequest, TokenResponse, UserLoginResponse, ProfileUpdateRequest, PasswordChangeRequest
from .password_utils import verify_password, hash_password
from .jwt_utils import create_access_token
from datetime import datetime


class AuthService:
    """Service para autenticação"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuthRepository(db)

    def login(self, credentials: LoginRequest) -> TokenResponse:
        """
        Autentica usuário e retorna token JWT
        
        Args:
            credentials: Email e senha
            
        Returns:
            TokenResponse com access_token e dados do usuário
            
        Raises:
            HTTPException 401: Credenciais inválidas ou usuário inativo
        """
        # Buscar usuário por email
        user = self.repository.get_user_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Verificar se usuário está ativo
        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário desativado. Contate o administrador."
            )
        
        # Verificar senha
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        # Gerar token JWT
        access_token = create_access_token(
            data={"user_id": user.id, "email": user.email, "role": user.role}
        )
        
        # Retornar resposta
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserLoginResponse.model_validate(user)
        )

    def get_current_user(self, user_id: int) -> UserLoginResponse:
        """
        Busca usuário atual (endpoint /me)
        
        Args:
            user_id: ID do usuário do token JWT
            
        Returns:
            Dados do usuário
            
        Raises:
            HTTPException 404: Usuário não encontrado
        """
        user = self.repository.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        if not user.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário desativado"
            )
        
        return UserLoginResponse.model_validate(user)
    
    def update_profile(self, user_id: int, profile_data: ProfileUpdateRequest) -> UserLoginResponse:
        """
        Atualiza perfil do usuário autenticado
        
        Args:
            user_id: ID do usuário do token JWT
            profile_data: Novos dados (nome, email)
            
        Returns:
            Dados atualizados do usuário
            
        Raises:
            HTTPException 404: Usuário não encontrado
            HTTPException 400: Email já em uso por outro usuário
        """
        user = self.repository.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se email já está em uso por outro usuário
        if profile_data.email != user.email:
            existing_user = self.repository.get_user_by_email(profile_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{profile_data.email}' já está em uso"
                )
        
        # Atualizar dados
        user.nome = profile_data.nome
        user.email = profile_data.email
        user.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(user)
        
        return UserLoginResponse.model_validate(user)
    
    def change_password(self, user_id: int, password_data: PasswordChangeRequest) -> dict:
        """
        Altera senha do usuário autenticado
        
        Args:
            user_id: ID do usuário do token JWT
            password_data: Senha atual e nova senha
            
        Returns:
            Mensagem de sucesso
            
        Raises:
            HTTPException 404: Usuário não encontrado
            HTTPException 400: Senha atual incorreta
        """
        user = self.repository.get_user_by_id(user_id)
        
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
        
        self.db.commit()
        
        return {"message": "Senha alterada com sucesso"}
