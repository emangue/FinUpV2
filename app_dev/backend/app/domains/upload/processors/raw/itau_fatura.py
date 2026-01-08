"""
Processador bruto para Fatura Itaú CSV
Adaptado de codigos_apoio/fatura_itau_csv.py
"""

import logging
import unicodedata
from pathlib import Path
from datetime import datetime
from typing import List
import pandas as pd

from .base import RawTransaction

logger = logging.getLogger(__name__)


def _remove_accents(text: str) -> str:
    """Remove acentos de uma string"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def process_itau_fatura(
    file_path: Path,
    nome_arquivo: str,
    nome_cartao: str,
    final_cartao: str
) -> List[RawTransaction]:
    """
    Processa fatura Itaú CSV
    
    Args:
        file_path: Caminho do arquivo
        nome_arquivo: Nome original do arquivo
        nome_cartao: Nome do cartão (ex: "Mastercard Black")
        final_cartao: Final do cartão (ex: "4321")
        
    Returns:
        Lista de RawTransaction
    """
    logger.info(f"Processando fatura Itaú: {nome_arquivo}")
    
    try:
        # Ler CSV com diferentes encodings possíveis
        for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
            try:
                df_raw = pd.read_csv(file_path, encoding=encoding, sep=',')
                logger.debug(f"✅ CSV lido com {encoding}: {len(df_raw)} linhas")
                break
            except (UnicodeDecodeError, Exception) as e:
                logger.debug(f"⚠️ Tentativa com {encoding} falhou: {str(e)}")
                continue
        else:
            raise ValueError("Não foi possível ler o arquivo CSV com nenhum encoding conhecido")
        
        logger.debug(f"Colunas originais: {df_raw.columns.tolist()}")
        
        # Preprocessar (adaptar lógica de preprocessar_fatura_itau)
        df_processed = _preprocess_fatura_itau(df_raw)
        logger.info(f"Fatura preprocessada: {len(df_processed)} transações")
        
        # Extrair mês da fatura do nome do arquivo (ex: fatura_202601.csv)
        mes_fatura = _extract_mes_fatura(nome_arquivo)
        
        # Converter para RawTransaction
        transactions = []
        data_criacao = datetime.now()
        
        for _, row in df_processed.iterrows():
            transaction = RawTransaction(
                banco='Itaú',
                tipo_documento='fatura',
                nome_arquivo=nome_arquivo,
                data_criacao=data_criacao,
                data=row['data'],
                lancamento=row['lançamento'],
                valor=row['valor (R$)'],
                nome_cartao=nome_cartao,
                final_cartao=final_cartao,
                mes_fatura=mes_fatura,
            )
            transactions.append(transaction)
        
        logger.info(f"✅ Fatura Itaú processada: {len(transactions)} transações")
        return transactions
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar fatura Itaú: {str(e)}", exc_info=True)
        raise


def _preprocess_fatura_itau(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocessa DataFrame bruto da fatura Itaú
    Lógica adaptada de fatura_itau_csv.preprocessar_fatura_itau()
    """
    # Normalizar nomes de colunas originais (sem acentos)
    df_raw.columns = [_remove_accents(str(col).strip().lower()) for col in df_raw.columns]
    logger.debug(f"Colunas após normalização: {df_raw.columns.tolist()}")
    
    # Verificar se já tem o cabeçalho correto
    if 'data' in df_raw.columns and ('lancamento' in df_raw.columns or 'estabelecimento' in df_raw.columns):
        logger.debug("✅ Cabeçalho já está na primeira linha")
        df = df_raw.copy()
    else:
        # Procurar cabeçalho nas primeiras 5 linhas (valores, não colunas)
        header_row = None
        for i in range(min(5, len(df_raw))):
            row_str = ' '.join(str(val).lower() for val in df_raw.iloc[i].values if pd.notna(val))
            row_str_norm = _remove_accents(row_str)
            
            if 'data' in row_str_norm and ('lancamento' in row_str_norm or 'estabelecimento' in row_str_norm):
                header_row = i
                logger.debug(f"✅ Cabeçalho encontrado na linha {i}: {row_str}")
                break
        
        if header_row is None:
            raise ValueError(
                "Este arquivo não parece ser uma fatura do Itaú no formato CSV esperado. "
                "Verifique se o arquivo contém as colunas: data, lançamento/estabelecimento, valor (separadas por vírgula ou ponto-e-vírgula)."
            )
        
        # Criar novo DataFrame a partir do cabeçalho
        df = df_raw.iloc[header_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # Normalizar nomes de colunas
        df.columns = [_remove_accents(str(col).strip().lower()) for col in df.columns]
        logger.debug(f"Colunas normalizadas após ajuste: {df.columns.tolist()}")
    
    # Mapear colunas
    col_map = {}
    for col in df.columns:
        if 'data' in col:
            col_map[col] = 'data'
        elif 'lancamento' in col or 'estabelecimento' in col or 'descrição' in col:
            col_map[col] = 'lançamento'
        elif 'valor' in col:
            col_map[col] = 'valor (R$)'
    
    df = df.rename(columns=col_map)
    
    # Selecionar apenas colunas necessárias
    required_cols = ['data', 'lançamento', 'valor (R$)']
    df = df[required_cols].copy()
    
    # Limpar dados
    df = df.dropna(subset=['data', 'lançamento', 'valor (R$)'])
    
    # Converter valor para float (manter sinal original do arquivo)
    df['valor (R$)'] = df['valor (R$)'].apply(_convert_valor_br)
    
    # Remover valores zero (exclusões específicas vêm da tabela transacoes_exclusao)
    df = df[df['valor (R$)'] != 0]
    
    return df.reset_index(drop=True)


def _convert_valor_br(valor_str) -> float:
    """
    Converte valor para float, detectando formato automaticamente
    
    Formatos aceitos:
    - Brasileiro: 1.234,56 (ponto = milhar, vírgula = decimal)
    - Americano: 1,234.56 (vírgula = milhar, ponto = decimal)
    - Simples: 1234.56 ou 1234,56
    """
    if pd.isna(valor_str):
        return 0.0
    
    valor_str = str(valor_str).strip()
    
    # Detectar formato baseado em posições de vírgula e ponto
    tem_virgula = ',' in valor_str
    tem_ponto = '.' in valor_str
    
    if tem_virgula and tem_ponto:
        # Ambos presentes: ver qual vem por último (é o decimal)
        pos_virgula = valor_str.rfind(',')
        pos_ponto = valor_str.rfind('.')
        
        if pos_ponto > pos_virgula:
            # Formato americano: 1,234.56
            valor_str = valor_str.replace(',', '')  # Remove separador de milhar
        else:
            # Formato brasileiro: 1.234,56
            valor_str = valor_str.replace('.', '')  # Remove separador de milhar
            valor_str = valor_str.replace(',', '.')  # Troca vírgula por ponto
    elif tem_virgula:
        # Só vírgula: pode ser decimal brasileiro (42,29) ou milhar americano (1,234)
        # Se há apenas uma vírgula E tem no máximo 2 dígitos após ela, é decimal
        partes = valor_str.split(',')
        if len(partes) == 2 and len(partes[1]) <= 2:
            # Formato brasileiro: 42,29
            valor_str = valor_str.replace(',', '.')
        else:
            # Formato americano milhar: 1,234
            valor_str = valor_str.replace(',', '')
    # Se só tem ponto, deixa como está (formato americano decimal)
    
    try:
        return float(valor_str)
    except ValueError:
        logger.warning(f"Não foi possível converter valor: {valor_str}")
        return 0.0


def _extract_mes_fatura(nome_arquivo: str) -> str:
    """
    Extrai mês da fatura do nome do arquivo
    Ex: fatura_202601.csv → '202601'
    """
    import re
    match = re.search(r'(\d{6})', nome_arquivo)
    if match:
        return match.group(1)
    
    # Fallback: usar mês/ano atual
    now = datetime.now()
    return now.strftime('%Y%m')
