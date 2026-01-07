"""
Raw Processors Package
Processadores brutos por banco/tipo
"""

from .base import RawTransaction
from .registry import get_processor

__all__ = [
    "RawTransaction",
    "get_processor",
]
