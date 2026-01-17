"""
Registry de processadores raw
Mapeia (banco, tipo, formato) → função processadora
"""

import logging
import unicodedata
from typing import Callable, Optional, Tuple, List
from pathlib import Path
import pandas as pd

from .base import RawTransaction
from .csv.itau_fatura import process_itau_fatura as csv_itau_fatura
from .excel.itau_extrato import process_itau_extrato
from .excel.btg_extrato import process_btg_extrato

logger = logging.getLogger(__name__)

# Tipo para função processadora
ProcessorFunc = Callable[[Path, str, str, str], List[RawTransaction]]

# Registry de processadores (banco, tipo, formato)
PROCESSORS: dict[Tuple[str, str, str], ProcessorFunc] = {
    # Itaú
    ('itau', 'fatura', 'csv'): csv_itau_fatura,
    ('itau', 'extrato', 'excel'): process_itau_extrato,
    # BTG Pactual
    ('btg', 'extrato', 'excel'): process_btg_extrato,
    ('btg pactual', 'extrato', 'excel'): process_btg_extrato,
    ('btg-pactual', 'extrato', 'excel'): process_btg_extrato,  # Variação com hífen
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


def get_processor(banco: str, tipo_documento: str, formato: str = None) -> Optional[ProcessorFunc]:
    """
    Retorna o processador adequado para banco, tipo e formato
    
    Args:
        banco: Nome do banco (ex: "Itaú", "BTG Pactual")
        tipo_documento: 'fatura' ou 'extrato'
        formato: 'csv', 'excel', 'pdf', 'ofx' (detectado automaticamente se None)
        
    Returns:
        Função processadora ou None se não encontrado
    """
    # Normalizar entrada
    banco_norm = _normalize_bank_name(banco)
    tipo_norm = tipo_documento.lower()
    formato_norm = formato.lower() if formato else None
    
    # Tentar com formato especificado
    if formato_norm:
        key = (banco_norm, tipo_norm, formato_norm)
        processor = PROCESSORS.get(key)
        
        if processor:
            logger.info(f"✅ Processador encontrado: {banco_norm}/{tipo_norm}/{formato_norm}")
            return processor
    
    # Fallback: buscar qualquer formato (retrocompatibilidade)
    for (b, t, f), proc in PROCESSORS.items():
        if b == banco_norm and t == tipo_norm:
            logger.info(f"✅ Processador encontrado (fallback): {b}/{t}/{f}")
            return proc
    
    logger.warning(f"⚠️ Processador não encontrado: {banco_norm}/{tipo_norm}/{formato_norm or 'auto'}")
    logger.info(f"📋 Processadores disponíveis: {list(PROCESSORS.keys())}")
    
    return None
