"""
Detector - Detecção inteligente de tipo de arquivo e colunas
"""
import pandas as pd
import re
from datetime import datetime


# Palavras-chave para identificar tipo de arquivo
INDICADORES_EXTRATO = [
    'pix', 'ted', 'doc', 'transferencia', 'transferência',
    'rendimento', 'juros', 'caixinha', 'saldo', 'deposito', 'depósito',
    'debito automatico', 'débito automático', 'resgate', 'aplicacao', 'aplicação'
]

INDICADORES_FATURA = [
    'parcela', 'parc', '/12', '/10', '/6', '/3',  # Detecta n/n
    'pagamento efetuado', 'anuidade', 'compra parcelada',
    'fatura anterior', 'limite disponivel', 'limite disponível'
]


def detectar_tipo_arquivo(df):
    """
    Detecta se o arquivo é Fatura de Cartão ou Extrato de Conta
    baseado em palavras-chave no conteúdo
    
    Args:
        df (DataFrame): DataFrame com os dados do arquivo
        
    Returns:
        dict: {
            'tipo': 'fatura' ou 'extrato',
            'confianca': float (0-1),
            'indicadores_encontrados': list
        }
    """
    # Converte tudo para texto para análise
    texto_completo = ''
    for col in df.columns:
        texto_completo += ' ' + df[col].astype(str).str.cat(sep=' ')
    
    texto_lower = texto_completo.lower()
    
    # Conta indicadores
    score_extrato = 0
    indicadores_extrato = []
    for indicador in INDICADORES_EXTRATO:
        if indicador in texto_lower:
            score_extrato += 1
            indicadores_extrato.append(indicador)
    
    score_fatura = 0
    indicadores_fatura = []
    for indicador in INDICADORES_FATURA:
        if indicador in texto_lower:
            score_fatura += 1
            indicadores_fatura.append(indicador)
    
    # Detecta padrão de parcelas (ex: "1/12", "02/10")
    if re.search(r'\d{1,2}/\d{1,2}(?!\d)', texto_completo):
        score_fatura += 2  # Peso maior para parcelas
        indicadores_fatura.append('padrão de parcelas')
    
    # Decisão
    total_score = score_extrato + score_fatura
    
    if total_score == 0:
        # Não conseguiu identificar
        return {
            'tipo': None,
            'confianca': 0.0,
            'indicadores_encontrados': []
        }
    
    if score_fatura > score_extrato:
        tipo = 'fatura'
        confianca = score_fatura / (total_score + 5)  # Normaliza
        indicadores = indicadores_fatura
    else:
        tipo = 'extrato'
        confianca = score_extrato / (total_score + 5)
        indicadores = indicadores_extrato
    
    return {
        'tipo': tipo,
        'confianca': min(confianca, 1.0),
        'indicadores_encontrados': indicadores
    }


def detectar_colunas(df):
    """
    Detecta automaticamente as colunas de Data, Estabelecimento e Valor
    
    Args:
        df (DataFrame): DataFrame com os dados do arquivo
        
    Returns:
        dict: {
            'data': nome_coluna ou None,
            'estabelecimento': nome_coluna ou None,
            'valor': nome_coluna ou None
        }
    """
    mapeamento = {
        'data': None,
        'estabelecimento': None,
        'valor': None
    }
    
    # Palavras-chave para cada tipo de coluna
    palavras_data = ['data', 'date', 'dt', 'fecha', 'dia']
    palavras_estabelecimento = [
        'estabelecimento', 'merchant', 'description', 'desc', 
        'comercio', 'comércio', 'lancamento', 'lançamento',
        'historico', 'histórico', 'descricao', 'descrição'
    ]
    palavras_valor = [
        'valor', 'value', 'amount', 'price', 'preco', 'preço',
        'montante', 'total', 'quantia'
    ]
    
    # Busca por nome de coluna
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # Data
        if not mapeamento['data']:
            if any(palavra in col_lower for palavra in palavras_data):
                mapeamento['data'] = col
        
        # Estabelecimento
        if not mapeamento['estabelecimento']:
            if any(palavra in col_lower for palavra in palavras_estabelecimento):
                mapeamento['estabelecimento'] = col
        
        # Valor
        if not mapeamento['valor']:
            if any(palavra in col_lower for palavra in palavras_valor):
                mapeamento['valor'] = col
    
    # Se não encontrou por nome, tenta por conteúdo
    if not mapeamento['data']:
        # Procura coluna com formato de data
        for col in df.columns:
            sample = df[col].dropna().head(10).astype(str)
            # Testa formatos comuns: DD/MM/YYYY, YYYY-MM-DD, DD-MM-YYYY
            if sample.str.match(r'^\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}').any():
                mapeamento['data'] = col
                break
    
    if not mapeamento['valor']:
        # Procura coluna numérica (pode ter vírgula ou ponto)
        for col in df.columns:
            try:
                # Tenta converter para numérico
                sample = df[col].dropna().head(10).astype(str)
                if sample.str.match(r'^-?\d+[.,]?\d*$').sum() >= 5:  # Maioria é número
                    mapeamento['valor'] = col
                    break
            except:
                continue
    
    if not mapeamento['estabelecimento']:
        # Se sobrou só uma coluna não mapeada com texto, assume como estabelecimento
        colunas_nao_mapeadas = [
            col for col in df.columns 
            if col not in mapeamento.values()
        ]
        if len(colunas_nao_mapeadas) == 1:
            mapeamento['estabelecimento'] = colunas_nao_mapeadas[0]
    
    return mapeamento


def mapear_colunas(df, col_data, col_estabelecimento, col_valor):
    """
    Valida e retorna um mapeamento de colunas
    
    Args:
        df (DataFrame): DataFrame com os dados
        col_data (str): Nome da coluna de data
        col_estabelecimento (str): Nome da coluna de estabelecimento
        col_valor (str): Nome da coluna de valor
        
    Returns:
        dict: Mapeamento validado ou None se inválido
    """
    # Valida se as colunas existem
    if not all(col in df.columns for col in [col_data, col_estabelecimento, col_valor]):
        return None
    
    return {
        'data': col_data,
        'estabelecimento': col_estabelecimento,
        'valor': col_valor
    }
