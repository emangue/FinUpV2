"""
Processadores Excel
Arquivos .xls, .xlsx, .xlsm
"""

from .itau_extrato import process_itau_extrato
from .btg_extrato import process_btg_extrato
from .mercadopago_extrato import process_mercadopago_extrato

__all__ = [
    "process_itau_extrato",
    "process_btg_extrato",
    "process_mercadopago_extrato",
]
