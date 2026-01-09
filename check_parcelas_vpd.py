import sqlite3

conn = sqlite3.connect('app_dev/backend/database/financas_dev.db')
cursor = conn.cursor()

print('\n=== PARCELAS VPD na base_parcelas ===\n')
cursor.execute("""
SELECT 
    id_parcela,
    estabelecimento_base,
    valor_parcela,
    qtd_parcelas,
    grupo_sugerido,
    subgrupo_sugerido,
    data_inicio,
    status
FROM base_parcelas
WHERE estabelecimento_base LIKE '%VPD%'
ORDER BY data_inicio DESC
LIMIT 5
""")

parcelas = cursor.fetchall()
if parcelas:
    for row in parcelas:
        id_parc, estab, valor, qtd, grupo, subgrupo, data_inicio, status = row
        print(f'IdParcela: {id_parc}')
        print(f'  Estabelecimento: {estab}')
        print(f'  Valor parcela: R$ {valor:.2f}')
        print(f'  Qtd parcelas: {qtd}')
        print(f'  Classificação: {grupo} > {subgrupo}')
        print(f'  Data início: {data_inicio}')
        print(f'  Status: {status}')
        print()
else:
    print('❌ Nenhuma parcela VPD na base_parcelas')

# Ver se o texto do lançamento contém padrão de parcela
print('\n=== ANÁLISE DO TEXTO ===\n')
print('Lançamento: "EBN    *VPD TRAVEL09/10"')
print('Padrão esperado: XX/YY no final')
print('Detectado: 09/10')
print('✅ Deveria gerar IdParcela!')

# Ver se há outras parcelas no formato similar
print('\n\n=== PARCELAS 09/10 ou 10/10 na base_parcelas ===\n')
cursor.execute("""
SELECT 
    id_parcela,
    estabelecimento_base,
    valor_parcela,
    qtd_parcelas
FROM base_parcelas
WHERE qtd_parcelas = 10
ORDER BY data_inicio DESC
LIMIT 10
""")

parcelas_10x = cursor.fetchall()
if parcelas_10x:
    print(f'Encontradas {len(parcelas_10x)} parcelas com 10x:')
    for row in parcelas_10x:
        id_parc, estab, valor, qtd = row
        print(f'  {estab[:40]:40} | R$ {valor:>8.2f} | IdParcela: {id_parc[:20]}...')
else:
    print('❌ Nenhuma parcela 10x encontrada')

conn.close()
