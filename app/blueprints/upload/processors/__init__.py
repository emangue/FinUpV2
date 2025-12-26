"""
Pacote processors
"""
from .fatura_itau import processar_fatura_itau
from .extrato_itau import processar_extrato_itau
from .mercado_pago import processar_mercado_pago
from .fatura_cartao import processar_fatura_cartao
from .extrato_conta import processar_extrato_conta

__all__ = [
    'processar_fatura_itau',
    'processar_extrato_itau',
    'processar_mercado_pago',
    'processar_fatura_cartao',
    'processar_extrato_conta'
]
