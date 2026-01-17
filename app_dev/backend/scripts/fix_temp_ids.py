"""Corrige IdTransacao temporários (_temp_) com sequência correta"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from collections import defaultdict
from app.shared.utils import generate_id_transacao

db_path = Path(__file__).parent.parent / 'database' / 'financas_dev.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Buscar transações com _temp_
cursor.execute('''
    SELECT id, user_id, Data, Estabelecimento, Valor
    FROM journal_entries 
    WHERE IdTransacao LIKE '%_temp_%'
    ORDER BY Data, id
''')
temp_records = cursor.fetchall()

if not temp_records:
    print('✅ Nenhum registro temporário encontrado')
    conn.close()
    exit(0)

# Agrupar por (data, estabelecimento, valor) para calcular sequência
grupos = defaultdict(list)
for rec in temp_records:
    id_entry, user_id, data, estab, valor = rec
    chave = f'{data}|{estab.upper()}|{valor:.2f}'
    grupos[chave].append((id_entry, user_id, data, estab, valor))

print(f'Corrigindo {len(temp_records)} registros temporários:')
for chave, registros in grupos.items():
    for idx, (id_entry, user_id, data, estab, valor) in enumerate(registros, start=2):
        novo_id = generate_id_transacao(data, estab.upper(), valor, user_id, sequencia=idx)
        cursor.execute('''
            UPDATE journal_entries
            SET IdTransacao = ?
            WHERE id = ?
        ''', (novo_id, id_entry))
        print(f'  ID {id_entry}: sequência {idx} -> {novo_id}')

conn.commit()
conn.close()
print('✅ Todos os temporários corrigidos!')
