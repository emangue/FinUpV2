"""
Processador bruto para Extrato Itaú XLS
Adaptado de codigos_apoio/extrato_itau_xls.py
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List
import pandas as pd

from .base import RawTransaction

logger = logging.getLogger(__name__)


def process_itau_extrato(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> List[RawTransaction]:
    """
    Processa extrato Itaú XLS
    
    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Lista de RawTransaction
    """
    logger.info(f"Processando extrato Itaú: {nome_arquivo}")
    
    try:
        # Ler XLS
        df_raw = pd.read_excel(file_path)
        logger.debug(f"XLS lido: {len(df_raw)} linhas")
        
        # Preprocessar
        df_processed = _preprocess_extrato_itau(df_raw)
        logger.info(f"Extrato preprocessado: {len(df_processed)} transações")
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for _, row in df_processed.iterrows():
            transaction = RawTransaction(
                banco='Itaú',
                tipo_documento='extrato',
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=row['data'],
                lancamento=row['lançamento'],
                valor=row['valor (R$)'],
                nome_cartao=None,
                final_cartao=None,
                mes_fatura=None,
            )
            transactions.append(transaction)
        
        logger.info(f"✅ Extrato Itaú processado: {len(transactions)} transações")
        return transactions
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato Itaú: {str(e)}", exc_info=True)
        raise


def _preprocess_extrato_itau(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessa DataFrame bruto do extrato Itaú XLS
    Lógica simplificada de extrato_itau_xls.preprocessar_extrato_itau_xls()
    """
    # Detectar linha do cabeçalho (linha 8 geralmente)
    header_row = None
    for i in range(min(15, len(df_raw))):
        row_str = ' '.join(str(val).lower() for val in df_raw.iloc[i].values if pd.notna(val))
        if 'data' in row_str and 'lancamento' in row_str and 'valor' in row_str:
            header_row = i
            break
    
    if header_row is None:
        raise ValueError(
            "Este arquivo não parece ser um extrato do Itaú no formato XLS esperado. "
            "Verifique se o arquivo contém as colunas: data, lançamento, valor (geralmente a partir da linha 8)."
        )
    
    # Extrair dados a partir do cabeçalho
    df = df_raw.iloc[header_row:].copy()
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    
    # Normalizar nomes de colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Selecionar apenas colunas necessárias (data, lançamento, valor)
    # XLS Itaú: coluna 0=data, coluna 1=lançamento, coluna 3=valor
    df = df.iloc[:, [0, 1, 3]].copy()
    df.columns = ['data', 'lançamento', 'valor (R$)']
    
    # Limpar dados
    df = df.dropna(subset=['data', 'lançamento', 'valor (R$)'])
    
    # Converter valor para float
    df['valor (R$)'] = pd.to_numeric(df['valor (R$)'], errors='coerce')
    df = df.dropna(subset=['valor (R$)'])
    
    # Remover valores zero
    df = df[df['valor (R$)'] != 0]
    
    # Converter data para DD/MM/YYYY
    df['data'] = pd.to_datetime(df['data'], errors='coerce').dt.strftime('%d/%m/%Y')
    df = df.dropna(subset=['data'])
    
    return df.reset_index(drop=True)
