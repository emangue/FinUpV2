"""
Upload Processors Package
Processamento em fases de arquivos financeiros
"""

from .raw import RawTransaction, get_processor
from .raw.pdf import (
    process_itau_extrato_pdf,
    process_itau_fatura_pdf,
    process_mercadopago_extrato_pdf,
)
from .marker import TransactionMarker, MarkedTransaction
from .classifier import CascadeClassifier, ClassifiedTransaction

__all__ = [
    "RawTransaction",
    "get_processor",
    "process_itau_extrato_pdf",
    "process_itau_fatura_pdf",
    "process_mercadopago_extrato_pdf",
    "TransactionMarker",
    "MarkedTransaction",
    "CascadeClassifier",
    "ClassifiedTransaction",
]
