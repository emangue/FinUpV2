"""
Utilitários de Autenticação JWT
Funções para criar e validar tokens JWT
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

def create_access_token(user_id: int) -> tuple[str, datetime]:
    """
    Cria access token JWT de curta duração
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Tupla (token_string, expiration_datetime)
    """
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt, expire


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """
    Cria refresh token JWT de longa duração
    
    Args:
        user_id: ID do usuário
        
    Returns:
        Tupla (token_string, expiration_datetime)
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt, expire


def decode_token(token: str) -> Optional[int]:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT string
        
    Returns:
        user_id se token válido, None se inválido/expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
        return int(user_id)
        
    except JWTError:
        return None
    except ValueError:
        return None
