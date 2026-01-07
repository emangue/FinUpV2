"""
Shared Utils Package
Utilitários compartilhados entre domínios
"""

from .hasher import fnv1a_64_hash, generate_id_simples
from .normalizer import (
    normalizar_estabelecimento,
    detectar_parcela,
    arredondar_2_decimais,
    get_faixa_valor,
    normalizar
)

__all__ = [
    "fnv1a_64_hash",
    "generate_id_simples",
    "normalizar_estabelecimento",
    "detectar_parcela",
    "arredondar_2_decimais",
    "get_faixa_valor",
    "normalizar",
]
