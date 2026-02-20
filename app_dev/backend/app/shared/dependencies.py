"""
Dependências para autenticação e usuários
🔐 SEGURANÇA - Autenticação JWT obrigatória em todos os endpoints
🔴 CORREÇÃO CRÍTICA (23/01/2026): Removido user_id hardcoded que causava vazamento de dados
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Session
from fastapi import Header, Depends, HTTPException, status, Request
from app.core.database import get_db
from app.domains.auth.jwt_utils import extract_user_id_from_token

if TYPE_CHECKING:
    from app.domains.users.models import User

def _get_token(authorization: Optional[str], request: Request) -> Optional[str]:
    """Extrai token de Authorization header ou cookie auth_token."""
    auth_val = authorization if isinstance(authorization, str) else None
    if auth_val and auth_val.startswith("Bearer "):
        return auth_val.replace("Bearer ", "")
    cookie = request.cookies.get("auth_token")
    return cookie

def get_current_user_id(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> int:
    """
    🔒 FUNÇÃO PRINCIPAL DE AUTENTICAÇÃO
    
    Retorna o ID do usuário autenticado via JWT (obrigatório)
    
    Esta função REQUER autenticação válida.
    Se o token não for fornecido ou for inválido, levanta exceção 401.
    
    ⚠️ NUNCA retorna user_id fixo ou fallback - isso causaria vazamento de dados!
    
    Args:
        authorization: Header "Authorization: Bearer <token>" (obrigatório)
        
    Returns:
        user_id extraído do token JWT (ex: 1, 2, 3, ...)
        
    Raises:
        HTTPException 401: Se token não fornecido, inválido ou expirado
        
    Examples:
        # ✅ COM token válido
        Authorization: Bearer eyJ... → user_id do token (ex: 2 para teste@email.com)
        
        # ❌ SEM token
        (sem header) → HTTPException 401
        
        # ❌ Token inválido/expirado
        Authorization: Bearer invalid → HTTPException 401
    
    Correção (23/01/2026):
        ANTES: Função retornava user_id=1 hardcoded (INSEGURO!)
        DEPOIS: Sempre extrai user_id do JWT (SEGURO)
    """
    token = _get_token(authorization, request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair e validar user_id do token JWT
    try:
        user_id = extract_user_id_from_token(token)
        
        if not user_id:
            raise ValueError("Token válido mas sem user_id")
        
        return user_id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# 🗑️ FUNÇÕES REMOVIDAS - VULNERABILIDADES DE SEGURANÇA
# ============================================================================
# 
# ❌ REMOVIDA: get_current_user_id() que retornava `return 1` hardcoded
#    Problema: Todos os usuários viam dados do user_id=1 (admin)
#    Correção: Substituída pela função acima que extrai user_id do JWT
# 
# ❌ REMOVIDA: get_current_user_id_optional() com fallback para user_id=1
#    Problema: Permitia acesso sem autenticação
#    Correção: Agora TODOS os endpoints exigem JWT válido (erro 401 se ausente)
# 
# ❌ REMOVIDA: Alias `get_current_user_id = get_current_user_from_jwt`
#    Problema: Imports aconteciam antes do alias, pegando função antiga
#    Correção: Função única `get_current_user_id()` definida corretamente
# 
# 🔒 REGRA: NUNCA mais criar funções com user_id hardcoded ou fallback!
# 
# ============================================================================

def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> "User":
    """
    🔒 Retorna o usuário autenticado completo (modelo User)
    
    Usa get_current_user_id para extrair user_id do JWT (header ou cookie),
    então busca o User completo no banco.
    
    Returns:
        User: Modelo completo do usuário autenticado
        
    Raises:
        HTTPException 401: Se token inválido
        HTTPException 404: Se usuário não encontrado no banco
    """
    # Import aqui para evitar circular import
    from app.domains.users.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuário ID {user_id} não encontrado"
        )
    
    return user


def require_admin(
    current_user: "User" = Depends(get_current_user)
) -> "User":
    """
    🔐 PROTEÇÃO ADMIN - Valida que usuário é administrador
    
    Similar ao get_current_user, mas TAMBÉM verifica se role='admin'.
    Use esta dependency em endpoints que só admins devem acessar.
    
    Returns:
        User: Modelo do usuário admin autenticado
        
    Raises:
        HTTPException 401: Se token inválido
        HTTPException 403: Se usuário não é admin
        HTTPException 404: Se usuário não encontrado
    """
    user = current_user
    
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem executar esta ação."
        )
    
    return user
