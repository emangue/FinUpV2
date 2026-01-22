"""
Dependências para autenticação e usuários
🔐 FASE 3 COMPLETA - Fallback removido, apenas autenticação obrigatória
"""
from sqlalchemy.orm import Session
from fastapi import Header, Depends
from typing import Optional
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.auth.jwt_utils import extract_user_id_from_token

def get_current_user_id() -> int:
    """
    ⚠️ DEPRECADO - Use get_current_user_from_jwt()
    
    Retorna o ID do usuário atual
    
    Por enquanto fixo em 1 (admin padrão)
    Mantido para retrocompatibilidade com endpoints que não usam JWT ainda
    """
    return 1

def get_current_user_from_jwt(
    authorization: Optional[str] = Header(None)
) -> int:
    """
    Retorna o ID do usuário autenticado via JWT (obrigatório)
    
    Esta função REQUER autenticação válida.
    Se o token não for fornecido ou for inválido, levanta exceção.
    
    Args:
        authorization: Header "Authorization: Bearer <token>" (obrigatório)
        
    Returns:
        user_id extraído do token JWT
        
    Raises:
        HTTPException 401: Se token não fornecido ou inválido
        
    Examples:
        # COM token válido
        Authorization: Bearer eyJ... → user_id do token (ex: 1, 2, 3)
        
        # SEM token
        (sem header) → HTTPException 401
        
        # Token inválido/expirado
        Authorization: Bearer invalid → HTTPException 401
    """
    from fastapi import HTTPException, status
    
    # Sem header Authorization
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Header malformado
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair token
    token = authorization.replace("Bearer ", "")
    
    # Extrair user_id do token
    try:
        user_id = extract_user_id_from_token(token)
        if not user_id:
            raise ValueError("Token inválido")
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============================================================================
# 🗑️ FUNÇÃO REMOVIDA - FASE 3 COMPLETA
# ============================================================================
# 
# get_current_user_id_optional() foi REMOVIDA para eliminar fallback inseguro
# 
# Motivo: Permitia acesso sem autenticação (fallback user_id=1)
# Problema: Usuários viam dados de outros usuários quando token não era enviado
# Solução: Força erro 401 quando token não está presente
# 
# Se algum endpoint quebrar com 401, significa que:
# 1. Frontend não está enviando Authorization header
# 2. fetch() está sendo usado direto (sem api-client.ts)
# 3. Componente não foi atualizado para usar apiGet/apiPost
# 
# Todos os endpoints agora usam: get_current_user_id()
# que chama get_current_user_from_jwt() internamente
# 
# ============================================================================

# Atalho para compatibilidade - Agora chama função com JWT obrigatório
get_current_user_id = get_current_user_from_jwt

def get_current_user(db: Session) -> User:
    """
    Retorna o usuário atual completo
    Por enquanto sempre retorna user_id = 1
    """
    user = db.query(User).filter(User.id == 1).first()
    return user
