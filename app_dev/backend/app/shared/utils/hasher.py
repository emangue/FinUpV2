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


def generate_id_transacao(data, estabelecimento, valor):
    """
    Gera IdTransacao consistente usando hash FNV-1a
    
    Args:
        data (str): Data no formato DD/MM/AAAA
        estabelecimento (str): Nome do estabelecimento
        valor (float): Valor da transação
        
    Returns:
        str: IdTransacao (hash FNV-1a 64-bit)
    """
    # Normaliza estabelecimento (remove acentos, caracteres especiais)
    # Nota: normalizar deve ser importado de normalizer.py
    from app.shared.utils.normalizer import normalizar
    
    estab_norm = normalizar(estabelecimento)
    valor_str = f"{float(valor):.2f}"
    
    # Chave: Data|EstabelecimentoNormalizado|Valor
    chave = f"{data}|{estab_norm}|{valor_str}"
    
    return fnv1a_64_hash(chave)


def generate_id_transacao(data, estabelecimento, valor, timestamp_micro=None):
    """
    Gera IdTransacao consistente usando hash FNV-1a
    
    Args:
        data (str): Data no formato DD/MM/AAAA
        estabelecimento (str): Nome do estabelecimento
        valor (float): Valor da transação
        timestamp_micro (str, optional): Timestamp em microsegundos para diferenciar duplicatas
        
    Returns:
        str: IdTransacao (hash FNV-1a 64-bit)
    """
    # Normaliza estabelecimento (remove acentos, caracteres especiais)
    from app.shared.utils.normalizer import normalizar
    
    estab_norm = normalizar(estabelecimento)
    valor_str = f"{float(valor):.2f}"
    
    # Chave: Data|EstabelecimentoNormalizado|Valor[|Timestamp]
    chave = f"{data}|{estab_norm}|{valor_str}"
    
    # Se fornecido timestamp, adiciona para garantir unicidade
    if timestamp_micro:
        chave += f"|{timestamp_micro}"
    
    return fnv1a_64_hash(chave)


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
