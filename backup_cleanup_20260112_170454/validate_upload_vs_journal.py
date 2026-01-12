import sqlite3
from pathlib import Path

db_path = Path('app_dev/backend/database/financas_dev.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('\n=== VALIDAÇÃO: PREVIEW vs JOURNAL_ENTRIES ===\n')

# 1. Buscar sessão mais recente
cursor.execute("""
    SELECT DISTINCT session_id 
    FROM preview_transacoes 
    ORDER BY session_id DESC 
    LIMIT 1
""")
session = cursor.fetchone()
if not session:
    print('❌ Nenhuma sessão ativa no preview!')
    conn.close()
    exit(1)

session_id = session[0]
print(f'📋 Sessão analisada: {session_id}\n')

# 2. Buscar transações do preview
cursor.execute("""
    SELECT 
        data,
        lancamento,
        EstabelecimentoBase,
        ValorPositivo,
        IdTransacao,
        GRUPO,
        SUBGRUPO,
        origem_classificacao
    FROM preview_transacoes
    WHERE session_id = ?
    ORDER BY data, EstabelecimentoBase, ValorPositivo
""", (session_id,))

preview_transactions = cursor.fetchall()
print(f'📊 Total no preview: {len(preview_transactions)} transações\n')

# 3. Para cada transação, verificar se existe em journal_entries
matches_by_id = 0
matches_by_data = 0
not_found = 0

print('=' * 120)
print(f"{'Data':<12} | {'Estabelecimento':<25} | {'Valor':>10} | {'Status':<15} | {'IdTransacao'}")
print('=' * 120)

for data, lancamento, estab, valor, id_trans, grupo, subgrupo, origem in preview_transactions:
    # Buscar por IdTransacao
    cursor.execute("""
        SELECT IdTransacao, GRUPO, SUBGRUPO 
        FROM journal_entries 
        WHERE IdTransacao = ?
    """, (id_trans,))
    
    match_by_id = cursor.fetchone()
    
    if match_by_id:
        matches_by_id += 1
        status = '✅ ID Match'
        print(f'{data:<12} | {estab:<25} | R$ {valor:>7.2f} | {status:<15} | {id_trans}')
        if match_by_id[1] or match_by_id[2]:
            print(f'             | {"":25} | {"":10} | {"   Classificado:":<15} | {match_by_id[1] or "?"} > {match_by_id[2] or "?"}')
    else:
        # Buscar por Data+Estabelecimento+Valor
        cursor.execute("""
            SELECT IdTransacao, GRUPO, SUBGRUPO
            FROM journal_entries 
            WHERE Data = ? 
            AND Estabelecimento = ? 
            AND ValorPositivo = ?
        """, (data, estab, valor))
        
        match_by_data = cursor.fetchone()
        
        if match_by_data:
            matches_by_data += 1
            status = '⚠️ Data Match'
            print(f'{data:<12} | {estab:<25} | R$ {valor:>7.2f} | {status:<15} | {id_trans}')
            print(f'             | {"":25} | {"":10} | {"   ID diferente:":<15} | {match_by_data[0]}')
        else:
            not_found += 1
            status = '🆕 Nova'
            print(f'{data:<12} | {estab:<25} | R$ {valor:>7.2f} | {status:<15} | {id_trans}')

print('=' * 120)

# 4. Resumo
print('\n=== RESUMO DA VALIDAÇÃO ===\n')
print(f'Total analisadas:        {len(preview_transactions)}')
print(f'✅ Match por IdTransacao: {matches_by_id} ({matches_by_id/len(preview_transactions)*100:.1f}%)')
print(f'⚠️ Match por Data/Estab/Valor: {matches_by_data} ({matches_by_data/len(preview_transactions)*100:.1f}%)')
print(f'🆕 Novas (não duplicadas): {not_found} ({not_found/len(preview_transactions)*100:.1f}%)')

# 5. Validação do sistema
print('\n=== VALIDAÇÃO DO SISTEMA ===\n')
if matches_by_data > 0:
    print('⚠️ ATENÇÃO: Existem transações com mesmos dados mas IdTransacao diferente!')
    print('   Isso significa que o hash está sendo calculado de forma diferente.')
    print('   Possíveis causas:')
    print('   - Formato de data diferente')
    print('   - Normalização de estabelecimento diferente')
    print('   - Arredondamento de valor diferente')
    print('   - Lógica de row_number não aplicada no journal_entries original')
else:
    print('✅ Nenhuma inconsistência de hash detectada!')

if matches_by_id > 0:
    print(f'\n✅ Sistema de deduplicação funcionando!')
    print(f'   {matches_by_id} transações seriam corretamente bloqueadas.')
else:
    print(f'\n🆕 Todas as transações são novas!')
    print(f'   Nenhuma duplicata encontrada.')

# 6. Teste de duplicatas dentro do preview
cursor.execute("""
    SELECT 
        data || '|' || EstabelecimentoBase || '|' || ValorPositivo as chave,
        COUNT(*) as qtd,
        GROUP_CONCAT(IdTransacao, ', ') as ids
    FROM preview_transacoes
    WHERE session_id = ?
    GROUP BY chave
    HAVING qtd > 1
""", (session_id,))

duplicates_in_preview = cursor.fetchall()
if duplicates_in_preview:
    print(f'\n=== DUPLICATAS DENTRO DO PREVIEW ===\n')
    for chave, qtd, ids in duplicates_in_preview:
        print(f'Chave: {chave}')
        print(f'  Quantidade: {qtd}')
        print(f'  IDs únicos: {ids}')
        print()

conn.close()
