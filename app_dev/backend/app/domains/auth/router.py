"""
Router do domínio Auth.
Endpoints FastAPI isolados aqui.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.shared.dependencies import get_current_user_id
from .service import AuthService
from .schemas import LoginRequest, TokenResponse, UserLoginResponse, LogoutRequest, ProfileUpdateRequest, PasswordChangeRequest
from .jwt_utils import extract_user_id_from_token


router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # Máximo 5 tentativas de login por minuto
def login(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna token JWT
    
    **Rate Limit:** 5 tentativas por minuto (proteção contra brute force)
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    
    Returns:
        - access_token: Token JWT
        - token_type: "bearer"
        - user: Dados do usuário
    """
    service = AuthService(db)
    return service.login(credentials)


@router.get("/me", response_model=UserLoginResponse)
def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Retorna dados do usuário autenticado
    
    Requer token JWT válido no header Authorization
    """
    # ✅ CORRIGIDO: user_id agora vem do JWT token
    
    service = AuthService(db)
    return service.get_current_user(user_id)


@router.post("/logout", status_code=204)
def logout(
    data: LogoutRequest = None,
    db: Session = Depends(get_db)
):
    """
    Logout do usuário (invalidação de token)
    
    Por enquanto apenas retorna 204 (token é stateless)
    Futuramente: blacklist de tokens
    """
    # TODO: Implementar blacklist de tokens (Fase 6)
    return None


def get_user_id_from_token(authorization: Optional[str] = Header(None)) -> int:
    """
    Extrai user_id do token JWT no header Authorization
    
    Raises:
        HTTPException 401: Se token não fornecido ou inválido
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    user_id = extract_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


@router.put("/profile", response_model=UserLoginResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil do usuário autenticado
    
    Requer token JWT válido no header Authorization.
    Permite atualizar nome e email.
    """
    service = AuthService(db)
    return service.update_profile(user_id, profile_data)


@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    user_id: int = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Altera senha do usuário autenticado
    
    Requer token JWT válido no header Authorization.
    Requer senha atual para validação.
    """
    service = AuthService(db)
    return service.change_password(user_id, password_data)
