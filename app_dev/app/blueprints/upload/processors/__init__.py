"""
Pacote processors - Apenas processadores genéricos
"""
from .fatura_cartao import processar_fatura_cartao
from .extrato_conta import processar_extrato_conta

__all__ = [
    'processar_fatura_cartao',
    'processar_extrato_conta'
]
