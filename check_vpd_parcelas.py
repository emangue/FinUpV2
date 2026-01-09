import sqlite3

conn = sqlite3.connect('app_dev/backend/database/financas_dev.db')
cursor = conn.cursor()

print('\n=== VERIFICANDO TRANSAÇÕES VPD TRAVEL ===\n')

# Buscar no preview
cursor.execute("""
SELECT 
    data,
    lancamento,
    valor,
    IdTransacao,
    IdParcela,
    ParcelaAtual,
    TotalParcelas,
    TemParcela,
    GRUPO,
    SUBGRUPO,
    origem_classificacao
FROM preview_transacoes
WHERE session_id = 'session_20260108_205224_1'
AND lancamento LIKE '%VPD TRAVEL%'
ORDER BY valor DESC
""")

preview = cursor.fetchall()
print('📊 Preview (Upload atual):')
for row in preview:
    data, lanc, valor, id_trans, id_parc, parc_atual, total_parc, tem_parc, grupo, subgrupo, origem = row
    print(f'\nData: {data}')
    print(f'  Lançamento: {lanc}')
    print(f'  Valor: R$ {valor:.2f}')
    print(f'  IdTransacao: {id_trans}')
    print(f'  IdParcela: {id_parc}')
    print(f'  Parcela: {parc_atual}/{total_parc} (TemParcela={tem_parc})')
    print(f'  Classificação: {origem} -> {grupo} > {subgrupo}')

# Buscar na base_parcelas
print('\n\n📋 Base Parcelas (histórico):')
cursor.execute("""
SELECT 
    Data,
    Estabelecimento,
    Valor,
    id_parcela,
    ParcelaAtual,
    TotalParcelas,
    GRUPO,
    SUBGRUPO
FROM base_parcelas
WHERE Estabelecimento LIKE '%VPD%'
ORDER BY Data DESC
LIMIT 5
""")

base_parcelas = cursor.fetchall()
if base_parcelas:
    for row in base_parcelas:
        data, estab, valor, id_parc, parc_atual, total_parc, grupo, subgrupo = row
        print(f'\nData: {data}')
        print(f'  Estabelecimento: {estab}')
        print(f'  Valor: R$ {valor:.2f}')
        print(f'  IdParcela: {id_parc}')
        print(f'  Parcela: {parc_atual}/{total_parc}')
        print(f'  Classificação: {grupo} > {subgrupo}')
else:
    print('  ❌ Nenhuma parcela VPD encontrada na base_parcelas')

# Buscar no journal_entries
print('\n\n📚 Journal Entries (histórico):')
cursor.execute("""
SELECT 
    Data,
    Estabelecimento,
    Valor,
    IdParcela,
    GRUPO,
    SUBGRUPO
FROM journal_entries
WHERE Estabelecimento LIKE '%VPD%'
ORDER BY Data DESC
LIMIT 5
""")

journal = cursor.fetchall()
if journal:
    for row in journal:
        data, estab, valor, id_parc, grupo, subgrupo = row
        print(f'\nData: {data}')
        print(f'  Estabelecimento: {estab}')
        print(f'  Valor: R$ {valor:.2f}')
        print(f'  IdParcela: {id_parc}')
        print(f'  Classificação: {grupo} > {subgrupo}')
else:
    print('  ❌ Nenhuma transação VPD encontrada no journal_entries')

conn.close()
