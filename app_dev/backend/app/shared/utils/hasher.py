"""
Utilitários para hash FNV-1a 64-bit

Versão: 2.1.0
Data: 27/12/2025
Status: stable

🔒 ARQUIVO CRÍTICO - Requer versionamento obrigatório

Implementa geração de hashes FNV-1a 64-bit para criação de IDs únicos.
Mudanças neste arquivo afetam a integridade dos dados e identificação
de transações duplicadas.

Histórico:
- 2.0.0: Migração de MD5 para FNV-1a 64-bit (correção bug colisão VPD)
- 2.1.0: Sistema de versionamento implementado

Fonte: https://github.com/emangue/FinUp/tree/main/app/utils/hasher.py
"""


def fnv1a_64_hash(text):
    """
    Gera hash FNV-1a 64-bit de uma string
    
    Args:
        text (str): Texto para gerar hash
        
    Returns:
        str: Hash em decimal (string)
    """
    FNV_OFFSET_64 = 0xcbf29ce484222325
    FNV_PRIME_64 = 0x100000001b3
    MASK64 = (1 << 64) - 1
    
    h = FNV_OFFSET_64
    for char in text:
        h ^= ord(char)
        h = (h * FNV_PRIME_64) & MASK64
    
    return str(h)


def generate_id_transacao(data, estabelecimento, valor, sequencia=None):
    """
    Gera IdTransacao consistente usando hash FNV-1a 64-bit com hash recursivo para duplicados
    
    ESTRATÉGIA v4.1.0 (HASH RECURSIVO):
    - Hash BASE: Data|Estabelecimento|Valor
    - DUPLICADOS: Aplica hash recursivamente N vezes
    - seq=1: hash(chave)
    - seq=2: hash(hash_seq1)
    - seq=3: hash(hash_seq2)
    - seq=N: hash aplicado N-1 vezes recursivamente
    - Garante hashes únicos para QUALQUER quantidade de duplicados
    
    Args:
        data (str): Data no formato DD/MM/AAAA
        estabelecimento (str): Nome do estabelecimento ORIGINAL (com parcelas, etc)
        valor (float): Valor da transação
        sequencia (int, optional): Número da ocorrência (1=primeira, 2=segunda, etc). Default: 1
        
    Returns:
        str: IdTransacao (hash FNV-1a 64-bit em decimal)
        
    Exemplos:
        >>> generate_id_transacao('15/10/2025', 'PIX TRANSF EMANUEL15/10', -1000.00, 1)
        '8119916638940476640'
        
        >>> generate_id_transacao('15/10/2025', 'PIX TRANSF EMANUEL15/10', -1000.00, 2)
        '15234567890123456789'  # hash(hash_anterior)
        
        >>> generate_id_transacao('15/10/2025', 'PIX TRANSF EMANUEL15/10', -1000.00, 10)
        '98765432109876543210'  # hash aplicado 9 vezes
    """
    # Default sequencia = 1
    if sequencia is None:
        sequencia = 1
    
    # UPPERCASE e trim (case-insensitive)
    estab_upper = str(estabelecimento).upper().strip()
    
    # Valor absoluto com 2 casas decimais
    valor_abs = abs(float(valor))
    valor_str = f"{valor_abs:.2f}"
    
    # Chave base: Data|Estabelecimento|Valor
    chave = f"{data}|{estab_upper}|{valor_str}"
    
    # Hash base
    hash_atual = fnv1a_64_hash(chave)
    
    # Aplicar hash recursivo para duplicados (seq > 1)
    # seq=2: 1 iteração (hash do hash)
    # seq=3: 2 iterações (hash do hash do hash)
    # seq=N: N-1 iterações - funciona para QUALQUER N!
    for _ in range(sequencia - 1):
        hash_atual = fnv1a_64_hash(hash_atual)
    
    return hash_atual


def generate_id_simples(data, estabelecimento, valor):
    """
    Gera ID simples (compatível com n8n)
    Inclui estabelecimento normalizado para evitar colisões
    
    Args:
        data (str): Data
        estabelecimento (str): Estabelecimento
        valor (float): Valor
        
    Returns:
        str: Hash simples
    """
    from app.shared.utils.normalizer import normalizar_estabelecimento
    
    # Normaliza estabelecimento para garantir consistência
    estab_norm = normalizar_estabelecimento(estabelecimento)
    
    # Inclui estabelecimento normalizado no hash
    str_concat = f"{data}{estab_norm}{valor:.2f}".replace(' ', '').replace('/', '').replace('-', '')
    
    # Hash simples (compatível com JavaScript)
    hash_val = 0
    for char in str_concat:
        hash_val = ((hash_val << 5) - hash_val) + ord(char)
        hash_val = hash_val & 0xFFFFFFFF  # Convert to 32bit integer
    
    # Retorna em decimal (consistente com journal_entries)
    return str(abs(hash_val))
