"""
Router do domínio Auth.
Endpoints FastAPI isolados aqui.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.config import settings
from .service import AuthService
from .jwt_utils import extract_user_id_from_token
from .schemas import LoginRequest, TokenResponse, UserLoginResponse, LogoutRequest, ProfileUpdateRequest, PasswordChangeRequest


router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login")
@limiter.limit("5/minute")  # Máximo 5 tentativas de login por minuto
def login(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna token JWT.
    Define cookie httpOnly para maior segurança (não acessível via JS).
    """
    service = AuthService(db)
    token_response = service.login(credentials)
    data = {
        "access_token": token_response.access_token,
        "token_type": token_response.token_type,
        "user": token_response.user.model_dump(),
    }
    response = JSONResponse(content=data)
    # Cookie httpOnly: não acessível via JS (proteção XSS)
    response.set_cookie(
        key="auth_token",
        value=token_response.access_token,
        max_age=3600,
        path="/",
        secure=not settings.DEBUG,  # Secure em produção (HTTPS)
        httponly=True,
        samesite="strict",
    )
    return response


def _get_token_from_request(request: Request, authorization: Optional[str]) -> Optional[str]:
    """Extrai token de Authorization ou cookie auth_token."""
    if authorization and authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "")
    return request.cookies.get("auth_token")


@router.get("/me", response_model=UserLoginResponse)
def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Retorna dados do usuário autenticado.
    Aceita token em Authorization header ou cookie auth_token.
    """
    token = _get_token_from_request(request, authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação não fornecido")
    
    user_id = extract_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Token válido mas sem user_id")
    
    service = AuthService(db)
    return service.get_current_user(user_id)


@router.post("/logout", status_code=204)
def logout(
    data: LogoutRequest = None,
    db: Session = Depends(get_db)
):
    """
    Logout do usuário. Remove cookie auth_token.
    """
    response = JSONResponse(content={}, status_code=204)
    response.delete_cookie(key="auth_token", path="/")
    return response


def get_user_id_from_token(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> int:
    """
    Extrai user_id do token JWT (header Authorization ou cookie auth_token).
    """
    token = _get_token_from_request(request, authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
