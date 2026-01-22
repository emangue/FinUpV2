"""
Utilitários para JWT (JSON Web Tokens).
Criação, validação e decodificação de tokens.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria token JWT com dados do usuário
    
    Args:
        data: Dados a incluir no token (user_id, email, role)
        expires_delta: Tempo de expiração customizado (opcional)
        
    Returns:
        Token JWT codificado como string
        
    Example:
        >>> token = create_access_token({"user_id": 1, "email": "admin@example.com"})
        >>> print(token)
        'eyJ0eXAiOiJKV1QiLCJhbGc...'
    """
    to_encode = data.copy()
    
    # Define expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona campos padrão JWT
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Codifica o token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_jwt(token: str) -> Dict:
    """
    Decodifica e valida token JWT
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Dict com dados do token (user_id, email, role, exp, iat)
        
    Raises:
        JWTError: Se token for inválido ou expirado
        
    Example:
        >>> payload = decode_jwt(token)
        >>> print(payload["user_id"])
        1
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    
    except JWTError as e:
        raise JWTError(f"Token inválido ou expirado: {str(e)}")


def verify_token(token: str) -> bool:
    """
    Verifica se token é válido (não expirou e assinatura correta)
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        True se válido, False caso contrário
        
    Example:
        >>> is_valid = verify_token(token)
        >>> if is_valid:
        ...     print("Token válido!")
    """
    try:
        decode_jwt(token)
        return True
    except JWTError:
        return False


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrai user_id do token JWT
    
    Args:
        token: Token JWT
        
    Returns:
        user_id se token válido, None caso contrário
        
    Example:
        >>> user_id = extract_user_id_from_token(token)
        >>> print(user_id)
        1
    """
    try:
        payload = decode_jwt(token)
        return payload.get("user_id")
    except JWTError:
        return None
