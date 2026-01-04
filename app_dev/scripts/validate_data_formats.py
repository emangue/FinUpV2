#!/usr/bin/env python3
"""
Data Format Validation Script
Valida formatos de dados no banco de dados (datas, valores, campos obrigatórios)

Versão: 1.0.0
Data: 03/01/2026
Autor: Sistema de Versionamento
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path
import re

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = 'financas.db'


def connect_db(db_path=DB_PATH):
    """Conecta ao banco de dados"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"❌ Banco de dados não encontrado: {db_path}")
    return sqlite3.connect(db_path)


def validate_date_format(date_str):
    """
    Valida formato DD/MM/AAAA
    Retorna: (is_valid, error_message)
    """
    if not date_str:
        return False, "Data vazia"
    
    # Regex para DD/MM/AAAA
    pattern = r'^\d{2}/\d{2}/\d{4}$'
    if not re.match(pattern, date_str):
        return False, f"Formato inválido (esperado DD/MM/AAAA): '{date_str}'"
    
    # Validar se é data real
    try:
        day, month, year = date_str.split('/')
        dt = datetime(int(year), int(month), int(day))
        
        # Validar ano razoável (1900-2100)
        if int(year) < 1900 or int(year) > 2100:
            return False, f"Ano inválido: {year}"
        
        return True, None
    except ValueError as e:
        return False, f"Data inválida: {str(e)}"


def validate_mesanoref_format(mesano_str):
    """
    Valida formato AAAAMM
    Retorna: (is_valid, error_message)
    """
    if not mesano_str:
        return True, None  # Campo opcional
    
    pattern = r'^\d{6}$'
    if not re.match(pattern, mesano_str):
        return False, f"Formato inválido (esperado AAAAMM): '{mesano_str}'"
    
    try:
        year = int(mesano_str[:4])
        month = int(mesano_str[4:])
        
        if year < 1900 or year > 2100:
            return False, f"Ano inválido em MesAnoRef: {year}"
        
        if month < 1 or month > 12:
            return False, f"Mês inválido em MesAnoRef: {month}"
        
        return True, None
    except ValueError:
        return False, f"MesAnoRef inválido: '{mesano_str}'"


def validate_data_consistency(data_str, ano, mesanoref):
    """
    Valida consistência entre Data, Ano e MesAnoRef
    NOTA: Data = data da COMPRA, MesAnoRef = mês de FATURAMENTO
    Podem ser diferentes legalmente (compra em dez, fatura em jan)
    Retorna: (is_valid, error_message)
    """
    # DESABILITADO: Esta validação foi removida pois Data e MesAnoRef
    # têm propósitos diferentes e não devem ser forçados a coincidir
    # Data = quando a transação aconteceu
    # MesAnoRef = quando foi faturada (pode ser mês seguinte)
    return True, None


def validate_tipogasto_values(cursor):
    """
    Valida se valores de TipoGasto estão na lista permitida
    Retorna: (invalid_count, invalid_values)
    """
    # Buscar valores válidos de BaseMarcacao
    cursor.execute("SELECT DISTINCT TipoGasto FROM base_marcacoes WHERE TipoGasto IS NOT NULL")
    valid_values = set(row[0] for row in cursor.fetchall())
    
    # Se não há valores válidos cadastrados, usar lista padrão
    if not valid_values:
        valid_values = {
            'Fixo',
            'Ajustável',
            'Ajustável - Saídas',
            'Ajustável - Viagens',
            'Ajustável - Delivery',
            'Ajustável - Supermercado',
            'Ajustável - Carro',
            'Ajustável - Uber',
            'Ajustável - Assinaturas',
            'Fatura'
        }
    
    # Buscar valores inválidos em journal_entries
    cursor.execute("""
        SELECT DISTINCT TipoGasto, COUNT(*) as count
        FROM journal_entries
        WHERE TipoGasto IS NOT NULL AND TipoGasto != ''
        GROUP BY TipoGasto
    """)
    
    invalid_values = {}
    for tipogasto, count in cursor.fetchall():
        if tipogasto not in valid_values:
            invalid_values[tipogasto] = count
    
    return sum(invalid_values.values()), invalid_values


def validate_journal_entries(cursor):
    """
    Valida formatos na tabela journal_entries
    Retorna: dict com estatísticas de erros
    """
    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    total = cursor.fetchone()[0]
    
    if total == 0:
        return {'total': 0, 'errors': []}
    
    print(f"🔍 Validando {total:,} transações...")
    
    errors = {
        'data_format': [],
        'data_lancamento_format': [],
        'mesanoref_format': [],
        'data_consistency': [],
        'valor_inconsistency': [],
        'missing_required': [],
        'tipogasto_invalid': []
    }
    
    # Validar campos obrigatórios
    required_fields = ['IdTransacao', 'Data', 'Estabelecimento', 'Valor', 'ValorPositivo', 'origem']
    
    for field in required_fields:
        cursor.execute(f"""
            SELECT id, {field}
            FROM journal_entries
            WHERE {field} IS NULL OR {field} = ''
            LIMIT 100
        """)
        results = cursor.fetchall()
        if results:
            errors['missing_required'].extend([
                {'id': row[0], 'field': field, 'value': row[1]}
                for row in results
            ])
    
    # Validar formato de Data
    cursor.execute("SELECT id, Data FROM journal_entries WHERE Data IS NOT NULL")
    for row_id, data in cursor.fetchall():
        is_valid, error_msg = validate_date_format(data)
        if not is_valid:
            errors['data_format'].append({'id': row_id, 'value': data, 'error': error_msg})
    
    # Validar formato de DataPostagem
    cursor.execute("SELECT id, DataPostagem FROM journal_entries WHERE DataPostagem IS NOT NULL AND DataPostagem != ''")
    for row_id, data_post in cursor.fetchall():
        is_valid, error_msg = validate_date_format(data_post)
        if not is_valid:
            errors['data_lancamento_format'].append({'id': row_id, 'value': data_post, 'error': error_msg})
    
    # Validar formato de MesAnoRef
    cursor.execute("SELECT id, DT_Fatura FROM journal_entries WHERE DT_Fatura IS NOT NULL AND DT_Fatura != ''")
    for row_id, dt_fatura in cursor.fetchall():
        is_valid, error_msg = validate_mesanoref_format(dt_fatura)
        if not is_valid:
            errors['mesanoref_format'].append({'id': row_id, 'value': dt_fatura, 'error': error_msg})
    
    # Validar consistência Data vs Ano vs DT_Fatura
    cursor.execute("SELECT id, Data, Ano, DT_Fatura FROM journal_entries WHERE Data IS NOT NULL")
    for row_id, data, ano, dt_fatura in cursor.fetchall():
        if validate_date_format(data)[0]:  # Só validar consistência se Data for válida
            is_valid, error_msg = validate_data_consistency(data, ano, dt_fatura)
            if not is_valid:
                errors['data_consistency'].append({
                    'id': row_id,
                    'Data': data,
                    'Ano': ano,
                    'MesAnoRef': dt_fatura,
                    'error': error_msg
                })
    
    # Validar inconsistências de valor
    cursor.execute("""
        SELECT id, Valor, ValorPositivo
        FROM journal_entries
        WHERE ABS(ABS(Valor) - ValorPositivo) > 0.01
        LIMIT 100
    """)
    for row_id, valor, valor_pos in cursor.fetchall():
        errors['valor_inconsistency'].append({
            'id': row_id,
            'Valor': valor,
            'ValorPositivo': valor_pos,
            'diff': abs(abs(valor) - valor_pos)
        })
    
    # Validar valores de TipoGasto
    invalid_count, invalid_values = validate_tipogasto_values(cursor)
    if invalid_count > 0:
        errors['tipogasto_invalid'] = invalid_values
    
    return {
        'total': total,
        'errors': errors
    }


def generate_validation_report(cursor, db_path='financas.db'):
    """Gera relatório completo de validação"""
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("🔍 DATA FORMAT VALIDATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Database: {db_path}")
    report_lines.append("")
    
    # Validar JournalEntry
    report_lines.append("💳 JOURNAL ENTRIES - Format Validation")
    report_lines.append("-" * 80)
    
    je_results = validate_journal_entries(cursor)
    
    if je_results['total'] == 0:
        report_lines.append("⚠️  Tabela vazia - sem dados para validar")
        report_lines.append("")
    else:
        total = je_results['total']
        errors = je_results['errors']
        
        # Campos obrigatórios faltando
        if errors['missing_required']:
            missing_count = len(errors['missing_required'])
            report_lines.append(f"❌ Campos Obrigatórios Faltando: {missing_count}")
            
            # Agrupar por campo
            by_field = {}
            for err in errors['missing_required']:
                field = err['field']
                by_field[field] = by_field.get(field, 0) + 1
            
            for field, count in by_field.items():
                report_lines.append(f"  - {field}: {count} registros")
            
            # Mostrar alguns exemplos
            report_lines.append("\n  Exemplos (primeiros 5):")
            for err in errors['missing_required'][:5]:
                report_lines.append(f"    ID {err['id']}: campo '{err['field']}' = {err['value']}")
            report_lines.append("")
        else:
            report_lines.append("✅ Campos Obrigatórios: OK")
        
        # Formato de Data
        if errors['data_format']:
            count = len(errors['data_format'])
            pct = (count / total * 100)
            report_lines.append(f"\n❌ Data (formato DD/MM/AAAA): {count} erros ({pct:.2f}%)")
            for err in errors['data_format'][:5]:
                report_lines.append(f"  - ID {err['id']}: {err['error']}")
            if count > 5:
                report_lines.append(f"  ... e mais {count - 5} erros")
        else:
            report_lines.append("\n✅ Data (formato DD/MM/AAAA): OK")
        
        # Formato de DataPostagem
        if errors['data_lancamento_format']:
            count = len(errors['data_lancamento_format'])
            report_lines.append(f"\n❌ DataPostagem (formato DD/MM/AAAA): {count} erros")
            for err in errors['data_lancamento_format'][:3]:
                report_lines.append(f"  - ID {err['id']}: {err['error']}")
        else:
            report_lines.append("\n✅ DataPostagem (formato DD/MM/AAAA): OK")
        
        # Formato de DT_Fatura
        if errors['mesanoref_format']:
            count = len(errors['mesanoref_format'])
            report_lines.append(f"\n❌ DT_Fatura (formato AAAAMM): {count} erros")
            for err in errors['mesanoref_format'][:3]:
                report_lines.append(f"  - ID {err['id']}: {err['error']}")
        else:
            report_lines.append("\n✅ DT_Fatura (formato AAAAMM): OK")
        
        # Consistência Data vs Ano vs DT_Fatura
        if errors['data_consistency']:
            count = len(errors['data_consistency'])
            pct = (count / total * 100)
            report_lines.append(f"\n⚠️  Consistência Data/Ano/DT_Fatura: {count} avisos ({pct:.2f}%)")
            for err in errors['data_consistency'][:3]:
                report_lines.append(f"  - ID {err['id']}: {err['error']}")
        else:
            report_lines.append("\n✅ Consistência Data/Ano/DT_Fatura: OK")
        
        # Inconsistências de valor
        if errors['valor_inconsistency']:
            count = len(errors['valor_inconsistency'])
            pct = (count / total * 100)
            report_lines.append(f"\n❌ Inconsistência Valor vs ValorPositivo: {count} erros ({pct:.2f}%)")
            for err in errors['valor_inconsistency'][:3]:
                report_lines.append(f"  - ID {err['id']}: Valor={err['Valor']:.2f}, ValorPositivo={err['ValorPositivo']:.2f} (diff={err['diff']:.2f})")
        else:
            report_lines.append("\n✅ Consistência Valor vs ValorPositivo: OK")
        
        # Valores inválidos de TipoGasto
        if errors['tipogasto_invalid']:
            total_invalid = sum(errors['tipogasto_invalid'].values())
            pct = (total_invalid / total * 100)
            report_lines.append(f"\n⚠️  TipoGasto com valores não padronizados: {total_invalid} ({pct:.2f}%)")
            for tipogasto, count in sorted(errors['tipogasto_invalid'].items(), key=lambda x: -x[1])[:10]:
                report_lines.append(f"  - '{tipogasto}': {count} registros")
        else:
            report_lines.append("\n✅ TipoGasto: Todos os valores são válidos")
        
        report_lines.append("")
    
    # Resumo
    report_lines.append("=" * 80)
    report_lines.append("📊 VALIDATION SUMMARY")
    report_lines.append("=" * 80)
    
    if je_results['total'] == 0:
        report_lines.append("⚠️  Banco de dados vazio - nenhuma transação para validar")
        score = 100
    else:
        total_errors = (
            len(je_results['errors']['missing_required']) +
            len(je_results['errors']['data_format']) +
            len(je_results['errors']['data_lancamento_format']) +
            len(je_results['errors']['mesanoref_format']) +
            len(je_results['errors']['data_consistency']) +
            len(je_results['errors']['valor_inconsistency'])
        )
        
        total_warnings = sum(je_results['errors']['tipogasto_invalid'].values()) if je_results['errors']['tipogasto_invalid'] else 0
        
        report_lines.append(f"Total Transações: {je_results['total']:,}")
        report_lines.append(f"Erros Críticos: {total_errors:,}")
        report_lines.append(f"Avisos: {total_warnings:,}")
        
        # Score de qualidade
        error_pct = (total_errors / je_results['total'] * 100) if je_results['total'] > 0 else 0
        warning_pct = (total_warnings / je_results['total'] * 100) if je_results['total'] > 0 else 0
        
        score = 100 - error_pct - (warning_pct * 0.5)
        score = max(0, min(100, score))
        
        report_lines.append(f"\n📊 Data Quality Score: {score:.1f}/100")
        
        if score >= 95:
            report_lines.append("✅ Dados em excelente qualidade!")
        elif score >= 80:
            report_lines.append("⚠️  Dados com qualidade boa, alguns ajustes recomendados")
        elif score >= 60:
            report_lines.append("🔶 Dados com problemas moderados - correção recomendada")
        else:
            report_lines.append("🚨 Dados com problemas graves - correção urgente necessária!")
    
    report_lines.append("=" * 80)
    
    return '\n'.join(report_lines), score


def main():
    """Executa validação e gera relatório"""
    import argparse
    
    global DB_PATH
    
    parser = argparse.ArgumentParser(description='Data Format Validation')
    parser.add_argument('--output', choices=['console', 'file'], default='console',
                        help='Output format (default: console)')
    parser.add_argument('--db', default=DB_PATH, help=f'Database path (default: {DB_PATH})')
    
    args = parser.parse_args()
    DB_PATH = args.db
    
    try:
        conn = connect_db(DB_PATH)
        cursor = conn.cursor()
        
        report_text, score = generate_validation_report(cursor, DB_PATH)
        
        if args.output == 'console':
            print(report_text)
        elif args.output == 'file':
            output_file = f"data_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"✅ Relatório salvo em: {output_file}")
        
        conn.close()
        
        # Exit code baseado no score
        if score < 60:
            return 2  # Critical
        elif score < 80:
            return 1  # Warning
        else:
            return 0  # OK
        
    except FileNotFoundError as e:
        print(str(e))
        return 3
    except Exception as e:
        print(f"❌ Erro ao validar dados: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == '__main__':
    sys.exit(main())
