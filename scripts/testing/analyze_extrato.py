#!/usr/bin/env python3
"""Análise detalhada do extrato bancário"""

import pandas as pd
import sqlite3
from collections import Counter

# Carregar regras
conn = sqlite3.connect('app_dev/backend/database/financas_dev.db')
cursor = conn.cursor()
cursor.execute('SELECT keywords, grupo, subgrupo FROM generic_classification_rules WHERE ativo = 1 ORDER BY prioridade DESC')
rules = [(r[0].upper().split(','), r[1], r[2]) for r in cursor.fetchall()]
conn.close()

def classify(estab):
    search = estab.upper()
    for keywords, grupo, subgrupo in rules:
        for kw in keywords:
            if kw.strip() in search:
                return grupo, subgrupo
    return None, None

# Ler extrato
df = pd.read_excel('_arquivos_historicos/_csvs_historico/Extrato Conta Corrente-221220252316.xls', 
                   skiprows=8, 
                   names=['data', 'lancamento', 'ag_origem', 'valor', 'saldo'])

print('🔍 ANÁLISE DO EXTRATO BANCÁRIO\n')
print('='*100)

nao_classificadas = []
classificadas = []

for _, row in df.iterrows():
    if pd.isna(row['lancamento']):
        continue
    
    lanc = str(row['lancamento'])
    if lanc in ['nan', 'lançamentos', 'LANÇAMENTOS', 'SALDO ANTERIOR']:
        continue
    
    # Skip PIX/Transferências
    lanc_upper = lanc.upper()
    if any(k in lanc_upper for k in ['PIX', 'TRANSFERENCIA', 'TRANSFERÊNCIA', 'TRANSF', 'TED', 'DOC', 'SALDO TOTAL']):
        continue
    
    grupo, subgrupo = classify(lanc)
    if not grupo:
        nao_classificadas.append(lanc)
    else:
        classificadas.append((lanc, grupo, subgrupo))

# Mostrar não classificadas
print('\n❌ TRANSAÇÕES NÃO CLASSIFICADAS (sem PIX/transferências):\n')
counter = Counter(nao_classificadas)
for lanc, count in counter.most_common(30):
    print(f'  [{count}x] {lanc}')

print(f'\n\n✅ EXEMPLOS DE TRANSAÇÕES CLASSIFICADAS ({len(classificadas)} total):\n')
for lanc, grupo, subgrupo in classificadas[:15]:
    print(f'  {lanc[:50]:<50} → {grupo} > {subgrupo}')

if len(classificadas) > 15:
    print(f'  ... e mais {len(classificadas)-15} transações')

print(f'\n{"="*100}')
print(f'📊 RESUMO:')
print(f'  Total analisado (sem PIX): {len(nao_classificadas) + len(classificadas)}')
print(f'  ✅ Classificadas: {len(classificadas)} ({len(classificadas)/(len(nao_classificadas)+len(classificadas))*100:.1f}%)')
print(f'  ❌ Não classificadas: {len(nao_classificadas)}')
print('='*100)
