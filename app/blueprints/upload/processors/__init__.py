"""
Pacote processors
"""
from .fatura_itau import processar_fatura_itau
from .extrato_itau import processar_extrato_itau
from .mercado_pago import processar_mercado_pago

__all__ = [
    'processar_fatura_itau',
    'processar_extrato_itau',
    'processar_mercado_pago'
]
