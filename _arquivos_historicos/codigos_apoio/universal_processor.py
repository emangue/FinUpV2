"""
Universal Transaction Processor
Versão: 1.0.0
Data: 04/01/2026

Recebe 3 campos básicos (Data, Estabelecimento, Valor) de qualquer fonte
e retorna transação processada com:
- IdTransacao (hash FNV-1a)
- IdParcela (hash MD5 para compras parceladas)
- Valores normalizados
- Detecção de parcelas
"""

import sys
import os
import re
from datetime import datetime
import hashlib

# Importar normalizer e hasher
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizer import (
    normalizar, 
    normalizar_estabelecimento, 
    arredondar_2_decimais
)
from hasher import generate_id_transacao


def extrair_info_parcela(estabelecimento, origem=''):
    """
    Extrai informação de parcela do estabelecimento
    
    Args:
        estabelecimento (str): Nome do estabelecimento
        origem (str): Origem da transação
        
    Returns:
        dict: {
            'tem_parcela': bool,
            'estabelecimento_base': str,
            'parcela_atual': int | None,
            'total_parcelas': int | None
        }
    """
    # Tenta formato com parênteses: "LOJA (3/12)"
    match = re.search(r'^(.+?)\s*\((\d{1,2})/(\d{1,2})\)\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        if 1 <= parcela <= total <= 99:
            return {
                'tem_parcela': True,
                'estabelecimento_base': match.group(1).strip(),
                'parcela_atual': parcela,
                'total_parcelas': total
            }
    
    # Tenta formato sem parênteses: "LOJA 3/12"
    match = re.search(r'^(.+?)\s+(\d{1,2})/(\d{1,2})\s*$', estabelecimento)
    if match:
        parcela = int(match.group(2))
        total = int(match.group(3))
        
        # Validação contextual para extratos
        eh_extrato = 'extrato' in origem.lower() or 'person' in origem.lower()
        if eh_extrato and total <= 12 and parcela <= 31:
            # Pode ser data, não parcela
            return {
                'tem_parcela': False,
                'estabelecimento_base': estabelecimento,
                'parcela_atual': None,
                'total_parcelas': None
            }
        
        if 1 <= parcela <= total <= 99:
            return {
                'tem_parcela': True,
                'estabelecimento_base': match.group(1).strip(),
                'parcela_atual': parcela,
                'total_parcelas': total
            }
    
    # Sem parcela
    return {
        'tem_parcela': False,
        'estabelecimento_base': estabelecimento,
        'parcela_atual': None,
        'total_parcelas': None
    }


def normalize_date(date_str):
    """
    Normaliza data para formato DD/MM/YYYY
    
    Aceita formatos:
    - DD/MM/YYYY
    - YYYY-MM-DD
    - DD-MM-YYYY
    - Timestamp ISO
    
    Args:
        date_str (str): Data em qualquer formato
        
    Returns:
        str: Data no formato DD/MM/YYYY
    """
    if not date_str:
        return None
    
    # Já está no formato correto
    if isinstance(date_str, str) and len(date_str) == 10 and '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 3 and len(parts[0]) == 2:
            return date_str
    
    # Tentar parsear diferentes formatos
    formatos = [
        '%Y-%m-%d',        # 2025-12-27
        '%d/%m/%Y',        # 27/12/2025
        '%d-%m-%Y',        # 27-12-2025
        '%Y-%m-%d %H:%M:%S',  # 2025-12-27 10:30:00
        '%d/%m/%Y %H:%M:%S',  # 27/12/2025 10:30:00
    ]
    
    for formato in formatos:
        try:
            dt = datetime.strptime(str(date_str).split('.')[0], formato)
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            continue
    
    # Se não conseguiu, retornar original
    return str(date_str)


def generate_id_parcela(estabelecimento_base, valor, total_parcelas=None):
    """
    Gera IdParcela (MD5 16 caracteres) para identificar contrato de parcelamento
    
    Args:
        estabelecimento_base (str): Estabelecimento sem o XX/YY
        valor (float): Valor da parcela
        total_parcelas (int, optional): Total de parcelas (se conhecido)
        
    Returns:
        str: Hash MD5 de 16 caracteres (hexadecimal)
        
    Examples:
        >>> generate_id_parcela("MERCADOLIVRE", 45.67, 12)
        'a3f2c1d4e5f6g7h8'
    """
    # Normalizar estabelecimento
    estab_norm = normalizar_estabelecimento(estabelecimento_base)
    
    # Arredondar valor
    valor_round = arredondar_2_decimais(valor)
    
    # Criar string para hash
    if total_parcelas:
        hash_input = f"{estab_norm}|{valor_round}|{total_parcelas}"
    else:
        hash_input = f"{estab_norm}|{valor_round}"
    
    # Gerar MD5 e pegar primeiros 16 caracteres
    hash_md5 = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    return hash_md5[:16]


def process_transaction(data, estabelecimento, valor, origem='universal', tipo_transacao='Débito'):
    """
    Processa uma transação individual
    
    Args:
        data (str): Data da transação (qualquer formato)
        estabelecimento (str): Nome do estabelecimento/beneficiário
        valor (float): Valor da transação (positivo ou negativo)
        origem (str): Origem dos dados (ex: 'itau_fatura', 'btg_extrato')
        tipo_transacao (str): 'Débito' ou 'Crédito'
        
    Returns:
        dict: Transação processada com todos os campos necessários
    """
    # Normalizar data
    data_norm = normalize_date(data)
    
    # Normalizar valor (sempre positivo para comparações)
    valor_abs = abs(float(valor))
    valor_positivo = arredondar_2_decimais(valor_abs)
    
    # Detectar parcela
    info_parcela = extrair_info_parcela(estabelecimento, origem)
    
    estabelecimento_base = info_parcela['estabelecimento_base']
    parcela_atual = info_parcela['parcela_atual']
    total_parcelas = info_parcela['total_parcelas']
    tem_parcela = info_parcela['tem_parcela']
    
    # Gerar IdTransacao (hash único da transação)
    # IMPORTANTE: Usa valor original (com sinal) para compatibilidade com journal_entries
    id_transacao = generate_id_transacao(data_norm, estabelecimento, float(valor))
    
    # Gerar IdParcela se tiver parcela
    id_parcela = None
    if tem_parcela and parcela_atual and total_parcelas:
        id_parcela = generate_id_parcela(estabelecimento_base, valor_positivo, total_parcelas)
    
    # Montar transação processada
    transacao = {
        # Campos originais normalizados
        'Data': data_norm,
        'Estabelecimento': estabelecimento,
        'Valor': valor,
        'ValorPositivo': valor_positivo,
        'TipoTransacao': tipo_transacao,
        
        # Campos de identificação
        'IdTransacao': id_transacao,
        'IdParcela': id_parcela,
        
        # Informações de parcela
        'EstabelecimentoBase': estabelecimento_base,
        'ParcelaAtual': parcela_atual,
        'TotalParcelas': total_parcelas,
        'TemParcela': tem_parcela,
        
        # Metadados
        'origem': origem,
        'data_processamento': datetime.now().isoformat(),
    }
    
    return transacao


def process_batch(transacoes, origem='universal'):
    """
    Processa um lote de transações
    
    Args:
        transacoes (list): Lista de dicts com chaves: Data, Estabelecimento, Valor
        origem (str): Origem dos dados
        
    Returns:
        list: Lista de transações processadas
        
    Examples:
        >>> transacoes = [
        ...     {'Data': '27/12/2025', 'Estabelecimento': 'IFOOD 1/3', 'Valor': -45.50},
        ...     {'Data': '28/12/2025', 'Estabelecimento': 'UBER', 'Valor': -18.90}
        ... ]
        >>> processadas = process_batch(transacoes, origem='itau_fatura')
    """
    resultado = []
    
    for idx, transacao in enumerate(transacoes):
        try:
            # Extrair campos obrigatórios
            data = transacao.get('Data') or transacao.get('data')
            estabelecimento = transacao.get('Estabelecimento') or transacao.get('estabelecimento')
            valor = transacao.get('Valor') or transacao.get('valor')
            
            if not data or not estabelecimento or valor is None:
                print(f"⚠️  Transação #{idx+1} ignorada: campos obrigatórios faltando")
                continue
            
            # Detectar tipo de transação
            tipo_transacao = 'Débito'
            if float(valor) > 0:
                tipo_transacao = 'Crédito'
            
            # Processar
            processada = process_transaction(
                data, 
                estabelecimento, 
                valor, 
                origem, 
                tipo_transacao
            )
            
            # Adicionar campos adicionais da transação original
            for key, value in transacao.items():
                if key not in processada:
                    processada[key] = value
            
            resultado.append(processada)
            
        except Exception as e:
            print(f"❌ Erro ao processar transação #{idx+1}: {e}")
            continue
    
    return resultado


def validate_transaction(transacao):
    """
    Valida se uma transação tem os campos mínimos necessários
    
    Args:
        transacao (dict): Transação a validar
        
    Returns:
        tuple: (bool, str) - (é_valida, mensagem_erro)
    """
    campos_obrigatorios = ['Data', 'Estabelecimento', 'Valor']
    
    for campo in campos_obrigatorios:
        if campo not in transacao or not transacao[campo]:
            return False, f"Campo obrigatório ausente: {campo}"
    
    # Validar data
    try:
        data_norm = normalize_date(transacao['Data'])
        if not data_norm or len(data_norm) != 10:
            return False, f"Data inválida: {transacao['Data']}"
    except Exception as e:
        return False, f"Erro ao normalizar data: {e}"
    
    # Validar valor
    try:
        float(transacao['Valor'])
    except (ValueError, TypeError):
        return False, f"Valor inválido: {transacao['Valor']}"
    
    return True, "OK"


if __name__ == '__main__':
    # Testes rápidos
    print("="*70)
    print("UNIVERSAL PROCESSOR - Testes")
    print("="*70)
    
    # Teste 1: Transação simples
    print("\n1. Transação simples:")
    t1 = process_transaction(
        data='27/12/2025',
        estabelecimento='UBER',
        valor=-25.50,
        origem='teste'
    )
    print(f"   IdTransacao: {t1['IdTransacao']}")
    print(f"   Data: {t1['Data']}")
    print(f"   Estabelecimento: {t1['Estabelecimento']}")
    print(f"   ValorPositivo: {t1['ValorPositivo']}")
    print(f"   IdParcela: {t1['IdParcela']}")
    
    # Teste 2: Transação parcelada
    print("\n2. Transação parcelada:")
    t2 = process_transaction(
        data='2025-12-28',
        estabelecimento='MERCADOLIVRE 3/12',
        valor=-89.90,
        origem='itau'
    )
    print(f"   IdTransacao: {t2['IdTransacao']}")
    print(f"   IdParcela: {t2['IdParcela']}")
    print(f"   EstabelecimentoBase: {t2['EstabelecimentoBase']}")
    print(f"   Parcela: {t2['ParcelaAtual']}/{t2['TotalParcelas']}")
    
    # Teste 3: Batch processing
    print("\n3. Processamento em lote:")
    transacoes = [
        {'Data': '27/12/2025', 'Estabelecimento': 'IFOOD 1/3', 'Valor': -45.50},
        {'Data': '28/12/2025', 'Estabelecimento': 'UBER', 'Valor': -18.90},
        {'Data': '29/12/2025', 'Estabelecimento': 'PAGAMENTO RECEBIDO', 'Valor': 1500.00}
    ]
    processadas = process_batch(transacoes, origem='teste')
    print(f"   {len(processadas)} transações processadas")
    for t in processadas:
        print(f"   - {t['Estabelecimento']}: {t['ValorPositivo']} ({t['TipoTransacao']})")
    
    print("\n✅ Testes concluídos")
