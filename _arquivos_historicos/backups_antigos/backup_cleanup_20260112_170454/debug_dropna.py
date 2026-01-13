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

print(f"Antes do dropna: {len(df)} linhas")
print("\nÚltimas 7 linhas ANTES do dropna:")
for i in range(max(0, len(df)-7), len(df)):
    row = df.iloc[i]
    data_ok = pd.notna(row['data'])
    lanc_ok = pd.notna(row['lançamento'])
    val_ok = pd.notna(row['valor (R$)'])
    print(f"  {i}: D={data_ok} L={lanc_ok} V={val_ok} | {row['data']} | {row['lançamento']} | {row['valor (R$)']}")

# AQUI É O PROBLEMA
df = df.dropna(subset=['data', 'lançamento', 'valor (R$)'])

print(f"\n\nDEPOIS do dropna: {len(df)} linhas")
print("\nÚltimas 5 linhas DEPOIS do dropna:")
for i in range(max(0, len(df)-5), len(df)):
    row = df.iloc[i]
    print(f"  {i}: {row['data']} | {row['lançamento']} | {row['valor (R$)']}")
