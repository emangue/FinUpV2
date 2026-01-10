"""
Processador bruto para Extrato BTG XLS
Adaptado de codigos_apoio/extrato_btg_xls.py
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List
import pandas as pd

from .base import RawTransaction

logger = logging.getLogger(__name__)


def process_btg_extrato(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> List[RawTransaction]:
    """
    Processa extrato BTG XLS
    
    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Lista de RawTransaction
    """
    logger.info(f"Processando extrato BTG: {nome_arquivo}")
    
    try:
        # Ler XLS
        df_raw = pd.read_excel(file_path)
        logger.debug(f"XLS lido: {len(df_raw)} linhas")
        
        # Preprocessar
        df_processed = _preprocess_extrato_btg(df_raw)
        logger.info(f"Extrato preprocessado: {len(df_processed)} transações")
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for _, row in df_processed.iterrows():
            transaction = RawTransaction(
                banco='BTG Pactual',
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
        
        logger.info(f"✅ Extrato BTG processado: {len(transactions)} transações")
        return transactions
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato BTG: {str(e)}", exc_info=True)
        raise


def _preprocess_extrato_btg(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessa DataFrame bruto do extrato BTG XLS
    Lógica simplificada de extrato_btg_xls.preprocessar_extrato_btg()
    """
    # Detectar linha do cabeçalho (linha 9 geralmente, começando coluna B)
    header_row = None
    for i in range(min(15, len(df_raw))):
        row_str = ' '.join(str(val).lower() for val in df_raw.iloc[i].values if pd.notna(val))
        if 'data' in row_str and 'categoria' in row_str and 'valor' in row_str:
            header_row = i
            break
    
    if header_row is None:
        raise ValueError(
            "Este arquivo não parece ser um extrato do BTG Pactual no formato XLS esperado. "
            "Verifique se o arquivo contém as colunas: data, categoria, descrição, valor (geralmente a partir da linha 9)."
        )
    
    # Extrair dados a partir do cabeçalho (linha 10+, coluna B em diante)
    df = df_raw.iloc[header_row + 1:, 1:].copy()
    headers = df_raw.iloc[header_row, 1:].values
    df.columns = headers
    df = df.reset_index(drop=True)
    
    # Normalizar nomes de colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Identificar coluna "Descrição" (contém "Saldo Diário")
    desc_col = None
    for col in df.columns:
        col_str = str(col).lower()
        if 'descri' in col_str or 'transação' in col_str or 'transacao' in col_str:
            desc_col = col
            break
    
    if desc_col is None:
        raise ValueError(
            "Estrutura do arquivo BTG Pactual inválida: coluna 'Descrição' não encontrada. "
            "Verifique se o arquivo é um extrato válido do BTG."
        )
    
    # Mapear colunas
    col_map = {}
    for col in df.columns:
        col_str = str(col).lower()
        if 'data' in col_str:
            col_map[col] = 'data'
        elif 'categoria' in col_str:
            col_map[col] = 'categoria'
        elif 'valor' in col_str:
            col_map[col] = 'valor (R$)'
    
    col_map[desc_col] = 'descricao'
    df = df.rename(columns=col_map)
    
    # Filtrar linhas de "Saldo Diário" ANTES de criar lançamento
    mask_saldo_diario = df['descricao'].astype(str).str.contains('Saldo Diário', case=False, na=False)
    df = df[~mask_saldo_diario]
    
    # Criar coluna "lançamento" combinando categoria e descrição
    df['lançamento'] = df['categoria'].fillna('').astype(str) + ' - ' + df['descricao'].fillna('').astype(str)
    
    # Selecionar colunas necessárias
    df = df[['data', 'lançamento', 'valor (R$)']].copy()
    
    # Limpar dados - remover linhas vazias ou inválidas
    df = df[df['data'].notna()]
    df = df[df['valor (R$)'].notna()]
    df = df[~df['lançamento'].str.strip().isin(['', ' - ', 'nan - nan'])]
    
    # Converter valor para float
    df['valor (R$)'] = df['valor (R$)'].apply(_convert_valor_br)
    
    # Remover valores zero
    df = df[df['valor (R$)'] != 0]
    
    # Converter data para DD/MM/YYYY
    df['data'] = pd.to_datetime(df['data'], errors='coerce').dt.strftime('%d/%m/%Y')
    df = df.dropna(subset=['data'])
    
    return df.reset_index(drop=True)


def _convert_valor_br(valor) -> float:
    """Converte valor brasileiro para float"""
    if pd.isna(valor):
        return 0.0
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    valor_str = str(valor).strip()
    valor_str = valor_str.replace('.', '').replace(',', '.')
    
    try:
        return float(valor_str)
    except ValueError:
        return 0.0
