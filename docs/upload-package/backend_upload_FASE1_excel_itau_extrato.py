"""
Processador bruto para Extrato Itaú XLS
Adaptado de codigos_apoio/extrato_itau_xls.py
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import pandas as pd

from ..base import RawTransaction, BalanceValidation

logger = logging.getLogger(__name__)


def process_itau_extrato(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str = None,
    final_cartao: str = None
) -> Tuple[List[RawTransaction], BalanceValidation]:
    """
    Processa extrato Itaú XLS
    
    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        nome_cartao: Não usado para extrato (None)
        final_cartao: Não usado para extrato (None)
        
    Returns:
        Tupla (Lista de RawTransaction, BalanceValidation)
    """
    logger.info(f"Processando extrato Itaú: {nome_arquivo}")
    
    try:
        # Ler XLS
        df_raw = pd.read_excel(file_path)
        logger.debug(f"XLS lido: {len(df_raw)} linhas")
        
        # Extrair saldos ANTES de preprocessar
        balance = _extract_balance_info(df_raw)
        logger.info(f"Saldos extraídos: Inicial={balance.saldo_inicial}, Final={balance.saldo_final}")
        
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
        
        # Calcular soma das transações e validar
        balance.soma_transacoes = round(sum(t.valor for t in transactions), 2)
        balance.validate()
        
        logger.info(f"✅ Extrato Itaú processado: {len(transactions)} transações")
        logger.info(f"📊 Validação de saldo: {balance.is_valid} (diferença: {balance.diferenca})")
        
        return transactions, balance
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar extrato Itaú: {str(e)}", exc_info=True)
        raise


def _extract_balance_info(df_raw: pd.DataFrame) -> BalanceValidation:
    """
    Extrai saldo inicial e final do extrato Itaú
    
    Args:
        df_raw: DataFrame bruto do Excel
        
    Returns:
        BalanceValidation com saldos extraídos
    """
    balance = BalanceValidation()
    
    # Procurar saldo inicial (SALDO ANTERIOR)
    for i in range(min(30, len(df_raw))):
        row_values = df_raw.iloc[i].values
        # Verificar se é linha de SALDO ANTERIOR
        for j, val in enumerate(row_values):
            if pd.notna(val) and 'SALDO ANTERIOR' in str(val).upper():
                # Saldo está na última coluna (saldos R$) - geralmente coluna 4
                if len(row_values) > 4 and pd.notna(row_values[4]):
                    try:
                        balance.saldo_inicial = float(row_values[4])
                        logger.debug(f"Saldo inicial encontrado: {balance.saldo_inicial}")
                    except (ValueError, TypeError):
                        pass
                break
    
    # Procurar saldo final (última linha com SALDO TOTAL DISPONÍVEL DIA)
    # IMPORTANTE: Pegar o último mesmo que seja zero, para validar todas as transações
    for i in range(len(df_raw)-1, -1, -1):
        row_values = df_raw.iloc[i].values
        # Verificar se é linha de SALDO TOTAL
        for j, val in enumerate(row_values):
            if pd.notna(val) and 'SALDO TOTAL' in str(val).upper():
                # Saldo está na última coluna (saldos R$) - geralmente coluna 4
                if len(row_values) > 4 and pd.notna(row_values[4]):
                    try:
                        balance.saldo_final = float(row_values[4])
                        logger.debug(f"Saldo final encontrado: {balance.saldo_final}")
                        return balance  # Retornar assim que encontrar o último
                    except (ValueError, TypeError):
                        pass
                break
    
    return balance


def _preprocess_extrato_itau(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessa DataFrame bruto do extrato Itaú XLS
    Lógica simplificada de extrato_itau_xls.preprocessar_extrato_itau_xls()
    """
    # Detectar linha do cabeçalho (linha 7/8 geralmente)
    header_row = None
    for i in range(min(20, len(df_raw))):
        row_str = ' '.join(str(val).lower() for val in df_raw.iloc[i].values if pd.notna(val))
        # Verificar se linha contém as 3 colunas principais
        if 'data' in row_str and ('lancamento' in row_str or 'lançamento' in row_str) and 'valor' in row_str:
            header_row = i
            logger.debug(f"Cabeçalho encontrado na linha {i}")
            break
    
    if header_row is None:
        raise ValueError(
            "Este arquivo não parece ser um extrato do Itaú no formato XLS esperado. "
            "Verifique se o arquivo contém as colunas: data, lançamento, valor (geralmente a partir da linha 7-8)."
        )
    
    # Extrair dados a partir do cabeçalho
    df = df_raw.iloc[header_row:].copy()
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    
    # Normalizar nomes de colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Log das colunas encontradas
    logger.debug(f"Colunas após normalização: {list(df.columns)}")
    
    # Pular primeira linha se for apenas "lançamentos" (linha decorativa)
    if len(df) > 0:
        first_row_str = ' '.join(str(val).lower() for val in df.iloc[0].values if pd.notna(val))
        if first_row_str.strip() == 'lançamentos':
            logger.debug("Pulando linha decorativa 'lançamentos'")
            df = df[1:].reset_index(drop=True)
    
    # Selecionar apenas colunas necessárias (data, lançamento, valor)
    # XLS Itaú: coluna 0=data, coluna 1=lançamento/lancamento, coluna 3=valor (R$)
    df = df.iloc[:, [0, 1, 3]].copy()
    df.columns = ['data', 'lançamento', 'valor (R$)']
    
    # IMPORTANTE: Remover lançamentos futuros ANTES do dropna()
    # Procurar linha marcadora "saídas futuras" ou "lançamentos futuros"
    # Essas linhas podem ter NaN nas colunas, então precisamos verificar antes de limpar
    for i in range(len(df)):
        # Verificar TODAS as colunas da linha para detectar marcadores
        row_values = df.iloc[i].values
        row_text = ' '.join(str(val).lower() for val in row_values if pd.notna(val))
        
        # Detectar marcadores de lançamentos futuros
        if ('saída' in row_text or 'saida' in row_text) and 'futura' in row_text:
            logger.debug(f"Encontrada linha marcadora de futuras na posição {i}: '{row_text}', removendo {len(df) - i} linhas")
            df = df.iloc[:i].copy()
            break
        if 'lançamento' in row_text and 'futuro' in row_text:
            logger.debug(f"Encontrada linha 'lançamentos futuros' na posição {i}: '{row_text}', removendo {len(df) - i} linhas")
            df = df.iloc[:i].copy()
            break
    
    # Limpar dados (agora sim, depois de remover futuras)
    df = df.dropna(subset=['data', 'lançamento', 'valor (R$)'])
    
    # Filtrar linhas que NÃO são transações reais (saldos)
    # Remover linhas com "SALDO ANTERIOR", "SALDO TOTAL", etc
    df = df[~df['lançamento'].str.upper().str.contains('SALDO', na=False)]
    logger.debug(f"Após filtrar saldos: {len(df)} linhas")
    
    # Converter valor para float
    df['valor (R$)'] = pd.to_numeric(df['valor (R$)'], errors='coerce')
    df = df.dropna(subset=['valor (R$)'])
    
    # Remover valores zero
    df = df[df['valor (R$)'] != 0]
    
    # Converter data para DD/MM/YYYY
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['data'])
    df['data'] = df['data'].dt.strftime('%d/%m/%Y')
    
    logger.debug(f"Transações válidas encontradas: {len(df)}")
    
    return df.reset_index(drop=True)
