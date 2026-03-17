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
from .excel.mercadopago_extrato import process_mercadopago_extrato
from .pdf.itau_extrato_pdf import process_itau_extrato_pdf
from .pdf.itau_fatura_pdf import process_itau_fatura_pdf
from .pdf.mercadopago_extrato_pdf import process_mercadopago_extrato_pdf
from .pdf.btg_fatura_pdf import process_btg_fatura_pdf
from .pdf.btg_extrato_pdf import process_btg_extrato_pdf
from .excel.btg_fatura_xlsx import process_btg_fatura_xlsx
from .pdf.mercadopago_fatura_pdf import process_mercadopago_fatura_pdf

logger = logging.getLogger(__name__)

# Tipo para função processadora
ProcessorFunc = Callable[[Path, str, str, str], List[RawTransaction]]

# Wrappers para processadores PDF que retornam Tuple[List, BalanceValidation]
# Precisam ser convertidos para retornar apenas List[RawTransaction]
def _wrap_extrato_pdf(processor_func):
    """Wrapper para extratos PDF que retornam (transactions, balance)"""
    def wrapper(file_path: Path, nome_arquivo: str, nome_cartao: str = None, final_cartao: str = None):
        transactions, balance = processor_func(file_path, nome_arquivo, nome_cartao, final_cartao)
        logger.info(f"📊 Validação de saldo: {balance.is_valid} (diferença: R$ {balance.diferenca:.2f})")
        return transactions
    return wrapper

# Registry de processadores (banco, tipo, formato)
PROCESSORS: dict[Tuple[str, str, str], ProcessorFunc] = {
    # Itaú
    ('itau', 'fatura', 'csv'): csv_itau_fatura,
    ('itau', 'extrato', 'excel'): process_itau_extrato,
    ('itau', 'extrato', 'pdf'): _wrap_extrato_pdf(process_itau_extrato_pdf),
    ('itau', 'fatura', 'pdf'): process_itau_fatura_pdf,
    # BTG Pactual - Extrato XLS
    ('btg', 'extrato', 'excel'): process_btg_extrato,
    ('btg pactual', 'extrato', 'excel'): process_btg_extrato,
    ('btg-pactual', 'extrato', 'excel'): process_btg_extrato,  # Variação com hífen
    # BTG Pactual - Extrato PDF
    ('btg', 'extrato', 'pdf'): process_btg_extrato_pdf,
    ('btg pactual', 'extrato', 'pdf'): process_btg_extrato_pdf,
    ('btg-pactual', 'extrato', 'pdf'): process_btg_extrato_pdf,
    # BTG Pactual - Fatura
    ('btg', 'fatura', 'excel'): process_btg_fatura_xlsx,
    ('btg pactual', 'fatura', 'excel'): process_btg_fatura_xlsx,
    ('btg', 'fatura', 'pdf'): process_btg_fatura_pdf,
    ('btg pactual', 'fatura', 'pdf'): process_btg_fatura_pdf,
    # Mercado Pago
    ('mercado pago', 'extrato', 'excel'): process_mercadopago_extrato,
    ('mercadopago', 'extrato', 'excel'): process_mercadopago_extrato,  # Variação sem espaço
    ('mercado pago', 'extrato', 'pdf'): _wrap_extrato_pdf(process_mercadopago_extrato_pdf),
    ('mercadopago', 'extrato', 'pdf'): _wrap_extrato_pdf(process_mercadopago_extrato_pdf),
    # Mercado Pago - Fatura
    ('mercado pago', 'fatura', 'pdf'): process_mercadopago_fatura_pdf,
    ('mercadopago', 'fatura', 'pdf'): process_mercadopago_fatura_pdf,
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
