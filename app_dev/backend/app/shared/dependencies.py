"""
Dependências de autenticação e validação
Lê JWT do cookie e valida usuário
"""
from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, TYPE_CHECKING
from app.core.database import get_db
from app.shared.auth import decode_token

if TYPE_CHECKING:
    from app.domains.users.models import User

def get_current_user_id(
    access_token: Optional[str] = Cookie(None, alias="access_token")
) -> int:
    """
    Extrai e valida user_id do JWT cookie
    
    IMPORTANTE: Esta função agora valida autenticação REAL via JWT
    - Lê cookie 'access_token' do browser
    - Valida assinatura JWT
    - Retorna user_id se válido
    - Lança 401 Unauthorized se inválido/ausente
    
    Args:
        access_token: Cookie JWT automático do browser
        
    Returns:
        user_id validado
        
    Raises:
        HTTPException 401: Se token ausente, inválido ou expirado
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Token ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = decode_token(access_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retorna usuário completo autenticado
    
    Dependency chain: Cookie → JWT validation → Database query
    
    Args:
        user_id: Extraído do JWT pelo get_current_user_id
        db: Sessão do banco
        
    Returns:
        Objeto User completo
        
    Raises:
        HTTPException 404: Se usuário não encontrado
    """
    from app.domains.users.models import User  # Import local para evitar circular
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if user.ativo != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )
    
    return user

