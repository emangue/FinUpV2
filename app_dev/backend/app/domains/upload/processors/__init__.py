"""
Upload Processors Package
Processamento em fases de arquivos financeiros
"""

from .raw import RawTransaction, get_processor
from .marker import TransactionMarker, MarkedTransaction
from .classifier import CascadeClassifier, ClassifiedTransaction

__all__ = [
    "RawTransaction",
    "get_processor",
    "TransactionMarker",
    "MarkedTransaction",
    "CascadeClassifier",
    "ClassifiedTransaction",
]
