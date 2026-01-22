"""
Utilitários para hash de senhas com bcrypt.
Segurança de senhas com salt rounds = 12.
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Gera hash bcrypt de uma senha
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash bcrypt da senha
        
    Example:
        >>> hashed = hash_password("senha123")
        >>> print(hashed)
        '$2b$12$...'
    
    Security:
        - Usa bcrypt com 12 salt rounds
        - Cada hash é único (salt automático)
        - Resistente a rainbow tables
        - Custo computacional ajustável
        - Trunca senhas maiores que 72 bytes (limite bcrypt)
    """
    # Bcrypt limita senhas a 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Gerar salt e hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se senha corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash bcrypt armazenado
        
    Returns:
        True se senha correta, False caso contrário
        
    Example:
        >>> hashed = hash_password("senha123")
        >>> verify_password("senha123", hashed)
        True
        >>> verify_password("senha-errada", hashed)
        False
    
    Security:
        - Timing-attack resistant
        - Automaticamente detecta algoritmo do hash
        - Suporta migração de algoritmos antigos
    """
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    hashed_bytes = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def is_bcrypt_hash(password_hash: str) -> bool:
    """
    Verifica se hash é bcrypt (começa com $2b$)
    
    Args:
        password_hash: Hash a verificar
        
    Returns:
        True se é bcrypt, False caso contrário
        
    Example:
        >>> is_bcrypt_hash("$2b$12$...")
        True
        >>> is_bcrypt_hash("5e884898da28...")  # SHA256
        False
    
    Note:
        Útil para scripts de migração SHA256 → bcrypt
    """
    return password_hash.startswith("$2b$") or password_hash.startswith("$2a$")
