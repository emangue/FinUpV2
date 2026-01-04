"""
Preprocessador para arquivos XLSX de extrato do Mercado Pago

O arquivo XLSX do Mercado Pago tem estrutura especial:
- Linha 1: Headers de totais (INITIAL_BALANCE, CREDITS, DEBITS, FINAL_BALANCE)
- Linha 2: Valores dos totais (ex: 968,20  68.079,29  -68.538,32  509,17)
- Linha 3: Vazia
- Linha 4: Headers das transações (RELEASE_DATE, TRANSACTION_TYPE, REFERENCE_ID, TRANSACTION_NET_AMOUNT, PARTIAL_BALANCE)
- Linha 5+: Transações

Validação:
- INITIAL_BALANCE + Σ(TRANSACTION_NET_AMOUNT) ≈ FINAL_BALANCE (±0.01)

Mapeamento:
- Data: RELEASE_DATE (coluna A) - converter "01-10-2025" → "01/10/2025"
- Lançamento: TRANSACTION_TYPE (coluna B)
- Valor: TRANSACTION_NET_AMOUNT (coluna D) - converter "1.232,46" → 1232.46

Versão: 1.0.0
Data: 27/12/2025
"""

import pandas as pd
import numpy as np
from datetime import datetime


def converter_valor_br(valor_str):
    """
    Converte valor em formato brasileiro para float
    
    Args:
        valor_str: String no formato "1.232,46" ou "968,20"
        
    Returns:
        float: Valor convertido
    """
    try:
        if pd.isna(valor_str):
            return np.nan
        
        valor_str = str(valor_str).strip()
        
        # Remove pontos (separador de milhar)
        valor_str = valor_str.replace('.', '')
        
        # Substitui vírgula por ponto (separador decimal)
        valor_str = valor_str.replace(',', '.')
        
        return float(valor_str)
    except:
        return np.nan


def is_extrato_mercadopago(df_raw, filename):
    """
    Detecta se o arquivo é um extrato Mercado Pago
    
    Args:
        df_raw: DataFrame lido sem tratamento
        filename: Nome do arquivo
        
    Returns:
        bool: True se for extrato Mercado Pago
    """
    try:
        if not filename.lower().endswith('.xlsx'):
            return False
        
        if df_raw.shape[0] < 5:
            return False
        
        # Verifica se linha 1 (index 0) tem headers esperados
        linha1 = df_raw.iloc[0].tolist()
        linha1_str = [str(x).upper().strip() for x in linha1 if pd.notna(x)]
        
        # Deve conter INITIAL_BALANCE e CREDITS e DEBITS
        has_initial = any('INITIAL' in s and 'BALANCE' in s for s in linha1_str)
        has_credits = any('CREDITS' in s for s in linha1_str)
        has_debits = any('DEBITS' in s for s in linha1_str)
        
        if has_initial and has_credits and has_debits:
            return True
        
        # Verifica se linha 4 (index 3) tem headers de transação
        if df_raw.shape[0] > 3:
            linha4 = df_raw.iloc[3].tolist()
            linha4_str = [str(x).upper().strip() for x in linha4 if pd.notna(x)]
            
            has_release_date = any('RELEASE' in s and 'DATE' in s for s in linha4_str)
            has_transaction = any('TRANSACTION' in s for s in linha4_str)
            
            if has_release_date and has_transaction:
                return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Erro ao detectar Mercado Pago: {e}")
        return False


def preprocessar_extrato_mercadopago(df_raw):
    """
    Preprocessa arquivo XLSX do extrato Mercado Pago para formato padronizado
    
    Args:
        df_raw: DataFrame bruto lido com pd.read_excel()
        
    Returns:
        tuple: (DataFrame processado, dict com validação)
    """
    print("🏦 Detectado: Extrato Mercado Pago")
    print(f"   Shape bruto: {df_raw.shape[0]} linhas x {df_raw.shape[1]} colunas")
    
    try:
        # 1. Extrair valores de totais (linha 2 = index 1)
        print("\n📊 ETAPA 1: Extraindo totais...")
        linha_totais = df_raw.iloc[1]
        
        # Coluna A = INITIAL_BALANCE, D = FINAL_BALANCE
        initial_balance_str = str(linha_totais.iloc[0]) if pd.notna(linha_totais.iloc[0]) else "0"
        final_balance_str = str(linha_totais.iloc[3]) if len(linha_totais) > 3 and pd.notna(linha_totais.iloc[3]) else "0"
        
        initial_balance = converter_valor_br(initial_balance_str)
        final_balance = converter_valor_br(final_balance_str)
        
        print(f"   ✓ INITIAL_BALANCE: R$ {initial_balance:.2f}")
        print(f"   ✓ FINAL_BALANCE: R$ {final_balance:.2f}")
        
        # 2. Ler transações (começam na linha 5 = index 4, com headers na linha 4 = index 3)
        print("\n📊 ETAPA 2: Extraindo transações...")
        
        # Usar linha 4 como headers
        headers = df_raw.iloc[3].tolist()
        headers_clean = [str(h).strip() if pd.notna(h) else f'col_{i}' for i, h in enumerate(headers)]
        
        # Dados começam na linha 5
        df_transacoes = df_raw.iloc[4:].copy()
        df_transacoes.columns = headers_clean
        df_transacoes = df_transacoes.reset_index(drop=True)
        
        # Remover linhas completamente vazias
        df_transacoes = df_transacoes.dropna(how='all')
        
        print(f"   ✓ Headers: {headers_clean}")
        print(f"   ✓ Total de linhas: {len(df_transacoes)}")
        
        # 3. Mapear colunas
        col_data = headers_clean[0]  # RELEASE_DATE
        col_tipo = headers_clean[1]  # TRANSACTION_TYPE
        col_valor = headers_clean[3] if len(headers_clean) > 3 else headers_clean[-1]  # TRANSACTION_NET_AMOUNT
        
        print(f"   ✓ Coluna Data: '{col_data}'")
        print(f"   ✓ Coluna Tipo: '{col_tipo}'")
        print(f"   ✓ Coluna Valor: '{col_valor}'")
        
        # 4. Processar transações
        print("\n📊 ETAPA 3: Processando transações...")
        transacoes_processadas = []
        
        for idx, row in df_transacoes.iterrows():
            data_raw = row[col_data]
            tipo_raw = row[col_tipo]
            valor_raw = row[col_valor]
            
            # Pular linhas vazias
            if pd.isna(data_raw) or pd.isna(tipo_raw) or pd.isna(valor_raw):
                continue
            
            # Tratar Data: "01-10-2025" → "01/10/2025"
            try:
                data_str = str(data_raw).strip()
                data_str = data_str.replace('-', '/')  # Substitui hífen por barra
                data_final = data_str
            except:
                print(f"   ⚠️ Data inválida na linha {idx}: {data_raw}")
                continue
            
            # Lançamento = TRANSACTION_TYPE
            lancamento = str(tipo_raw).strip()
            
            # Converter valor
            valor = converter_valor_br(valor_raw)
            if pd.isna(valor):
                print(f"   ⚠️ Valor inválido na linha {idx}: {valor_raw}")
                continue
            
            transacoes_processadas.append({
                'data': data_final,
                'lançamento': lancamento,
                'valor (R$)': valor
            })
        
        df_final = pd.DataFrame(transacoes_processadas)
        
        print(f"\n   ✓ DataFrame final: {len(df_final)} transações processadas")
        
        # 5. VALIDAÇÃO
        print("\n📊 ETAPA 4: Validando integridade dos dados...")
        validacao = {
            'valido': False,
            'saldo_anterior': initial_balance,
            'soma_transacoes': 0.0,
            'saldo_calculado': 0.0,
            'saldo_final_arquivo': final_balance,
            'diferenca': 0.0,
            'mensagem': ''
        }
        
        if not pd.isna(initial_balance) and not pd.isna(final_balance):
            soma_transacoes = df_final['valor (R$)'].sum()
            saldo_calculado = initial_balance + soma_transacoes
            diferenca = saldo_calculado - final_balance
            
            validacao['soma_transacoes'] = soma_transacoes
            validacao['saldo_calculado'] = saldo_calculado
            validacao['diferenca'] = diferenca
            
            if abs(diferenca) <= 0.01:
                validacao['valido'] = True
                validacao['mensagem'] = "✅ Extrato validado: INITIAL_BALANCE + Σ Transações = FINAL_BALANCE"
                print(f"   ✅ Validação APROVADA")
                print(f"      INITIAL_BALANCE: R$ {initial_balance:.2f}")
                print(f"      Soma Transações: R$ {soma_transacoes:.2f}")
                print(f"      Saldo Calculado: R$ {saldo_calculado:.2f}")
                print(f"      FINAL_BALANCE: R$ {final_balance:.2f}")
                print(f"      Diferença: R$ {diferenca:.4f}")
            else:
                validacao['valido'] = False
                validacao['mensagem'] = f"❌ ERRO DE VALIDAÇÃO: Diferença de R$ {diferenca:.2f}"
                print(f"   ❌ Validação REPROVADA - Diferença: R$ {diferenca:.2f}")
        else:
            validacao['mensagem'] = "⚠️ Validação desabilitada (saldos não encontrados)"
            print("   ⚠️ Validação desabilitada")
        
        # 6. Informações extras
        validacao['total_transacoes'] = len(df_final)
        
        print(f"\n✅ Preprocessamento Mercado Pago concluído: {len(df_final)} transações")
        print(f"   Colunas finais: {list(df_final.columns)}")
        
        return df_final, validacao
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERRO ao preprocessar Mercado Pago: {e}")
        print(traceback.format_exc())
        raise
