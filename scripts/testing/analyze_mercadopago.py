#!/usr/bin/env python3
"""Análise detalhada do arquivo MercadoPago"""

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

# Ler MercadoPago
df = pd.read_excel('_arquivos_historicos/_csvs_historico/MP202504.xlsx', skiprows=2)

# Renomear colunas baseado na primeira linha válida
df.columns = ['date', 'transaction_type', 'reference_id', 'amount', 'balance']

# Remover primeira linha (cabeçalho duplicado)
df = df[1:].reset_index(drop=True)

print('🔍 ANÁLISE DO ARQUIVO MERCADOPAGO (MP202504.xlsx)\n')
print('='*100)

nao_classificadas = []
classificadas = []

for _, row in df.iterrows():
    if pd.isna(row['transaction_type']):
        continue
    
    transacao = str(row['transaction_type'])
    if transacao in ['nan', 'TRANSACTION_TYPE']:
        continue
    
    # Skip PIX/Transferências/Reservas internas
    transacao_upper = transacao.upper()
    if any(k in transacao_upper for k in ['PIX RECEBIDA', 'PIX ENVIADA', 'TRANSFERENCIA RECEBIDA', 'TRANSFERENCIA ENVIADA', 'DINHEIRO RESERVADO', 'DINHEIRO RETIRADO', 'RESERVA POR']):
        continue
    
    grupo, subgrupo = classify(transacao)
    if not grupo:
        nao_classificadas.append(transacao)
    else:
        classificadas.append((transacao, grupo, subgrupo))

# Mostrar não classificadas
print('\n❌ TRANSAÇÕES NÃO CLASSIFICADAS (sem PIX/transferências/reservas internas):\n')
counter = Counter(nao_classificadas)
for transacao, count in counter.most_common(30):
    print(f'  [{count}x] {transacao}')

print(f'\n\n✅ EXEMPLOS DE TRANSAÇÕES CLASSIFICADAS ({len(classificadas)} total):\n')
for transacao, grupo, subgrupo in classificadas[:20]:
    print(f'  {transacao[:60]:<60} → {grupo} > {subgrupo}')

if len(classificadas) > 20:
    print(f'  ... e mais {len(classificadas)-20} transações')

print(f'\n{"="*100}')
print(f'📊 RESUMO:')
print(f'  Total analisado (sem PIX/reservas): {len(nao_classificadas) + len(classificadas)}')
print(f'  ✅ Classificadas: {len(classificadas)} ({len(classificadas)/(len(nao_classificadas)+len(classificadas))*100:.1f}%)')
print(f'  ❌ Não classificadas: {len(nao_classificadas)}')
print('='*100)
