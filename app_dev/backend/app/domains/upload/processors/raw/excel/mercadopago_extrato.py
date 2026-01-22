"""
Processador bruto para Extrato Mercado Pago XLSX
Estrutura: XLSX com cabeçalho em linha 3, transações a partir da linha 4
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import pandas as pd

from ..base import RawTransaction, BalanceValidation

logger = logging.getLogger(__name__)


def process_mercadopago_extrato(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa extrato Mercado Pago XLSX
    
    Estrutura do arquivo:
    - Linha 0: Headers (INITIAL_BALANCE, CREDITS, DEBITS, FINAL_BALANCE)
    - Linha 1: Valores dos totais (saldo inicial, créditos totais, débitos totais, saldo final)
    - Linha 2: Em branco
    - Linha 3: Headers das transações (RELEASE_DATE, TRANSACTION_TYPE, REFERENCE_ID, TRANSACTION_NET_AMOUNT, PARTIAL_BALANCE)
    - Linha 4+: Transações (data, tipo, ID, valor líquido, saldo parcial)
    
    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Tupla (Lista de RawTransaction, BalanceValidation)
    """
    logger.info(f"Processando extrato Mercado Pago: {nome_arquivo}")
    
    try:
        # Ler XLSX sem header
        df_raw = pd.read_excel(file_path, header=None)
        logger.debug(f"XLSX lido: {len(df_raw)} linhas")
        
        # Extrair saldos da linha 1 (índice 1)
        balance = _extract_balance_info(df_raw)
        logger.info(f"Saldos extraídos: Inicial={balance.saldo_inicial}, Final={balance.saldo_final}")
        
        # Processar transações (a partir da linha 4)
        df_transactions = _preprocess_extrato_mercadopago(df_raw)
        logger.info(f"Extrato preprocessado: {len(df_transactions)} transações")
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for _, row in df_transactions.iterrows():
            transaction = RawTransaction(
                banco='Mercado Pago',
                tipo_documento='extrato',
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=row['data'],
                lancamento=row['lancamento'],
                valor=row['valor'],
                nome_cartao=None,
                final_cartao=None,
                mes_fatura=None,
            )
            transactions.append(transaction)
        
        # Calcular soma das transações e validar
        balance.soma_transacoes = round(sum(t.valor for t in transactions), 2)
        balance.validate()
        
        logger.info(f"✅ Extrato Mercado Pago processado: {len(transactions)} transações")
        logger.info(f"📊 Validação de saldo: {balance.is_valid} (diferença: {balance.diferenca})")
        
        return transactions, balance
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato Mercado Pago: {str(e)}", exc_info=True)
        raise


def _extract_balance_info(df_raw: pd.DataFrame) -> BalanceValidation:
    """
    Extrai saldo inicial e final do extrato Mercado Pago
    
    Linha 1 (índice 1) contém: [saldo_inicial, creditos_totais, debitos_totais, saldo_final, NaN]
    
    Args:
        df_raw: DataFrame bruto do Excel
        
    Returns:
        BalanceValidation com saldos extraídos
    """
    balance = BalanceValidation()
    
    try:
        # Linha 1 tem os valores (índice 1)
        valores_linha = df_raw.iloc[1]
        
        # Coluna 0: INITIAL_BALANCE
        if pd.notna(valores_linha[0]):
            saldo_str = str(valores_linha[0]).replace('.', '').replace(',', '.')
            balance.saldo_inicial = float(saldo_str)
            logger.debug(f"Saldo inicial encontrado: {balance.saldo_inicial}")
        
        # Coluna 3: FINAL_BALANCE
        if pd.notna(valores_linha[3]):
            saldo_str = str(valores_linha[3]).replace('.', '').replace(',', '.')
            balance.saldo_final = float(saldo_str)
            logger.debug(f"Saldo final encontrado: {balance.saldo_final}")
            
    except Exception as e:
        logger.warning(f"Erro ao extrair saldos: {str(e)}")
    
    return balance


def _preprocess_extrato_mercadopago(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessa DataFrame bruto do extrato Mercado Pago XLSX
    
    Args:
        df_raw: DataFrame bruto (header=None)
        
    Returns:
        DataFrame com colunas: data, lancamento, valor
    """
    # Headers das transações estão na linha 3 (índice 3)
    # Transações começam na linha 4 (índice 4)
    df = df_raw.iloc[4:].copy()
    
    # Usar headers da linha 3
    df.columns = df_raw.iloc[3].values
    
    # Resetar index
    df = df.reset_index(drop=True)
    
    # Selecionar colunas relevantes:
    # Coluna 0: RELEASE_DATE (data)
    # Coluna 1: TRANSACTION_TYPE (tipo de transação - será o lançamento)
    # Coluna 3: TRANSACTION_NET_AMOUNT (valor líquido)
    df_processed = df.iloc[:, [0, 1, 3]].copy()
    df_processed.columns = ['data', 'lancamento', 'valor']
    
    # Remover linhas vazias
    df_processed = df_processed.dropna(subset=['data', 'lancamento', 'valor'])
    
    # Converter data de DD-MM-YYYY para DD/MM/YYYY
    df_processed['data'] = pd.to_datetime(df_processed['data'], format='%d-%m-%Y', errors='coerce')
    df_processed = df_processed.dropna(subset=['data'])
    df_processed['data'] = df_processed['data'].dt.strftime('%d/%m/%Y')
    
    # Converter valor (formato brasileiro: 1.234,56 → 1234.56)
    df_processed['valor'] = df_processed['valor'].astype(str)
    df_processed['valor'] = df_processed['valor'].str.replace('.', '', regex=False)  # Remove separador de milhares
    df_processed['valor'] = df_processed['valor'].str.replace(',', '.', regex=False)  # Vírgula vira ponto
    df_processed['valor'] = pd.to_numeric(df_processed['valor'], errors='coerce')
    
    # Remover linhas com valores inválidos
    df_processed = df_processed.dropna(subset=['valor'])
    
    # Remover valores zero (se houver)
    df_processed = df_processed[df_processed['valor'] != 0]
    
    # Limpar texto do lançamento (remover espaços extras)
    df_processed['lancamento'] = df_processed['lancamento'].str.strip()
    
    logger.debug(f"Transações válidas encontradas: {len(df_processed)}")
    
    return df_processed.reset_index(drop=True)
