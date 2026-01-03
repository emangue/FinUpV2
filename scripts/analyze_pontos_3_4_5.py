#!/usr/bin/env python3
"""
Análise detalhada para Pontos 4, 3 e 5
"""
import sqlite3

conn = sqlite3.connect('app/financas.db')
cursor = conn.cursor()

print('=' * 100)
print('PONTO 4: EXEMPLOS DE INCONSISTÊNCIA DATA/ANO/DT_FATURA')
print('=' * 100)

# Buscar exemplos com inconsistência
cursor.execute('''
    SELECT id, Data, Ano, DT_Fatura, Estabelecimento, Valor, origem
    FROM journal_entries
    WHERE Data LIKE '__/__/____'
      AND (
        Ano != CAST(substr(Data, 7, 4) AS INTEGER)
        OR
        (DT_Fatura IS NOT NULL AND 
         CAST(substr(DT_Fatura, 1, 4) AS INTEGER) != CAST(substr(Data, 7, 4) AS INTEGER))
      )
    LIMIT 10
''')

results = cursor.fetchall()

print(f'\nEncontrados {len(results)} exemplos:\n')
print(f"{'ID':<8} {'Data':<12} {'Ano':<6} {'DT_Fatura':<10} {'Valor':<12} {'Estabelecimento':<40} {'Origem':<20}")
print('-' * 100)

for row in results:
    id_val, data, ano, dt_fatura, estab, valor, origem = row
    estab_short = (estab[:37] + '...') if estab and len(estab) > 40 else (estab or 'N/A')
    origem_short = (origem[:17] + '...') if origem and len(origem) > 20 else (origem or 'N/A')
    valor_str = f'R$ {valor:>9.2f}'
    dt_str = dt_fatura or 'N/A'
    print(f'{id_val:<8} {data:<12} {ano:<6} {dt_str:<10} {valor_str:<12} {estab_short:<40} {origem_short:<20}')

# Analisar o que está causando
print('\n' + '=' * 100)
print('ANÁLISE DA INCONSISTÊNCIA:')
print('=' * 100)

for row in results[:3]:
    id_val, data, ano, dt_fatura, estab, valor, origem = row
    day, month, year = data.split('/')
    data_year = int(year)
    data_month = int(month)
    
    print(f'\nID {id_val}:')
    print(f'  Data: {data}')
    print(f'    → Ano extraído da Data: {data_year}')
    print(f'    → Mês extraído da Data: {data_month:02d}')
    print(f'  Ano armazenado: {ano}')
    
    if dt_fatura:
        dt_year = int(dt_fatura[:4])
        dt_month = int(dt_fatura[4:6])
        print(f'  DT_Fatura: {dt_fatura}')
        print(f'    → Ano: {dt_year}')
        print(f'    → Mês: {dt_month:02d}')
        
        if data_year != dt_year:
            print(f'  ❌ Ano da Data ({data_year}) != Ano do DT_Fatura ({dt_year})')
        
        month_diff = abs((data_year * 12 + data_month) - (dt_year * 12 + dt_month))
        if month_diff > 1:
            print(f'  ⚠️  Diferença de {month_diff} meses entre Data e DT_Fatura')

print('\n\n' + '=' * 100)
print('PONTOS 3 e 5: ANÁLISE DETALHADA DE TIPOGASTO')
print('=' * 100)

# Análise por tipo de transação
print('\n1. TRANSFERÊNCIAS ENTRE CONTAS (serão desconsideradas)')
print('-' * 100)
cursor.execute('''
    SELECT 
        GRUPO, 
        SUBGRUPO, 
        TipoGasto,
        COUNT(*) as qtd,
        SUM(ValorPositivo) as total
    FROM journal_entries
    WHERE GRUPO LIKE '%Transferência%' OR GRUPO LIKE '%transferência%'
    GROUP BY GRUPO, SUBGRUPO, TipoGasto
    ORDER BY qtd DESC
''')

for grupo, subgrupo, tipogasto, qtd, total in cursor.fetchall():
    tipogasto_str = tipogasto or '(NULL)'
    print(f'{grupo:<35} | {subgrupo:<20} | TipoGasto: {tipogasto_str:<25} | {qtd:>4} transações | R$ {total:>12,.2f}')

print('\n2. SALÁRIOS (receita, não gasto)')
print('-' * 100)
cursor.execute('''
    SELECT 
        GRUPO, 
        SUBGRUPO, 
        TipoGasto,
        COUNT(*) as qtd,
        SUM(ValorPositivo) as total
    FROM journal_entries
    WHERE GRUPO LIKE '%Salário%' OR GRUPO LIKE '%salário%'
    GROUP BY GRUPO, SUBGRUPO, TipoGasto
    ORDER BY qtd DESC
''')

for grupo, subgrupo, tipogasto, qtd, total in cursor.fetchall():
    tipogasto_str = tipogasto or '(NULL)'
    print(f'{grupo:<35} | {subgrupo:<20} | TipoGasto: {tipogasto_str:<25} | {qtd:>4} transações | R$ {total:>12,.2f}')

print('\n3. INVESTIMENTOS (aplicação, não gasto)')
print('-' * 100)
cursor.execute('''
    SELECT 
        GRUPO, 
        SUBGRUPO, 
        TipoGasto,
        COUNT(*) as qtd,
        SUM(ValorPositivo) as total
    FROM journal_entries
    WHERE GRUPO LIKE '%Investimento%'
    GROUP BY GRUPO, SUBGRUPO, TipoGasto
    ORDER BY qtd DESC
''')

for grupo, subgrupo, tipogasto, qtd, total in cursor.fetchall():
    tipogasto_str = tipogasto or '(NULL)'
    print(f'{grupo:<35} | {subgrupo:<20} | TipoGasto: {tipogasto_str:<25} | {qtd:>4} transações | R$ {total:>12,.2f}')

print('\n4. VALORES NÃO PADRONIZADOS (ponto 5)')
print('-' * 100)
cursor.execute('''
    SELECT 
        TipoGasto,
        GRUPO,
        SUBGRUPO,
        COUNT(*) as qtd
    FROM journal_entries
    WHERE TipoGasto IN ('Ajustável - Investimentos', 'Ignorar', 'Fatura', 'Ajustado')
    GROUP BY TipoGasto, GRUPO, SUBGRUPO
    ORDER BY TipoGasto, qtd DESC
''')

for tipogasto, grupo, subgrupo, qtd in cursor.fetchall():
    print(f'TipoGasto: {tipogasto:<30} | {grupo:<30} | {subgrupo:<20} | {qtd:>4} transações')

print('\n' + '=' * 100)
print('RESUMO DE TIPOS DE TRANSAÇÃO:')
print('=' * 100)
cursor.execute('''
    SELECT 
        TipoTransacao,
        COUNT(*) as qtd,
        SUM(ValorPositivo) as total
    FROM journal_entries
    GROUP BY TipoTransacao
    ORDER BY qtd DESC
''')

for tipo, qtd, total in cursor.fetchall():
    tipo_str = tipo or '(NULL)'
    print(f'{tipo_str:<30} | {qtd:>5} transações | R$ {total:>15,.2f}')

conn.close()
