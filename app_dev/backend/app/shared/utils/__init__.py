"""
Shared Utils Package
Utilitários compartilhados entre domínios
"""

from .hasher import fnv1a_64_hash, generate_id_simples, generate_id_transacao
from .normalizer import (
    normalizar_estabelecimento,
    detectar_parcela,
    arredondar_2_decimais,
    get_faixa_valor,
    normalizar,
    tokensValidos,
    intersecaoCount,
    toNumberFlexible
)

__all__ = [
    "fnv1a_64_hash",
    "generate_id_simples",
    "generate_id_transacao",
    "normalizar_estabelecimento",
    "detectar_parcela",
    "arredondar_2_decimais",
    "get_faixa_valor",
    "normalizar",
    "tokensValidos",
    "intersecaoCount", 
    "toNumberFlexible",
]
