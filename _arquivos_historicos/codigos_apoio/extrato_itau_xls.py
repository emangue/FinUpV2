"""
Preprocessador para arquivos XLS de extrato do Itaú

O arquivo XLS do Itaú tem estrutura especial:
- Linhas 0-7: Cabeçalhos do banco e info da conta
- Linha 8: Headers reais (data, lançamento, ag./origem, valor (R$), saldos (R$))
- Linha 9: Texto "lançamentos" (ignorar)
- Linha 10+: Dados das transações
- Linhas de saldo devem ser filtradas (SALDO ANTERIOR, SALDO TOTAL DISPONÍVEL DIA)

Inclui validação de integridade:
- Saldo Anterior + Σ Transações = Saldo Total Disponível Final

Versão: 1.1.0
Data: 27/12/2025
Autor: Sistema de Versionamento
"""

import pandas as pd
import numpy as np
from datetime import datetime


def detectar_estrutura_extrato(df_raw):
    """
    Analisa arquivo bruto e detecta automaticamente onde começam os dados
    
    Args:
        df_raw: DataFrame bruto sem processamento
        
    Returns:
        dict com informações da estrutura:
        {
            'linha_header': int,
            'linha_dados_inicio': int,
            'headers': list,
            'info_conta': dict
        }
    """
    estrutura = {
        'linha_header': None,
        'linha_dados_inicio': None,
        'headers': [],
        'info_conta': {}
    }
    
    # Procurar linha com headers (data, lançamento, valor)
    for idx in range(min(15, len(df_raw))):
        row = df_raw.iloc[idx].tolist()
        row_str = [str(x).lower().strip() for x in row if pd.notna(x)]
        
        # Procurar por palavras-chave de header
        if 'data' in row_str and 'lançamento' in row_str:
            estrutura['linha_header'] = idx
            estrutura['headers'] = [str(x) for x in df_raw.iloc[idx].tolist()]
            break
    
    if estrutura['linha_header'] is None:
        raise ValueError("Não foi possível detectar linha de headers no arquivo")
    
    # Dados começam 2 linhas após header (pular linha com "lançamentos")
    estrutura['linha_dados_inicio'] = estrutura['linha_header'] + 2
    
    # Extrair informações da conta (linhas 2-4)
    try:
        if len(df_raw) > 4:
            nome_row = df_raw.iloc[2].tolist()
            if len(nome_row) >= 2 and str(nome_row[0]).strip() == 'Nome:':
                estrutura['info_conta']['nome'] = str(nome_row[1]).strip()
            
            agencia_row = df_raw.iloc[3].tolist()
            if len(agencia_row) >= 2 and str(agencia_row[0]).strip() == 'Agência:':
                estrutura['info_conta']['agencia'] = str(agencia_row[1]).strip()
            
            conta_row = df_raw.iloc[4].tolist()
            if len(conta_row) >= 2 and str(conta_row[0]).strip() == 'Conta:':
                estrutura['info_conta']['conta'] = str(conta_row[1]).strip()
    except Exception as e:
        print(f"⚠️ Não foi possível extrair info da conta: {e}")
    
    return estrutura


def extrair_saldos(df):
    """
    Extrai saldo anterior e saldo final do DataFrame
    
    Args:
        df: DataFrame com todas as linhas (incluindo saldos)
        
    Returns:
        dict com {
            'saldo_anterior': float,
            'saldo_final': float,
            'data_inicial': str,
            'data_final': str
        }
    """
    saldos = {
        'saldo_anterior': None,
        'saldo_final': None,
        'data_inicial': None,
        'data_final': None
    }
    
    # Procurar SALDO ANTERIOR (primeira linha com saldo)
    saldo_anterior_rows = df[
        df['lançamento'].str.contains('SALDO ANTERIOR', case=False, na=False)
    ]
    
    if len(saldo_anterior_rows) > 0:
        primeira_linha = saldo_anterior_rows.iloc[0]
        saldos['saldo_anterior'] = pd.to_numeric(primeira_linha['saldos (R$)'], errors='coerce')
        saldos['data_inicial'] = primeira_linha['data']
    
    # Procurar último SALDO TOTAL DISPONÍVEL DIA antes de "lançamentos futuros"
    # Primeiro, encontrar onde começam os lançamentos futuros (procurar em todas as colunas)
    futuros_mask = df.apply(lambda row: row.astype(str).str.contains('lançamentos futuros', case=False, na=False).any(), axis=1)
    futuros_idx = df[futuros_mask].index
    
    if len(futuros_idx) > 0:
        # Considerar apenas linhas antes de "lançamentos futuros"
        df_ate_hoje = df.loc[:futuros_idx[0]-1]
    else:
        df_ate_hoje = df
    
    # Procurar último saldo disponível (aceitar variações de escrita)
    saldo_final_rows = df_ate_hoje[
        df_ate_hoje['lançamento'].str.contains('SALDO TOTAL DISPON', case=False, na=False)
    ]
    
    if len(saldo_final_rows) > 0:
        ultima_linha = saldo_final_rows.iloc[-1]
        saldos['saldo_final'] = pd.to_numeric(ultima_linha['saldos (R$)'], errors='coerce')
        saldos['data_final'] = ultima_linha['data']
    
    return saldos


def validar_integridade_extrato(df_transacoes, saldos):
    """
    Valida se Saldo Anterior + Σ Transações = Saldo Final
    
    Args:
        df_transacoes: DataFrame apenas com transações (sem linhas de saldo)
        saldos: dict com saldo_anterior e saldo_final
        
    Returns:
        dict com resultado da validação:
        {
            'valido': bool,
            'saldo_anterior': float,
            'soma_transacoes': float,
            'saldo_calculado': float,
            'saldo_final_arquivo': float,
            'diferenca': float,
            'mensagem': str
        }
    """
    resultado = {
        'valido': False,
        'saldo_anterior': saldos.get('saldo_anterior', 0.0),
        'soma_transacoes': 0.0,
        'saldo_calculado': 0.0,
        'saldo_final_arquivo': saldos.get('saldo_final', 0.0),
        'diferenca': 0.0,
        'mensagem': ''
    }
    
    # Calcular soma das transações (aceitar ambos os nomes de coluna)
    coluna_valor = 'valor (R$)' if 'valor (R$)' in df_transacoes.columns else 'Valor'
    if coluna_valor in df_transacoes.columns:
        resultado['soma_transacoes'] = df_transacoes[coluna_valor].sum()
    
    # Calcular saldo esperado
    if resultado['saldo_anterior'] is not None:
        resultado['saldo_calculado'] = resultado['saldo_anterior'] + resultado['soma_transacoes']
    else:
        resultado['mensagem'] = "⚠️ Saldo anterior não encontrado no arquivo"
        return resultado
    
    # Verificar se saldo final existe
    if resultado['saldo_final_arquivo'] is None:
        resultado['mensagem'] = "⚠️ Saldo final não encontrado no arquivo"
        return resultado
    
    # Calcular diferença
    resultado['diferenca'] = resultado['saldo_calculado'] - resultado['saldo_final_arquivo']
    
    # Validar (tolerância de R$ 0.01 para erros de arredondamento)
    if abs(resultado['diferenca']) <= 0.01:
        resultado['valido'] = True
        resultado['mensagem'] = "✅ Extrato validado: Saldo Anterior + Transações = Saldo Final"
    else:
        resultado['valido'] = False
        resultado['mensagem'] = f"❌ ERRO DE VALIDAÇÃO: Diferença de R$ {resultado['diferenca']:.2f}"
    
    return resultado


def is_extrato_itau_xls(df_raw, filename):
    """
    Detecta se o arquivo é um extrato Itaú XLS
    
    Args:
        df_raw: DataFrame lido sem tratamento
        filename: Nome do arquivo
        
    Returns:
        bool: True se for extrato Itaú XLS
    """
    if not filename.lower().endswith('.xls'):
        return False
    
    # Verifica se linha 0 contém "Logotipo Itaú"
    if df_raw.shape[0] < 10:
        return False
    
    primeira_celula = str(df_raw.iloc[0, 0]).strip() if pd.notna(df_raw.iloc[0, 0]) else ''
    
    if 'Logotipo' in primeira_celula and 'Itaú' in primeira_celula:
        return True
    
    if 'Itaú' in primeira_celula or 'ITAU' in primeira_celula.upper():
        return True
    
    # Verifica se linha 6 contém "Lançamentos"
    if df_raw.shape[0] > 6:
        linha6 = str(df_raw.iloc[6, 0]).strip() if pd.notna(df_raw.iloc[6, 0]) else ''
        if 'Lançamentos' in linha6 or 'LANÇAMENTOS' in linha6.upper():
            return True
    
    # Verifica se linha 8 tem headers esperados
    if df_raw.shape[0] > 8:
        row8 = df_raw.iloc[8].tolist()
        row8_str = [str(x).lower() for x in row8 if pd.notna(x)]
        if 'data' in row8_str and 'lançamento' in row8_str:
            return True
    
    return False


def preprocessar_extrato_itau_xls(df_raw):
    """
    Preprocessa arquivo XLS do extrato Itaú para formato padronizado
    
    Args:
        df_raw: DataFrame bruto lido com pd.read_excel()
        
    Returns:
        tuple: (DataFrame processado, dict com validação)
    """
    print("🏦 Detectado: Extrato Itaú XLS")
    print(f"   Shape bruto: {df_raw.shape[0]} linhas x {df_raw.shape[1]} colunas")
    
    # 1. Detectar estrutura automaticamente
    print("\n📊 ETAPA 1: Detectando estrutura do arquivo...")
    estrutura = detectar_estrutura_extrato(df_raw)
    print(f"   ✓ Linha de headers: {estrutura['linha_header']}")
    print(f"   ✓ Início dos dados: {estrutura['linha_dados_inicio']}")
    if estrutura['info_conta']:
        print(f"   ✓ Conta: {estrutura['info_conta'].get('nome', 'N/A')}")
        print(f"   ✓ Agência: {estrutura['info_conta'].get('agencia', 'N/A')} / Conta: {estrutura['info_conta'].get('conta', 'N/A')}")
    
    # 2. Extrair dados com headers corretos
    headers = estrutura['headers']
    df = df_raw.iloc[estrutura['linha_dados_inicio']:].copy()
    df.columns = headers
    df = df.reset_index(drop=True)
    
    print(f"\n   Dados brutos extraídos: {len(df)} linhas")
    
    # 3. Extrair saldos ANTES de filtrar
    print("\n📊 ETAPA 2: Extraindo saldos para validação...")
    saldos = extrair_saldos(df)
    
    if saldos['saldo_anterior'] is not None:
        print(f"   ✓ Saldo Anterior ({saldos['data_inicial']}): R$ {saldos['saldo_anterior']:.2f}")
    else:
        print(f"   ⚠️ Saldo Anterior não encontrado")
    
    if saldos['saldo_final'] is not None:
        print(f"   ✓ Saldo Final ({saldos['data_final']}): R$ {saldos['saldo_final']:.2f}")
    else:
        print(f"   ⚠️ Saldo Final não encontrado")
    
    # 4. Filtrar apenas transações (remover linhas de saldo e lançamentos futuros)
    print("\n📊 ETAPA 3: Filtrando transações válidas...")
    
    # Encontrar onde começam os lançamentos futuros (procurar em todas as colunas)
    futuros_mask = df.apply(lambda row: row.astype(str).str.contains('lançamentos futuros', case=False, na=False).any(), axis=1)
    futuros_idx = df[futuros_mask].index
    
    if len(futuros_idx) > 0:
        print(f"   ✓ Encontrados lançamentos futuros na linha {futuros_idx[0]}")
        df = df.loc[:futuros_idx[0]-1].copy()
        print(f"   ✓ Descartadas {len(df_raw) - len(df) - estrutura['linha_dados_inicio']} linhas futuras")
    
    # Filtrar transações válidas
    condicao_valida = (
        df['lançamento'].notna() & 
        ~df['lançamento'].str.contains('SALDO', case=False, na=False)
    )
    
    df_transacoes = df[condicao_valida].copy()
    
    print(f"   ✓ Transações válidas: {len(df_transacoes)} linhas")
    
    # 5. Selecionar apenas colunas necessárias (MANTER NOMES ORIGINAIS)
    colunas_necessarias = ['data', 'lançamento', 'valor (R$)']
    colunas_disponiveis = [col for col in colunas_necessarias if col in df_transacoes.columns]
    df_transacoes = df_transacoes[colunas_disponiveis].copy()
    
    # 6. Converter valores para numérico
    if 'valor (R$)' in df_transacoes.columns:
        df_transacoes['valor (R$)'] = pd.to_numeric(df_transacoes['valor (R$)'], errors='coerce')
        df_transacoes = df_transacoes[df_transacoes['valor (R$)'].notna()]
    
    # 7. Limpar espaços em branco
    for col in df_transacoes.columns:
        if df_transacoes[col].dtype == 'object':
            df_transacoes[col] = df_transacoes[col].str.strip()
    
    # 8. VALIDAR INTEGRIDADE (usar nome original da coluna)
    print("\n📊 ETAPA 4: Validando integridade dos dados...")
    validacao = validar_integridade_extrato(df_transacoes, saldos)
    
    print(f"   {validacao['mensagem']}")
    if validacao['valido']:
        print(f"   ✓ Saldo Anterior: R$ {validacao['saldo_anterior']:.2f}")
        print(f"   ✓ Soma Transações: R$ {validacao['soma_transacoes']:.2f}")
        print(f"   ✓ Saldo Calculado: R$ {validacao['saldo_calculado']:.2f}")
        print(f"   ✓ Saldo Arquivo: R$ {validacao['saldo_final_arquivo']:.2f}")
        print(f"   ✓ Diferença: R$ {validacao['diferenca']:.4f}")
    else:
        print(f"   ⚠️ Saldo Anterior: R$ {validacao['saldo_anterior']:.2f}")
        print(f"   ⚠️ Soma Transações: R$ {validacao['soma_transacoes']:.2f}")
        print(f"   ⚠️ Saldo Calculado: R$ {validacao['saldo_calculado']:.2f}")
        print(f"   ⚠️ Saldo Arquivo: R$ {validacao['saldo_final_arquivo']:.2f}")
        print(f"   ⚠️ Diferença: R$ {validacao['diferenca']:.2f}")
    
    print(f"\n✅ Preprocessamento concluído: {len(df_transacoes)} transações")
    print(f"   Colunas finais: {list(df_transacoes.columns)}")
    print(f"   Período: {saldos['data_inicial']} até {saldos['data_final']}")
    
    # Retornar DataFrame e informações de validação
    validacao['estrutura'] = estrutura
    validacao['saldos'] = saldos
    validacao['periodo'] = {
        'data_inicial': saldos['data_inicial'],
        'data_final': saldos['data_final']
    }
    
    return df_transacoes, validacao
