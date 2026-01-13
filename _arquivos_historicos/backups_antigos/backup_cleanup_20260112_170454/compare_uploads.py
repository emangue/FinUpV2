import sqlite3
from pathlib import Path
from collections import defaultdict

db_path = Path('app_dev/backend/database/financas_dev.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar os dois uploads
sessions = ['session_20260108_204445_1', 'session_20260108_204612_1']

print('\n=== COMPARAÇÃO DE CONSISTÊNCIA - MESMO ARQUIVO, 2 UPLOADS ===\n')

data_by_session = {}
for session_id in sessions:
    cursor.execute('''
    SELECT 
        data,
        EstabelecimentoBase,
        ValorPositivo,
        IdTransacao
    FROM preview_transacoes
    WHERE session_id = ?
    ORDER BY data, EstabelecimentoBase, ValorPositivo
    ''', (session_id,))
    
    rows = cursor.fetchall()
    data_by_session[session_id] = rows

# Comparar
session1_ids = [row[3] for row in data_by_session[sessions[0]]]
session2_ids = [row[3] for row in data_by_session[sessions[1]]]

print(f'Upload 1 ({sessions[0]}):')
for i, (data, estab, valor, id_trans) in enumerate(data_by_session[sessions[0]]):
    print(f'  [{i}] {data} | {estab:20} | {valor:>7.2f} | {id_trans}')

print(f'\nUpload 2 ({sessions[1]}):')
for i, (data, estab, valor, id_trans) in enumerate(data_by_session[sessions[1]]):
    print(f'  [{i}] {data} | {estab:20} | {valor:>7.2f} | {id_trans}')

print('\n=== VERIFICAÇÃO DE CONSISTÊNCIA ===\n')
if session1_ids == session2_ids:
    print('✅ PERFEITO! IdTransacao são IDÊNTICOS nos dois uploads!')
    print('   O sistema é DETERMINÍSTICO.')
    print('   Mesmo arquivo → Mesmos IDs → Deduplicação funcionará!')
else:
    print('❌ PROBLEMA! IdTransacao são DIFERENTES!')
    print('   O sistema NÃO é determinístico.')
    print('\nDiferenças:')
    for i in range(len(session1_ids)):
        if session1_ids[i] != session2_ids[i]:
            print(f'  Posição {i}: {session1_ids[i]} ≠ {session2_ids[i]}')

conn.close()
