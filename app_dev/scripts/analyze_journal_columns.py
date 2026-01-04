#!/usr/bin/env python3
"""
Análise Completa de Colunas - journal_entries
Analisa todas as colunas da tabela para validar necessidade e propor otimizações

Versão: 1.0.0
Data: 03/01/2026
"""

import sqlite3
import os
from datetime import datetime
from collections import Counter

DB_PATH = 'app/financas.db'

def connect_db():
    """Conecta ao banco de dados"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def analyze_column(cursor, col_name, col_type):
    """Analisa estatísticas de uma coluna"""
    stats = {
        'name': col_name,
        'type': col_type,
        'total': 0,
        'null_count': 0,
        'null_pct': 0,
        'unique_count': 0,
        'sample_values': [],
        'value_distribution': []
    }
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    stats['total'] = cursor.fetchone()[0]
    
    # Contagem de NULLs
    cursor.execute(f"SELECT COUNT(*) FROM journal_entries WHERE {col_name} IS NULL OR {col_name} = ''")
    stats['null_count'] = cursor.fetchone()[0]
    stats['null_pct'] = (stats['null_count'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    # Valores únicos
    cursor.execute(f"SELECT COUNT(DISTINCT {col_name}) FROM journal_entries WHERE {col_name} IS NOT NULL AND {col_name} != ''")
    stats['unique_count'] = cursor.fetchone()[0]
    
    # Sample de valores (primeiros 5 não-null)
    cursor.execute(f"SELECT DISTINCT {col_name} FROM journal_entries WHERE {col_name} IS NOT NULL AND {col_name} != '' LIMIT 5")
    stats['sample_values'] = [row[0] for row in cursor.fetchall()]
    
    # Distribuição de valores (top 10)
    cursor.execute(f"""
        SELECT {col_name}, COUNT(*) as count
        FROM journal_entries
        WHERE {col_name} IS NOT NULL AND {col_name} != ''
        GROUP BY {col_name}
        ORDER BY count DESC
        LIMIT 10
    """)
    stats['value_distribution'] = [(row[0], row[1]) for row in cursor.fetchall()]
    
    return stats

def analyze_origem_banco_relationship(cursor):
    """Analisa relação entre origem e banco"""
    cursor.execute("""
        SELECT origem, banco, COUNT(*) as count
        FROM journal_entries
        GROUP BY origem, banco
        ORDER BY origem, count DESC
    """)
    return cursor.fetchall()

def check_inconsistencies(cursor):
    """Verifica inconsistências nos dados"""
    issues = []
    
    # Itau vs Itaú
    cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE origem LIKE '%Itau%' OR origem LIKE '%Itaú%'")
    itau_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT origem, COUNT(*) FROM journal_entries WHERE origem LIKE '%Itau%' OR origem LIKE '%Itaú%' GROUP BY origem")
    itau_variants = cursor.fetchall()
    
    if len(itau_variants) > 1:
        issues.append({
            'type': 'inconsistent_naming',
            'column': 'origem',
            'description': f'Múltiplas variações de "Itaú": {itau_variants}',
            'total_affected': itau_count
        })
    
    # Origem com informações redundantes (ex: "Fatura - arquivo.csv")
    cursor.execute("SELECT origem FROM journal_entries WHERE origem LIKE '%-%' OR origem LIKE '%.%' GROUP BY origem")
    complex_origens = [row[0] for row in cursor.fetchall()]
    
    if complex_origens:
        issues.append({
            'type': 'complex_values',
            'column': 'origem',
            'description': 'Origem contém informações de arquivo',
            'examples': complex_origens[:5]
        })
    
    # Banco NULL mas origem preenchida
    cursor.execute("SELECT COUNT(*) FROM journal_entries WHERE banco IS NULL AND origem IS NOT NULL")
    banco_null = cursor.fetchone()[0]
    
    if banco_null > 0:
        issues.append({
            'type': 'missing_data',
            'column': 'banco',
            'description': f'{banco_null} registros sem banco mas com origem',
            'total_affected': banco_null
        })
    
    return issues

def generate_report(conn):
    """Gera relatório completo"""
    cursor = conn.cursor()
    
    # Schema
    cursor.execute("PRAGMA table_info(journal_entries)")
    columns = cursor.fetchall()
    
    report = []
    report.append("="*100)
    report.append("📊 ANÁLISE COMPLETA DE COLUNAS - journal_entries")
    report.append("="*100)
    report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    report.append(f"Database: {DB_PATH}")
    report.append("")
    
    # Total de transações
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    total = cursor.fetchone()[0]
    report.append(f"Total de transações: {total:,}")
    report.append("")
    
    # Análise coluna por coluna
    report.append("="*100)
    report.append("📋 ANÁLISE DETALHADA POR COLUNA")
    report.append("="*100)
    report.append("")
    
    for col in columns:
        col_id, col_name, col_type, notnull, default_val, pk = col
        
        # Pular ID (primary key)
        if col_name == 'id':
            continue
            
        stats = analyze_column(cursor, col_name, col_type)
        
        report.append(f"📌 {col_name.upper()}")
        report.append(f"   Tipo: {col_type}")
        report.append(f"   Obrigatório: {'Sim' if notnull == 1 else 'Não'}")
        report.append(f"   NULL/Vazio: {stats['null_count']:,} ({stats['null_pct']:.1f}%)")
        report.append(f"   Valores únicos: {stats['unique_count']:,}")
        
        if stats['sample_values']:
            report.append(f"   Exemplos: {', '.join(str(v)[:50] for v in stats['sample_values'][:3])}")
        
        if stats['value_distribution'] and stats['unique_count'] < 50:
            report.append(f"   Distribuição:")
            for val, count in stats['value_distribution'][:5]:
                val_str = str(val)[:50] if val else "(vazio)"
                report.append(f"      - {val_str}: {count:,} ({count/total*100:.1f}%)")
        
        report.append("")
    
    # Análise de relacionamento origem/banco
    report.append("="*100)
    report.append("🔗 RELACIONAMENTO ORIGEM x BANCO")
    report.append("="*100)
    report.append("")
    
    origem_banco = analyze_origem_banco_relationship(cursor)
    for origem, banco, count in origem_banco[:20]:
        origem_str = origem if origem else "(NULL)"
        banco_str = banco if banco else "(NULL)"
        report.append(f"   {origem_str:40} | {banco_str:20} | {count:,}")
    
    report.append("")
    
    # Inconsistências
    report.append("="*100)
    report.append("⚠️  INCONSISTÊNCIAS DETECTADAS")
    report.append("="*100)
    report.append("")
    
    issues = check_inconsistencies(cursor)
    for i, issue in enumerate(issues, 1):
        report.append(f"{i}. {issue['type'].upper()} - {issue['column']}")
        report.append(f"   {issue['description']}")
        if 'total_affected' in issue:
            report.append(f"   Registros afetados: {issue['total_affected']:,}")
        if 'examples' in issue:
            report.append(f"   Exemplos: {issue['examples']}")
        report.append("")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        conn = connect_db()
        report = generate_report(conn)
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"column_analysis_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n✅ Relatório salvo em: {filename}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
