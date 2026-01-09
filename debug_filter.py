#!/usr/bin/env python3
import pandas as pd

arquivo = '_csvs_historico/extrato_itau.xls'
df_raw = pd.read_excel(arquivo, header=None)

# Detectar cabeçalho
header_row = None
for i in range(min(20, len(df_raw))):
    row_str = ' '.join(str(val).lower() for val in df_raw.iloc[i].values if pd.notna(val))
    if 'data' in row_str and ('lancamento' in row_str or 'lançamento' in row_str) and 'valor' in row_str:
        header_row = i
        break

print(f"Cabeçalho na linha: {header_row}")

# Extrair dados
df = df_raw.iloc[header_row:].copy()
df.columns = df.iloc[0]
df = df[1:].reset_index(drop=True)
df.columns = df.columns.str.strip().str.lower()

# Pular linha decorativa
if len(df) > 0:
    first_row_str = ' '.join(str(val).lower() for val in df.iloc[0].values if pd.notna(val))
    if first_row_str.strip() == 'lançamentos':
        df = df[1:].reset_index(drop=True)

# Selecionar colunas
df = df.iloc[:, [0, 1, 3]].copy()
df.columns = ['data', 'lançamento', 'valor (R$)']

# Limpar
df = df.dropna(subset=['data', 'lançamento', 'valor (R$)'])

# Filtrar saldos
df = df[~df['lançamento'].str.upper().str.contains('SALDO', na=False)]

print(f"\nApós filtros iniciais: {len(df)} linhas")
print("\nÚltimas 5 linhas:")
for i in range(max(0, len(df)-5), len(df)):
    row = df.iloc[i]
    print(f"  {i}: {row['data']} | {row['lançamento']} | {row['valor (R$)']}")

print("\n\nProcurando 'SAÍDAS FUTURAS':")
for i in range(len(df)):
    lancamento_str = str(df.iloc[i]['lançamento']).strip()
    lancamento_upper = lancamento_str.upper()
    
    if 'SAÍDA' in lancamento_upper or 'SAIDA' in lancamento_upper:
        print(f"  Linha {i}: '{lancamento_str}' (upper: '{lancamento_upper}')")
        if 'FUTURA' in lancamento_upper:
            print(f"    ✅ MATCH! Contém FUTURA")
            print(f"    Removeria {len(df) - i} linhas")
            break
