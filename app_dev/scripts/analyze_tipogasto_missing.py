#!/usr/bin/env python3
"""
TipoGasto Missing Analysis Script
Analisa transações sem TipoGasto preenchido e agrupa por GRUPO/SUBGRUPO

Versão: 1.0.0
Data: 03/01/2026
Autor: Sistema de Versionamento
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = 'financas.db'


def connect_db(db_path=DB_PATH):
    """Conecta ao banco de dados"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_path}")
    return sqlite3.connect(db_path)


def analyze_missing_tipogasto(cursor):
    """
    Analisa transações sem TipoGasto
    Retorna estatísticas detalhadas por GRUPO/SUBGRUPO
    """
    # Total de transações
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    total = cursor.fetchone()[0]
    
    if total == 0:
        return {
            'total': 0,
            'missing_tipogasto': 0,
            'missing_pct': 0,
            'by_grupo_subgrupo': [],
            'by_grupo_only': [],
            'no_classification': 0
        }
    
    # Transações sem TipoGasto
    cursor.execute("""
        SELECT COUNT(*)
        FROM journal_entries
        WHERE TipoGasto IS NULL OR TipoGasto = ''
    """)
    missing_tipogasto = cursor.fetchone()[0]
    missing_pct = (missing_tipogasto / total * 100) if total > 0 else 0
    
    # Agrupar por GRUPO + SUBGRUPO (ambos preenchidos)
    cursor.execute("""
        SELECT 
            GRUPO,
            SUBGRUPO,
            COUNT(*) as qtd,
            SUM(ValorPositivo) as valor_total,
            MIN(Data) as primeira_data,
            MAX(Data) as ultima_data
        FROM journal_entries
        WHERE (TipoGasto IS NULL OR TipoGasto = '')
            AND GRUPO IS NOT NULL 
            AND GRUPO != ''
            AND SUBGRUPO IS NOT NULL
            AND SUBGRUPO != ''
        GROUP BY GRUPO, SUBGRUPO
        ORDER BY qtd DESC
    """)
    by_grupo_subgrupo = cursor.fetchall()
    
    # Agrupar por GRUPO apenas (SUBGRUPO vazio)
    cursor.execute("""
        SELECT 
            GRUPO,
            COUNT(*) as qtd,
            SUM(ValorPositivo) as valor_total,
            MIN(Data) as primeira_data,
            MAX(Data) as ultima_data
        FROM journal_entries
        WHERE (TipoGasto IS NULL OR TipoGasto = '')
            AND GRUPO IS NOT NULL 
            AND GRUPO != ''
            AND (SUBGRUPO IS NULL OR SUBGRUPO = '')
        GROUP BY GRUPO
        ORDER BY qtd DESC
    """)
    by_grupo_only = cursor.fetchall()
    
    # Transações sem nenhuma classificação
    cursor.execute("""
        SELECT COUNT(*)
        FROM journal_entries
        WHERE (TipoGasto IS NULL OR TipoGasto = '')
            AND (GRUPO IS NULL OR GRUPO = '')
            AND (SUBGRUPO IS NULL OR SUBGRUPO = '')
    """)
    no_classification = cursor.fetchone()[0]
    
    # Exemplos de transações sem classificação
    cursor.execute("""
        SELECT 
            id,
            Data,
            Estabelecimento,
            Valor,
            origem,
            banco
        FROM journal_entries
        WHERE (TipoGasto IS NULL OR TipoGasto = '')
            AND (GRUPO IS NULL OR GRUPO = '')
            AND (SUBGRUPO IS NULL OR SUBGRUPO = '')
        LIMIT 10
    """)
    no_classification_examples = cursor.fetchall()
    
    return {
        'total': total,
        'missing_tipogasto': missing_tipogasto,
        'missing_pct': missing_pct,
        'by_grupo_subgrupo': by_grupo_subgrupo,
        'by_grupo_only': by_grupo_only,
        'no_classification': no_classification,
        'no_classification_examples': no_classification_examples
    }


def check_base_marcacoes(cursor, grupo, subgrupo):
    """
    Verifica se combinação GRUPO/SUBGRUPO existe em base_marcacoes
    Retorna o TipoGasto correspondente
    """
    cursor.execute("""
        SELECT TipoGasto
        FROM base_marcacoes
        WHERE GRUPO = ? AND SUBGRUPO = ?
    """, (grupo, subgrupo))
    
    result = cursor.fetchone()
    return result[0] if result else None


def generate_tipogasto_report(cursor, db_path='financas.db'):
    """Gera relatório de TipoGasto missing"""
    report_lines = []
    
    report_lines.append("=" * 100)
    report_lines.append("📊 ANÁLISE DE TIPOGASTO MISSING")
    report_lines.append("=" * 100)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Database: {db_path}")
    report_lines.append("")
    
    results = analyze_missing_tipogasto(cursor)
    
    if results['total'] == 0:
        report_lines.append("⚠️  Banco de dados vazio - nenhuma transação encontrada")
        report_lines.append("")
        return '\n'.join(report_lines)
    
    # Estatísticas gerais
    report_lines.append("📈 ESTATÍSTICAS GERAIS")
    report_lines.append("-" * 100)
    report_lines.append(f"Total de Transações: {results['total']:,}")
    report_lines.append(f"Transações sem TipoGasto: {results['missing_tipogasto']:,} ({results['missing_pct']:.2f}%)")
    report_lines.append(f"Transações completamente sem classificação: {results['no_classification']:,}")
    report_lines.append("")
    
    # Transações com GRUPO + SUBGRUPO mas sem TipoGasto
    if results['by_grupo_subgrupo']:
        report_lines.append("📋 TRANSAÇÕES COM GRUPO + SUBGRUPO (mas sem TipoGasto)")
        report_lines.append("-" * 100)
        report_lines.append(f"{'GRUPO':<30} {'SUBGRUPO':<30} {'QTD':>8} {'VALOR TOTAL':>15} {'PERÍODO':<25} {'TipoGasto sugerido':<20}")
        report_lines.append("-" * 100)
        
        total_items = 0
        for grupo, subgrupo, qtd, valor_total, primeira, ultima in results['by_grupo_subgrupo']:
            total_items += qtd
            
            # Verificar se existe em base_marcacoes
            tipogasto_sugerido = check_base_marcacoes(cursor, grupo, subgrupo)
            sugerido_str = tipogasto_sugerido if tipogasto_sugerido else "⚠️  NÃO EXISTE"
            
            valor_str = f"R$ {valor_total:,.2f}" if valor_total else "R$ 0.00"
            periodo = f"{primeira} a {ultima}" if primeira and ultima else "N/A"
            
            report_lines.append(
                f"{grupo:<30} {subgrupo:<30} {qtd:>8,} {valor_str:>15} {periodo:<25} {sugerido_str:<20}"
            )
        
        report_lines.append("-" * 100)
        report_lines.append(f"TOTAL: {total_items:,} transações")
        report_lines.append("")
    
    # Transações com GRUPO apenas (sem SUBGRUPO)
    if results['by_grupo_only']:
        report_lines.append("📋 TRANSAÇÕES COM GRUPO APENAS (sem SUBGRUPO nem TipoGasto)")
        report_lines.append("-" * 100)
        report_lines.append(f"{'GRUPO':<40} {'QTD':>8} {'VALOR TOTAL':>15} {'PERÍODO':<25}")
        report_lines.append("-" * 100)
        
        total_items = 0
        for grupo, qtd, valor_total, primeira, ultima in results['by_grupo_only']:
            total_items += qtd
            valor_str = f"R$ {valor_total:,.2f}" if valor_total else "R$ 0.00"
            periodo = f"{primeira} a {ultima}" if primeira and ultima else "N/A"
            
            report_lines.append(
                f"{grupo:<40} {qtd:>8,} {valor_str:>15} {periodo:<25}"
            )
        
        report_lines.append("-" * 100)
        report_lines.append(f"TOTAL: {total_items:,} transações")
        report_lines.append("")
    
    # Transações completamente sem classificação
    if results['no_classification'] > 0:
        report_lines.append("⚠️  TRANSAÇÕES COMPLETAMENTE SEM CLASSIFICAÇÃO")
        report_lines.append("-" * 100)
        report_lines.append(f"Total: {results['no_classification']:,} transações")
        report_lines.append("")
        
        if results['no_classification_examples']:
            report_lines.append("Exemplos (primeiros 10):")
            report_lines.append(f"{'ID':<8} {'DATA':<12} {'ESTABELECIMENTO':<40} {'VALOR':>12} {'ORIGEM':<15} {'BANCO':<10}")
            report_lines.append("-" * 100)
            
            for row in results['no_classification_examples']:
                row_id, data, estab, valor, origem, banco = row
                estab_str = (estab[:37] + '...') if estab and len(estab) > 40 else (estab or 'N/A')
                valor_str = f"R$ {valor:,.2f}" if valor else "R$ 0.00"
                origem_str = origem or 'N/A'
                banco_str = banco or 'N/A'
                
                report_lines.append(
                    f"{row_id:<8} {data or 'N/A':<12} {estab_str:<40} {valor_str:>12} {origem_str:<15} {banco_str:<10}"
                )
            report_lines.append("")
    
    # Resumo e recomendações
    report_lines.append("=" * 100)
    report_lines.append("💡 RECOMENDAÇÕES")
    report_lines.append("=" * 100)
    
    if results['missing_tipogasto'] == 0:
        report_lines.append("✅ Todas as transações têm TipoGasto preenchido!")
    else:
        report_lines.append("📝 Ações Recomendadas:")
        report_lines.append("")
        
        if results['by_grupo_subgrupo']:
            # Contar quantos têm sugestão em base_marcacoes
            com_sugestao = 0
            sem_sugestao = 0
            
            for grupo, subgrupo, qtd, *_ in results['by_grupo_subgrupo']:
                tipogasto = check_base_marcacoes(cursor, grupo, subgrupo)
                if tipogasto:
                    com_sugestao += qtd
                else:
                    sem_sugestao += qtd
            
            report_lines.append(f"1. BACKFILL VIA BASE_MARCACOES ({com_sugestao:,} transações):")
            report_lines.append("   - Executar UPDATE em journal_entries usando base_marcacoes")
            report_lines.append("   - Script SQL sugerido:")
            report_lines.append("     ```sql")
            report_lines.append("     UPDATE journal_entries")
            report_lines.append("     SET TipoGasto = (")
            report_lines.append("         SELECT TipoGasto FROM base_marcacoes")
            report_lines.append("         WHERE base_marcacoes.GRUPO = journal_entries.GRUPO")
            report_lines.append("         AND base_marcacoes.SUBGRUPO = journal_entries.SUBGRUPO")
            report_lines.append("     )")
            report_lines.append("     WHERE (TipoGasto IS NULL OR TipoGasto = '')")
            report_lines.append("       AND GRUPO IS NOT NULL AND SUBGRUPO IS NOT NULL;")
            report_lines.append("     ```")
            report_lines.append("")
            
            if sem_sugestao > 0:
                report_lines.append(f"2. ADICIONAR EM BASE_MARCACOES ({sem_sugestao:,} transações):")
                report_lines.append("   - Combinações GRUPO/SUBGRUPO que NÃO existem em base_marcacoes")
                report_lines.append("   - Precisam ser cadastradas manualmente com TipoGasto apropriado")
                report_lines.append("")
        
        if results['by_grupo_only']:
            report_lines.append(f"3. PREENCHER SUBGRUPO ({sum(qtd for _, qtd, *_ in results['by_grupo_only']):,} transações):")
            report_lines.append("   - Transações têm GRUPO mas não SUBGRUPO")
            report_lines.append("   - Reclassificar manualmente ou via classificador automático")
            report_lines.append("")
        
        if results['no_classification'] > 0:
            report_lines.append(f"4. CLASSIFICAÇÃO COMPLETA ({results['no_classification']:,} transações):")
            report_lines.append("   - Executar classificador automático (app/utils/classificador.py)")
            report_lines.append("   - Revisar e classificar manualmente casos não resolvidos")
            report_lines.append("")
        
        # Estratégia de fallback
        report_lines.append("5. ESTRATÉGIA DE FALLBACK (valores padrão):")
        report_lines.append("   - Alimentação → 'Ajustável - Saídas'")
        report_lines.append("   - Transporte → 'Ajustável - Uber'")
        report_lines.append("   - Saúde, Educação, Moradia → 'Fixo'")
        report_lines.append("   - Lazer, Compras → 'Ajustável'")
        report_lines.append("   - Outros casos → 'Ajustável' (genérico)")
    
    report_lines.append("=" * 100)
    
    return '\n'.join(report_lines)


def main():
    """Executa análise e gera relatório"""
    import argparse
    
    global DB_PATH
    
    parser = argparse.ArgumentParser(description='Análise de TipoGasto Missing')
    parser.add_argument('--output', choices=['console', 'file'], default='console',
                        help='Output format (default: console)')
    parser.add_argument('--db', default=DB_PATH, help=f'Database path (default: {DB_PATH})')
    
    args = parser.parse_args()
    DB_PATH = args.db
    
    try:
        conn = connect_db(DB_PATH)
        cursor = conn.cursor()
        
        report_text = generate_tipogasto_report(cursor, DB_PATH)
        
        if args.output == 'console':
            print(report_text)
        elif args.output == 'file':
            output_file = f"tipogasto_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Relatório salvo em: {output_file}")
        
        conn.close()
        return 0
        
    except FileNotFoundError as e:
        print(str(e))
        return 1
    except Exception as e:
        print(f"❌ Erro ao analisar TipoGasto: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
