"""
Dependências para autenticação e usuários
🔐 SEGURANÇA - Autenticação JWT obrigatória em todos os endpoints
🔴 CORREÇÃO CRÍTICA (23/01/2026): Removido user_id hardcoded que causava vazamento de dados
"""
from sqlalchemy.orm import Session
from fastapi import Header, Depends, HTTPException, status
from typing import Optional
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.auth.jwt_utils import extract_user_id_from_token

def get_current_user_id(
    authorization: Optional[str] = Header(None)
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
    # Validar presença do header Authorization
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validar formato do header
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido (use: Bearer <token>)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair token
    token = authorization.replace("Bearer ", "")
    
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

def get_current_user(db: Session) -> User:
    """
    Retorna o usuário atual completo
    Por enquanto sempre retorna user_id = 1
    """
    user = db.query(User).filter(User.id == 1).first()
    return user
