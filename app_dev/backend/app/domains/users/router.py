"""
Domínio Users - Router
Endpoints HTTP - autenticação e gestão de usuários
"""
from fastapi import APIRouter, Depends, Query, Response, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.config import settings
from app.shared.dependencies import get_current_user_id, get_current_user
from app.shared.auth import create_access_token, create_refresh_token, decode_token
from .service import UserService, verify_password, hash_password
from .models import User, RefreshToken
from .schemas import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserListResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest
)

# Configura rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["users"])


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
def login(
    request: Request,  # IMPORTANTE: Request necessário para rate limiting
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Endpoint de login com JWT e rate limiting
    
    Rate Limit: 5 requisições por minuto por IP (proteção brute force)
    
    Fluxo:
    1. Valida email + senha
    2. Gera access_token (15min) + refresh_token (7 dias)
    3. Salva tokens em httpOnly cookies
    4. Retorna tokens no body também (compatibilidade)
    
    Segurança:
    - httpOnly cookie = protege contra XSS
    - Secure cookie = HTTPS apenas em produção (⚠️ MEGA IMPORTANTE)
    - SameSite=Lax = protege contra CSRF
    - Rate limiting = 5 req/min por IPmpatibilidade)
    
    Segurança:
    - httpOnly cookie = protege contra XSS
    - Secure cookie = apenas HTTPS (produção)
    - SameSite=Lax = protege contra CSRF
    """
    # Buscar usuário por email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verificar senha
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verificar se usuário está ativo
    if user.ativo != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado. Contate o administrador."
        )
    
    # Gerar tokens
    access_token, access_expire = create_access_token(user.id)
    refresh_token, refresh_expire = create_refresh_token(user.id)
    
    # Salvar refresh token no banco (para validação futura)
    refresh_token_hash = hash_password(refresh_token)  # Hash do refresh token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=refresh_expire
    )
    db.add(db_refresh_token)
    db.commit()
    
    # ⚠️ MEGA IMPORTANTE: Em produção (HTTPS), secure=True obrigatório!
    is_production = settings.ENVIRONMENT == "production"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # JavaScript não pode acessar
        secure=is_production,  # HTTPS obrigatório em prod (⚠️ importante!)
        samesite="lax",  # Proteção CSRF
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # segundos
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,  # HTTPS obrigatório em prod (⚠️ importante!)
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # segundos
    )
    
    # Retornar tokens no body também (compatibilidade)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/auth/logout")
def logout(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Endpoint de logout
    
    Fluxo:
    1. Invalida refresh tokens do usuário no banco
    2. Limpa cookies do browser
    
    Nota: Access token continua válido até expirar (15min)
    mas sem refresh token, usuário precisa fazer login novamente
    """
    # Revogar todos os refresh tokens do usuário
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == 0
    ).update({"revoked": 1})
    db.commit()
    
    # Limpar cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return {"message": "Logout realizado com sucesso"}


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_info(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna informações do usuário autenticado
    
    Usado pelo frontend para:
    1. Verificar se sessão é válida
    2. Obter dados do usuário logado
    3. Middleware de autenticação
    """
    try:
        # Garantir que o objeto user está completo
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )
        return user
    except Exception as e:
        # Log do erro para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in /auth/me: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar dados do usuário: {str(e)}"
        )


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_access_token(
    response: Response,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renova access token usando refresh token
    
    Fluxo:
    1. Valida refresh token
    2. Verifica se não foi revogado
    3. Gera novo access token
    4. Mantém mesmo refresh token
    """
    # Decodificar refresh token
    user_id = decode_token(refresh_data.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    
    # Buscar refresh token no banco
    token_hash = hash_password(refresh_data.refresh_token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == 0
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não encontrado ou revogado"
        )
    
    # Gerar novo access token
    access_token, access_expire = create_access_token(user_id)
    
    # Atualizar cookie
    is_production = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,  # Mesmo refresh token
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ======================================
# Endpoints de Gestão de Usuários
# ======================================

@router.get("/users/", response_model=UserListResponse)
def list_users(
    apenas_ativos: bool = Query(True, description="Listar apenas usuários ativos"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os usuários
    """
    service = UserService(db)
    return service.list_users(apenas_ativos)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca usuário por ID
    """
    service = UserService(db)
    return service.get_user(user_id)

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Cria novo usuário
    """
    service = UserService(db)
    return service.create_user(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza usuário
    """
    service = UserService(db)
    return service.update_user(user_id, update_data)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Desativa usuário (soft delete)
    """
    service = UserService(db)
    return service.delete_user(user_id)

@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    nova_senha: str,
    db: Session = Depends(get_db)
):
    """
    Reseta a senha de um usuário
    """
    service = UserService(db)
    return service.reset_password(user_id, nova_senha)
