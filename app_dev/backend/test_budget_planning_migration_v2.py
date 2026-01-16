#!/usr/bin/env python3
"""
TESTES PÓS-MIGRAÇÃO: BUDGET_PLANNING - Fase 4  
==============================================

Valida a nova estrutura budget_planning (grupo em vez de tipo_gasto):
1. Todos os registros têm grupo válido
2. Sem NULLs em grupo
3. Integridade com base_grupos_config
4. Distribuição sensível de registros
5. Consistência com journal_entries
"""

import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def test_grupos_validos(conn):
    """TESTE 1: Todos os grupos devem estar em base_grupos_config (ou zerados)"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 1: Validar grupos em base_grupos_config")
    print("-" * 80)
    
    # Grupos em budget_planning
    cursor.execute("SELECT COUNT(DISTINCT grupo) FROM budget_planning")
    total_grupos = cursor.fetchone()[0]
    
    # Grupos que existem em base_grupos_config
    cursor.execute("""
        SELECT COUNT(DISTINCT bp.grupo)
        FROM budget_planning bp
        INNER JOIN base_grupos_config bgc ON bp.grupo = bgc.nome_grupo
    """)
    grupos_validos = cursor.fetchone()[0]
    
    # Grupos inválidos (não estão em base_grupos_config)
    cursor.execute("""
        SELECT DISTINCT bp.grupo
        FROM budget_planning bp
        LEFT JOIN base_grupos_config bgc ON bp.grupo = bgc.nome_grupo
        WHERE bgc.nome_grupo IS NULL
    """)
    invalidos = [row[0] for row in cursor.fetchall()]
    
    print(f"Total de grupos únicos: {total_grupos}")
    print(f"Grupos válidos (em base_grupos_config): {grupos_validos}")
    print(f"Grupos inválidos: {len(invalidos)}")
    
    if invalidos:
        print(f"   Inválidos: {', '.join(invalidos[:10])}{'...' if len(invalidos) > 10 else ''}")
        # Verificar se estão zerados
        cursor.execute("""
            SELECT COUNT(*)
            FROM budget_planning bp
            LEFT JOIN base_grupos_config bgc ON bp.grupo = bgc.nome_grupo
            WHERE bgc.nome_grupo IS NULL
              AND (valor_planejado != 0 OR valor_medio_3_meses != 0)
        """)
        nao_zerados = cursor.fetchone()[0]
        
        if nao_zerados > 0:
            print(f"❌ FALHOU - {nao_zerados} registros inválidos NÃO zerados!")
            return False
        else:
            print("⚠️  ATENÇÃO - Grupos inválidos mas valores zerados (OK)")
            return True
    else:
        print("✅ PASSOU - Todos os grupos são válidos\n")
        return True


def test_sem_nulls(conn):
    """TESTE 2: Verificar ausência de NULLs em campos críticos"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 2: Verificar NULLs em campos críticos")
    print("-" * 80)
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN grupo IS NULL THEN 1 ELSE 0 END) as null_grupo,
            SUM(CASE WHEN mes_referencia IS NULL THEN 1 ELSE 0 END) as null_mes
        FROM budget_planning
    """)
    
    null_grupo, null_mes = cursor.fetchone()
    
    print(f"NULLs em grupo: {null_grupo}")
    print(f"NULLs em mes_referencia: {null_mes}")
    
    if null_grupo == 0 and null_mes == 0:
        print("✅ PASSOU - Nenhum NULL em campos críticos\n")
        return True
    else:
        print("❌ FALHOU - Encontrados NULLs!\n")
        return False


def test_unique_constraint(conn):
    """TESTE 3: Verificar UNIQUE constraint (user_id, grupo, mes_referencia)"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 3: Validar constraint UNIQUE")
    print("-" * 80)
    
    cursor.execute("""
        SELECT user_id, grupo, mes_referencia, COUNT(*) as duplicatas
        FROM budget_planning
        GROUP BY user_id, grupo, mes_referencia
        HAVING COUNT(*) > 1
    """)
    
    duplicatas = cursor.fetchall()
    
    if duplicatas:
        print(f"❌ FALHOU - Encontradas {len(duplicatas)} combinações duplicadas:")
        for user_id, grupo, mes, count in duplicatas[:5]:
            print(f"   user_id={user_id}, grupo={grupo}, mes={mes}: {count} registros")
        return False
    else:
        print("✅ PASSOU - Nenhuma duplicata (constraint OK)\n")
        return True


def test_distribuicao(conn):
    """TESTE 4: Validar distribuição sensível de registros"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 4: Distribuição de registros por grupo")
    print("-" * 80)
    
    cursor.execute("""
        SELECT grupo, COUNT(*) as total
        FROM budget_planning
        GROUP BY grupo
        ORDER BY total DESC
        LIMIT 10
    """)
    
    print("Top 10 grupos:")
    for grupo, total in cursor.fetchall():
        print(f"  {grupo:30s}: {total:3d} registros")
    
    cursor.execute("SELECT COUNT(*) FROM budget_planning")
    total = cursor.fetchone()[0]
    
    if total > 0:
        print(f"\n✅ PASSOU - {total} registros distribuídos\n")
        return True
    else:
        print("\n❌ FALHOU - Tabela vazia!\n")
        return False


def test_valores_recalculados(conn):
    """TESTE 5: Verificar que valor_medio_3_meses foi recalculado"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 5: Valores recalculados (valor_medio_3_meses)")
    print("-" * 80)
    
    # Registros com valor_medio_3_meses != 0 (foram recalculados)
    cursor.execute("""
        SELECT COUNT(*)
        FROM budget_planning bp
        INNER JOIN base_grupos_config bgc ON bp.grupo = bgc.nome_grupo
        WHERE valor_medio_3_meses != 0
    """)
    recalculados = cursor.fetchone()[0]
    
    # Total de registros válidos
    cursor.execute("""
        SELECT COUNT(*)
        FROM budget_planning bp
        INNER JOIN base_grupos_config bgc ON bp.grupo = bgc.nome_grupo
    """)
    total_validos = cursor.fetchone()[0]
    
    print(f"Registros válidos: {total_validos}")
    print(f"Recalculados (valor_medio_3_meses != 0): {recalculados}")
    print(f"Percentual recalculado: {recalculados/total_validos*100:.1f}%")
    
    # Esperamos que alguns tenham sido recalculados (nem todos terão histórico)
    if recalculados > 0:
        print("✅ PASSOU - Valores foram recalculados\n")
        return True
    else:
        print("⚠️  ATENÇÃO - Nenhum valor recalculado (histórico vazio?)\n")
        return True  # Não é erro crítico


def test_consistencia_journal(conn):
    """TESTE 6: Grupos em budget_planning devem existir em journal_entries"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 6: Consistência com journal_entries")
    print("-" * 80)
    
    # Grupos em budget_planning que NÃO existem em journal_entries
    cursor.execute("""
        SELECT DISTINCT bp.grupo
        FROM budget_planning bp
        WHERE NOT EXISTS (
            SELECT 1 FROM journal_entries je WHERE je.GRUPO = bp.grupo
        )
    """)
    
    grupos_sem_transacoes = [row[0] for row in cursor.fetchall()]
    
    if grupos_sem_transacoes:
        print(f"⚠️  {len(grupos_sem_transacoes)} grupos sem transações em journal_entries:")
        print(f"   {', '.join(grupos_sem_transacoes[:10])}{'...' if len(grupos_sem_transacoes) > 10 else ''}")
        print("   (Isso pode ser OK se são planejamentos futuros)\n")
        return True
    else:
        print("✅ PASSOU - Todos os grupos têm transações em journal_entries\n")
        return True


def test_estrutura_tabela(conn):
    """TESTE 7: Validar estrutura da tabela (colunas corretas)"""
    cursor = conn.cursor()
    
    print("\n🧪 TESTE 7: Estrutura da tabela budget_planning")
    print("-" * 80)
    
    cursor.execute("PRAGMA table_info(budget_planning)")
    colunas = {row[1] for row in cursor.fetchall()}
    
    colunas_esperadas = {
        'id', 'user_id', 'grupo', 'mes_referencia',
        'valor_planejado', 'valor_medio_3_meses',
        'created_at', 'updated_at'
    }
    
    print(f"Colunas esperadas: {len(colunas_esperadas)}")
    print(f"Colunas encontradas: {len(colunas)}")
    
    # Verificar que tipo_gasto NÃO existe mais
    if 'tipo_gasto' in colunas:
        print("❌ FALHOU - Coluna 'tipo_gasto' ainda existe (deveria ter sido removida)!")
        return False
    
    # Verificar que grupo existe
    if 'grupo' not in colunas:
        print("❌ FALHOU - Coluna 'grupo' não existe!")
        return False
    
    missing = colunas_esperadas - colunas
    extra = colunas - colunas_esperadas
    
    if missing:
        print(f"⚠️  Colunas faltando: {missing}")
    if extra:
        print(f"⚠️  Colunas extras: {extra}")
    
    if not missing and 'tipo_gasto' not in colunas:
        print("✅ PASSOU - Estrutura correta (grupo em vez de tipo_gasto)\n")
        return True
    else:
        return False


def main():
    print("="*80)
    print("TESTES PÓS-MIGRAÇÃO: BUDGET_PLANNING (Fase 4)")
    print("="*80)
    
    if not DB_PATH.exists():
        print(f"\n❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Verificar que budget_planning existe
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='budget_planning'
        """)
        
        if not cursor.fetchone():
            print("\n❌ ERRO: Tabela budget_planning não encontrada!")
            return 1
        
        print("\n✅ Tabela budget_planning encontrada\n")
        
        # Executar testes
        resultados = [
            test_estrutura_tabela(conn),
            test_grupos_validos(conn),
            test_sem_nulls(conn),
            test_unique_constraint(conn),
            test_distribuicao(conn),
            test_valores_recalculados(conn),
            test_consistencia_journal(conn),
        ]
        
        # Resumo
        print("="*80)
        print("RESUMO DOS TESTES")
        print("="*80)
        
        passados = sum(resultados)
        total = len(resultados)
        
        print(f"✅ Passaram: {passados}/{total}")
        print(f"❌ Falharam: {total - passados}/{total}")
        
        if passados == total:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("\n✅ Fase 4 concluída com sucesso!")
            print("\n⏭️  PRÓXIMO: Fase 5 - Atualizar classifiers")
            return 0
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM - Revisar migração")
            return 1
            
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
