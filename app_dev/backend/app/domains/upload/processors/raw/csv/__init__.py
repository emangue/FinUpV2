"""
Processadores CSV
Arquivos de texto delimitados por vírgula
"""

from .itau_fatura import process_itau_fatura

__all__ = [
    "process_itau_fatura",
]
