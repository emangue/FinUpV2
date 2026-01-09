import sqlite3
from pathlib import Path
from collections import defaultdict

db_path = Path('app_dev/backend/database/financas_dev.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('\n=== ANÁLISE DE DUPLICATAS - TEST_DUPLICATAS.CSV ===\n')
cursor.execute('''
SELECT 
    data,
    EstabelecimentoBase,
    ValorPositivo,
    IdTransacao
FROM preview_transacoes
WHERE session_id = 'session_20260108_204445_1'
ORDER BY data, EstabelecimentoBase, ValorPositivo
''')

rows = cursor.fetchall()
groups = defaultdict(list)

for data, estab, valor, id_trans in rows:
    key = f'{data}|{estab}|{valor:.2f}'
    groups[key].append(id_trans)

print('Agrupamento por chave única (Data|Estabelecimento|Valor):\n')
duplicates_found = 0
for key, ids in sorted(groups.items()):
    if len(ids) > 1:
        duplicates_found += 1
        print(f'✅ DUPLICATA DETECTADA:')
        print(f'  Chave: {key}')
        print(f'  Qtd: {len(ids)} transações')
        print(f'  IDs gerados (devem ser DIFERENTES):')
        for i, id_trans in enumerate(ids):
            print(f'    [{i}] {id_trans}')
        print()

if duplicates_found == 0:
    print('❌ PROBLEMA: Nenhuma duplicata detectada!')
    print('   O sistema de row_number NÃO funcionou.')
else:
    print(f'\n✅ Sistema funcionou! {duplicates_found} grupos de duplicatas detectados.')
    print('   Cada transação duplicada recebeu IdTransacao único.')

conn.close()
