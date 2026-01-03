#!/usr/bin/env python3
"""
Database Health Check Script
Analisa qualidade dos dados, integridade e gera relatório completo

Versão: 1.0.0
Data: 02/01/2026
Autor: Sistema de Deployment
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path para importar models
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = 'financas.db'


def connect_db(db_path=DB_PATH):
    """Conecta ao banco de dados"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_path}")
    return sqlite3.connect(db_path)


def analyze_table_structure(cursor, table_name):
    """Obtém estrutura da tabela"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()


def null_analysis(cursor, table_name, columns):
    """Analisa valores NULL por coluna"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    
    if total_rows == 0:
        return {}, total_rows
    
    null_stats = {}
    for col in columns:
        col_name = col[1]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL OR {col_name} = ''")
        null_count = cursor.fetchone()[0]
        null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0
        null_stats[col_name] = {
            'null_count': null_count, 
            'null_pct': round(null_pct, 2),
            'usable': null_pct < 100
        }
    
    return null_stats, total_rows


def analyze_journal_entries(cursor):
    """Análise profunda da tabela JournalEntry"""
    report = {}
    
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    report['total'] = cursor.fetchone()[0]
    
    if report['total'] == 0:
        return report
    
    # Transações por usuário
    cursor.execute("""
        SELECT user_id, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY user_id
        ORDER BY count DESC
    """)
    report['per_user'] = cursor.fetchall()
    
    # Transações por origem
    cursor.execute("""
        SELECT origem, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY origem
        ORDER BY count DESC
    """)
    report['per_origin'] = cursor.fetchall()
    
    # Transações por banco
    cursor.execute("""
        SELECT banco, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY banco
        ORDER BY count DESC
    """)
    report['per_banco'] = cursor.fetchall()
    
    # Classificações faltando
    cursor.execute("""
        SELECT COUNT(*) 
        FROM journal_entries 
        WHERE GRUPO IS NULL OR GRUPO = '' OR SUBGRUPO IS NULL OR SUBGRUPO = '' OR TipoGasto IS NULL OR TipoGasto = ''
    """)
    report['missing_classification'] = cursor.fetchone()[0]
    
    # Método de classificação
    cursor.execute("""
        SELECT forma_classificacao, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY forma_classificacao
        ORDER BY count DESC
    """)
    report['classification_method'] = cursor.fetchall()
    
    # Inconsistências de valor
    cursor.execute("""
        SELECT COUNT(*) 
        FROM journal_entries 
        WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01
    """)
    report['value_inconsistencies'] = cursor.fetchone()[0]
    
    # Transações com parcelas
    cursor.execute("""
        SELECT COUNT(*), COUNT(DISTINCT IdParcela)
        FROM journal_entries 
        WHERE IdParcela IS NOT NULL AND IdParcela != ''
    """)
    parcela_data = cursor.fetchone()
    report['with_parcela'] = parcela_data[0]
    report['unique_parcelas'] = parcela_data[1]
    
    # Distribuição por ano
    cursor.execute("""
        SELECT Ano, COUNT(*) as count 
        FROM journal_entries 
        GROUP BY Ano
        ORDER BY Ano DESC
    """)
    report['per_year'] = cursor.fetchall()
    
    return report


def analyze_base_parcelas(cursor):
    """Analisa tabela BaseParcelas"""
    report = {}
    
    cursor.execute("SELECT COUNT(*) FROM base_parcelas")
    report['total'] = cursor.fetchone()[0]
    
    if report['total'] == 0:
        return report
    
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM base_parcelas 
        GROUP BY status
    """)
    report['per_status'] = cursor.fetchall()
    
    # Contratos órfãos (sem transações correspondentes)
    cursor.execute("""
        SELECT COUNT(*)
        FROM base_parcelas bp
        WHERE NOT EXISTS (
            SELECT 1 FROM journal_entries je 
            WHERE je.IdParcela = bp.id_parcela
        )
    """)
    report['orphaned'] = cursor.fetchone()[0]
    
    # Contratos ativos mas completos
    cursor.execute("""
        SELECT COUNT(*)
        FROM base_parcelas
        WHERE status = 'ativo' AND qtd_pagas >= qtd_parcelas
    """)
    report['active_but_complete'] = cursor.fetchone()[0]
    
    return report


def analyze_base_padrao(cursor):
    """Analisa tabela BasePadrao"""
    report = {}
    
    cursor.execute("SELECT COUNT(*) FROM base_padroes")
    report['total'] = cursor.fetchone()[0]
    
    if report['total'] == 0:
        return report
    
    cursor.execute("""
        SELECT user_id, COUNT(*) as count 
        FROM base_padroes 
        GROUP BY user_id
        ORDER BY count DESC
    """)
    report['per_user'] = cursor.fetchall()
    
    cursor.execute("""
        SELECT confianca, COUNT(*) as count 
        FROM base_padroes 
        GROUP BY confianca
    """)
    report['per_confidence'] = cursor.fetchall()
    
    # Padrões com baixa contagem
    cursor.execute("""
        SELECT COUNT(*)
        FROM base_padroes
        WHERE contagem < 3
    """)
    report['low_count'] = cursor.fetchone()[0]
    
    return report


def analyze_users(cursor):
    """Analisa tabela User"""
    report = {}
    
    cursor.execute("SELECT COUNT(*) FROM users")
    report['total'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE ativo = 1")
    report['active'] = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role
    """)
    report['per_role'] = cursor.fetchall()
    
    return report


def generate_report(output_format='console'):
    """Gera relatório completo de saúde do banco"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        report_lines = []
        issues = {'critical': [], 'warning': [], 'info': []}
        
        # Cabeçalho
        report_lines.append("=" * 80)
        report_lines.append("📊 DATABASE HEALTH CHECK REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Database: {DB_PATH}")
        report_lines.append("")
        
        # Análise de usuários
        user_report = analyze_users(cursor)
        report_lines.append("👥 USERS")
        report_lines.append("-" * 80)
        report_lines.append(f"Total: {user_report['total']}")
        report_lines.append(f"Active: {user_report['active']}")
        report_lines.append(f"Roles: {user_report['per_role']}")
        report_lines.append("")
        
        if user_report['total'] == 0:
            issues['critical'].append("No users found in database")
        
        # Análise de transações
        je_report = analyze_journal_entries(cursor)
        report_lines.append("💳 JOURNAL ENTRIES (Transactions)")
        report_lines.append("-" * 80)
        report_lines.append(f"Total transactions: {je_report.get('total', 0):,}")
        
        if je_report.get('total', 0) > 0:
            report_lines.append(f"Missing classifications: {je_report.get('missing_classification', 0):,}")
            report_lines.append(f"Value inconsistencies: {je_report.get('value_inconsistencies', 0):,}")
            report_lines.append(f"Installment transactions: {je_report.get('with_parcela', 0):,}")
            report_lines.append(f"Unique parcela contracts: {je_report.get('unique_parcelas', 0):,}")
            
            report_lines.append("\nPer User:")
            for user_id, count in je_report.get('per_user', [])[:5]:
                pct = (count / je_report['total'] * 100) if je_report['total'] > 0 else 0
                report_lines.append(f"  User {user_id or 'NULL'}: {count:,} ({pct:.1f}%)")
            
            report_lines.append("\nPer Origin:")
            for origem, count in je_report.get('per_origin', []):
                pct = (count / je_report['total'] * 100) if je_report['total'] > 0 else 0
                report_lines.append(f"  {origem}: {count:,} ({pct:.1f}%)")
            
            report_lines.append("\nPer Year:")
            for year, count in je_report.get('per_year', []):
                report_lines.append(f"  {year}: {count:,}")
            
            # Issues
            if je_report.get('value_inconsistencies', 0) > 0:
                issues['critical'].append(f"Value inconsistencies: {je_report['value_inconsistencies']}")
            
            missing_pct = (je_report.get('missing_classification', 0) / je_report['total'] * 100) if je_report['total'] > 0 else 0
            if missing_pct > 10:
                issues['warning'].append(f"High percentage of unclassified transactions: {missing_pct:.1f}%")
            elif je_report.get('missing_classification', 0) > 0:
                issues['info'].append(f"Some unclassified transactions: {je_report['missing_classification']}")
        
        report_lines.append("")
        
        # Análise de parcelas
        bp_report = analyze_base_parcelas(cursor)
        report_lines.append("📦 BASE PARCELAS (Installment Contracts)")
        report_lines.append("-" * 80)
        report_lines.append(f"Total contracts: {bp_report.get('total', 0)}")
        
        if bp_report.get('total', 0) > 0:
            report_lines.append(f"Status: {bp_report.get('per_status', [])}")
            report_lines.append(f"Orphaned contracts: {bp_report.get('orphaned', 0)}")
            report_lines.append(f"Active but complete: {bp_report.get('active_but_complete', 0)}")
            
            if bp_report.get('orphaned', 0) > 0:
                issues['warning'].append(f"Orphaned parcela contracts: {bp_report['orphaned']}")
            
            if bp_report.get('active_but_complete', 0) > 0:
                issues['info'].append(f"Contracts needing status update: {bp_report['active_but_complete']}")
        
        report_lines.append("")
        
        # Análise de padrões
        pad_report = analyze_base_padrao(cursor)
        report_lines.append("🎯 BASE PADROES (Classification Patterns)")
        report_lines.append("-" * 80)
        report_lines.append(f"Total patterns: {pad_report.get('total', 0)}")
        
        if pad_report.get('total', 0) > 0:
            report_lines.append(f"Per User: {pad_report.get('per_user', [])}")
            report_lines.append(f"Confidence levels: {pad_report.get('per_confidence', [])}")
            report_lines.append(f"Low-count patterns (<3): {pad_report.get('low_count', 0)}")
            
            if pad_report.get('low_count', 0) > 10:
                issues['info'].append(f"Many low-confidence patterns: {pad_report['low_count']}")
        
        report_lines.append("")
        
        # Resumo de issues
        report_lines.append("=" * 80)
        report_lines.append("🎯 SUMMARY")
        report_lines.append("=" * 80)
        
        report_lines.append(f"🚨 Critical Issues: {len(issues['critical'])}")
        for issue in issues['critical']:
            report_lines.append(f"  - {issue}")
        
        report_lines.append(f"\n⚠️  Warning Issues: {len(issues['warning'])}")
        for issue in issues['warning']:
            report_lines.append(f"  - {issue}")
        
        report_lines.append(f"\nℹ️  Info: {len(issues['info'])}")
        for issue in issues['info']:
            report_lines.append(f"  - {issue}")
        
        report_lines.append("")
        
        # Score de saúde
        health_score = 100
        health_score -= len(issues['critical']) * 20
        health_score -= len(issues['warning']) * 5
        health_score = max(0, health_score)
        
        report_lines.append(f"📊 Database Health Score: {health_score}/100")
        
        if health_score >= 90:
            report_lines.append("✅ Database is in excellent condition!")
        elif health_score >= 70:
            report_lines.append("⚠️  Database has minor issues that should be addressed")
        elif health_score >= 50:
            report_lines.append("🔶 Database has significant issues requiring attention")
        else:
            report_lines.append("🚨 Database has critical issues - review immediately!")
        
        report_lines.append("=" * 80)
        
        conn.close()
        
        # Output
        report_text = '\n'.join(report_lines)
        
        if output_format == 'console':
            print(report_text)
        elif output_format == 'file':
            output_file = f"database_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Report saved to: {output_file}")
        
        # Exit code baseado no health score
        if health_score < 50:
            return 2  # Critical
        elif health_score < 70:
            return 1  # Warning
        else:
            return 0  # OK
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Health Check')
    parser.add_argument('--output', choices=['console', 'file'], default='console',
                        help='Output format (default: console)')
    parser.add_argument('--db', default=DB_PATH, help=f'Database path (default: {DB_PATH})')
    
    args = parser.parse_args()
    DB_PATH = args.db
    
    exit_code = generate_report(output_format=args.output)
    sys.exit(exit_code)
