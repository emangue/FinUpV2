"""
Registry de processadores raw
Mapeia (banco, tipo) → função processadora
"""

import logging
from typing import Callable, Optional, Tuple, List
from pathlib import Path
import pandas as pd

from .base import RawTransaction
from .itau_fatura import process_itau_fatura
from .itau_extrato import process_itau_extrato
from .btg_extrato import process_btg_extrato

logger = logging.getLogger(__name__)

# Tipo para função processadora
ProcessorFunc = Callable[[Path, str, str, str], List[RawTransaction]]

# Registry de processadores
PROCESSORS: dict[Tuple[str, str], ProcessorFunc] = {
    ('itau', 'fatura'): process_itau_fatura,
    ('itau', 'extrato'): process_itau_extrato,
    ('btg', 'extrato'): process_btg_extrato,
}


def get_processor(banco: str, tipo_documento: str) -> Optional[ProcessorFunc]:
    """
    Retorna o processador adequado para banco e tipo
    
    Args:
        banco: Nome do banco em lowercase
        tipo_documento: 'fatura' ou 'extrato'
        
    Returns:
        Função processadora ou None se não encontrado
    """
    key = (banco.lower(), tipo_documento.lower())
    processor = PROCESSORS.get(key)
    
    if processor:
        logger.info(f"Processador encontrado: {banco}/{tipo_documento}")
    else:
        logger.warning(f"Processador não encontrado para: {banco}/{tipo_documento}")
        logger.info(f"Processadores disponíveis: {list(PROCESSORS.keys())}")
    
    return processor
