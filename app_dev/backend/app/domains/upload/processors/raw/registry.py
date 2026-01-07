"""
Registry de processadores raw
Mapeia (banco, tipo) → função processadora
"""

import logging
import unicodedata
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
    ('btg pactual', 'extrato'): process_btg_extrato,
}


def _normalize_bank_name(banco: str) -> str:
    """
    Normaliza nome do banco: lowercase + remove acentos
    
    Args:
        banco: Nome do banco original (ex: "Itaú", "BTG Pactual")
        
    Returns:
        Nome normalizado (ex: "itau", "btg pactual")
    """
    # Lowercase
    banco = banco.lower()
    
    # Remover acentos usando NFD (Normalization Form Decomposed)
    banco_nfd = unicodedata.normalize('NFD', banco)
    banco_sem_acento = ''.join(
        char for char in banco_nfd 
        if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing Mark (acentos)
    )
    
    return banco_sem_acento


def get_processor(banco: str, tipo_documento: str) -> Optional[ProcessorFunc]:
    """
    Retorna o processador adequado para banco e tipo
    
    Args:
        banco: Nome do banco (ex: "Itaú", "BTG Pactual")
        tipo_documento: 'fatura' ou 'extrato'
        
    Returns:
        Função processadora ou None se não encontrado
    """
    # Normalizar entrada
    banco_norm = _normalize_bank_name(banco)
    tipo_norm = tipo_documento.lower()
    
    key = (banco_norm, tipo_norm)
    processor = PROCESSORS.get(key)
    
    if processor:
        logger.info(f"✅ Processador encontrado: {banco_norm}/{tipo_norm}")
    else:
        logger.warning(f"⚠️ Processador não encontrado: {banco_norm}/{tipo_norm}")
        logger.info(f"📋 Processadores disponíveis: {list(PROCESSORS.keys())}")
    
    return processor
