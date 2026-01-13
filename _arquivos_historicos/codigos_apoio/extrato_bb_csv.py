"""
Preprocessador para Extrato Banco do Brasil (CSV)

Versão: 3.0.0
Data: 28/12/2025

Detecta e processa arquivos de extrato CSV do Banco do Brasil.

Formato esperado:
- Colunas: Data, Dependencia Origem, Histórico, Data do Balancete, Número do documento, Valor
- Primeira linha de dados: "Saldo Anterior" com valor inicial
- Última linha: "S A L D O" com saldo final
- Encoding: Latin-1 ou CP1252 (arquivo com corrupção UTF-8)
- Formato de data: DD/MM/YYYY
- Formato de valor: String com quotes "-38.27" (negativo = débito)

Exemplos de transações:
- Compra com Cartão - 02/01 13:02 AFONSO SCHM ST TEREZ
- Pix - Enviado - 03/01 18:00 Lojas Belian Moda Ltda
- BB Rende Fácil - Rende Facil (investimentos automáticos)
"""
import pandas as pd
import re
from datetime import datetime


def is_extrato_bb_csv(file_path):
    """
    Detecta se o arquivo é um extrato CSV do Banco do Brasil
    
    Critérios:
    - Extensão .csv
    - Tem coluna "Histórico" (mesmo com encoding corrompido: Hist�rico)
    - Primeira linha de dados contém "Saldo Anterior"
    - Última linha contém "S A L D O"
    """
    try:
        # Tentar múltiplos encodings
        for encoding in ['latin-1', 'cp1252', 'utf-8', 'iso-8859-1']:
            try:
                # Ler primeiras linhas
                df_test = pd.read_csv(file_path, encoding=encoding, nrows=5)
                
                # Verificar colunas características
                colunas = [col.lower() for col in df_test.columns]
                
                # Procura por "Histórico" (pode estar corrompido)
                historico_col = any('hist' in col for col in colunas)
                
                # Verifica "Saldo Anterior" na primeira linha
                if historico_col and len(df_test) > 0:
                    primeira_linha = df_test.iloc[0].to_string()
                    if 'saldo anterior' in primeira_linha.lower():
                        print(f"✅ Detectado: Extrato BB CSV (encoding: {encoding})")
                        return True
                        
            except Exception:
                continue
        
        return False
        
    except Exception as e:
        print(f"⚠️  Erro ao detectar extrato BB CSV: {e}")
        return False


def extrair_estabelecimento(historico):
    """
    Extrai nome do estabelecimento do campo Histórico
    
    Formatos:
    - "Compra com Cartão - 02/01 13:02 AFONSO SCHM ST TEREZ"
    - "Pix - Enviado - 03/01 18:00 Lojas Belian Moda Ltda"
    - "Pix Periódico - 06/01 Thereza Christina Teixei 006/999"
    - "BB Rende Fácil - Rende Facil"
    
    Retorna:
    - Nome do estabelecimento/beneficiário extraído
    """
    if pd.isna(historico):
        return "N/A"
    
    historico = str(historico).strip()
    
    # BB Rende Fácil (investimento automático)
    if 'rende f' in historico.lower() or 'rende facil' in historico.lower():
        return "BB Rende Fácil"
    
    # Compra com Cartão - DD/MM HH:MM ESTABELECIMENTO
    match = re.search(r'compra com cart.o.*\d{2}:\d{2}\s+(.+)', historico, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Pix - Enviado/Recebido - DD/MM HH:MM BENEFICIÁRIO
    match = re.search(r'pix.*\d{2}:\d{2}\s+(.+?)(?:\s+\d{3}/\d{3})?$', historico, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Pix Periódico - DD/MM BENEFICIÁRIO
    match = re.search(r'pix peri.dico.*\d{2}/\d{2}\s+(.+?)(?:\s+\d{3}/\d{3})?$', historico, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback: retorna tudo após o último hífen
    parts = historico.split(' - ')
    if len(parts) > 1:
        # Remove data/hora se presente no final
        estabelecimento = parts[-1].strip()
        estabelecimento = re.sub(r'\d{2}/\d{2}\s+\d{2}:\d{2}', '', estabelecimento).strip()
        return estabelecimento if estabelecimento else historico
    
    return historico


def processar_extrato_bb_csv(file_path):
    """
    Processa arquivo de extrato CSV do Banco do Brasil
    
    Retorna:
    {
        'df': DataFrame com transações processadas,
        'validacao': {
            'saldo_anterior': float,
            'saldo_final': float,
            'soma_transacoes': float,
            'valido': bool,
            'diferenca': float
        },
        'banco': 'Banco do Brasil',
        'tipodocumento': 'Extrato Bancário',
        'preprocessado': True
    }
    """
    print("\n📋 Processando Extrato Banco do Brasil (CSV)...")
    
    # Tentar múltiplos encodings
    df = None
    encoding_usado = None
    
    for encoding in ['latin-1', 'cp1252', 'utf-8', 'iso-8859-1']:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            encoding_usado = encoding
            print(f"✅ Arquivo lido com encoding: {encoding}")
            break
        except Exception:
            continue
    
    if df is None:
        raise Exception("Não foi possível ler o arquivo com nenhum encoding")
    
    # Normalizar nomes de colunas - remover caracteres corrompidos
    colunas_normalizadas = []
    for col in df.columns:
        col_limpa = col.strip()
        # Substituir caracteres corrompidos
        col_limpa = col_limpa.replace('�', 'o')
        col_limpa = col_limpa.replace('Histórico', 'Historico')
        col_limpa = col_limpa.replace('Hist�rico', 'Historico')
        col_limpa = col_limpa.replace('Número', 'Numero')
        col_limpa = col_limpa.replace('N�mero', 'Numero')
        colunas_normalizadas.append(col_limpa)
    
    df.columns = colunas_normalizadas
    print(f"📋 Colunas detectadas: {list(df.columns)}")
    
    # Identificar linha de saldo anterior
    primeira_linha = df.iloc[0]
    saldo_anterior = 0.0
    
    if 'saldo anterior' in str(primeira_linha.values).lower():
        try:
            # Coluna "Valor" tem o saldo anterior
            saldo_anterior = float(str(primeira_linha['Valor']).replace(',', '.'))
            print(f"💰 Saldo Anterior: R$ {saldo_anterior:,.2f}")
        except Exception as e:
            print(f"⚠️  Erro ao ler saldo anterior: {e}")
    
    # Remover primeira linha (Saldo Anterior)
    df = df.iloc[1:].copy()
    
    # Identificar e remover última linha (S A L D O)
    ultima_linha = df.iloc[-1]
    saldo_final = 0.0
    
    if 's a l d o' in str(ultima_linha.values).lower():
        try:
            saldo_final = float(str(ultima_linha['Valor']).replace(',', '.'))
            print(f"💰 Saldo Final: R$ {saldo_final:,.2f}")
        except Exception as e:
            print(f"⚠️  Erro ao ler saldo final: {e}")
        
        # Remover última linha
        df = df.iloc[:-1].copy()
    
    # Processar transações
    print(f"📊 Processando {len(df)} transações...")
    
    # Converter valores
    df['Valor'] = df['Valor'].astype(str).str.replace(',', '.').astype(float)
    
    # Extrair estabelecimento do histórico (usar nome normalizado)
    df['estabelecimento'] = df['Historico'].apply(extrair_estabelecimento)
    
    # Renomear colunas para formato padrão esperado pelo processador
    df = df.rename(columns={
        'Data': 'data',
        'Valor': 'valor (R$)',
        'Historico': 'lançamento'  # O processador espera 'lançamento'
    })
    
    # Manter descricao_original para referência
    df['descricao_original'] = df['lançamento'].copy()
    
    # Selecionar colunas relevantes
    df_final = df[['data', 'lançamento', 'valor (R$)', 'descricao_original']].copy()
    
    # Validação: saldo anterior + soma transações = saldo final
    soma_transacoes = df_final['valor (R$)'].sum()
    saldo_calculado = saldo_anterior + soma_transacoes
    diferenca = abs(saldo_calculado - saldo_final)
    valido = diferenca < 0.01  # Tolerância de 1 centavo
    
    # Mensagem de validação
    if valido:
        mensagem = f"✅ Validação OK - Diferença: R$ {diferenca:.2f}"
        print(f"✅ Validação: PASSOU (diferença: R$ {diferenca:.2f})")
    else:
        mensagem = f"⚠️ Validação falhou - Diferença: R$ {diferenca:.2f}"
        print(f"⚠️  Validação: FALHOU (diferença: R$ {diferenca:.2f})")
        print(f"   Saldo Anterior: R$ {saldo_anterior:.2f}")
        print(f"   Soma Transações: R$ {soma_transacoes:.2f}")
        print(f"   Saldo Calculado: R$ {saldo_calculado:.2f}")
        print(f"   Saldo Final Esperado: R$ {saldo_final:.2f}")
    
    validacao = {
        'saldo_anterior': saldo_anterior,
        'saldo_final': saldo_final,
        'soma_transacoes': soma_transacoes,
        'saldo_calculado': saldo_calculado,
        'valido': valido,
        'diferenca': diferenca,
        'mensagem': mensagem
    }
    
    return {
        'df': df_final,
        'validacao': validacao,
        'banco': 'Banco do Brasil',
        'tipodocumento': 'Extrato Bancário',
        'preprocessado': True
    }


# Exportar funções principais
__all__ = ['is_extrato_bb_csv', 'processar_extrato_bb_csv']
