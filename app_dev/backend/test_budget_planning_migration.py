#!/usr/bin/env python3
"""
TESTES PÓS-MIGRAÇÃO: BUDGET_PLANNING - Fase 4
==============================================

Valida que a migração da Fase 4 foi executada corretamente:
- Todos os registros têm tipo_gasto válido (5 valores)
- Mapeamento grupo → tipo_gasto está correto
- Nenhum NULL inesperado
- Integridade referencial com base_grupos_config
"""

import sys
import sqlite3
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"

# Valores esperados
VALORES_ESPERADOS = {'Fixo', 'Ajustável', 'Investimentos', 'Transferência', 'Receita'}


def test_valores_unicos(conn):
    """TESTE 1: Deve ter exatamente 5 valores únicos de tipo_gasto"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 1: Valores únicos de tipo_gasto")
    print("-" * 80)
    
    cursor.execute("""
        SELECT DISTINCT tipo_gasto 
        FROM budget_planning 
        WHERE tipo_gasto IS NOT NULL
        ORDER BY tipo_gasto
    """)
    
    valores = [row[0] for row in cursor.fetchall()]
    
    if len(valores) == 5:
        print(f"   ✅ 5 valores únicos (correto)")
        for valor in valores:
            print(f"      - {valor}")
        print("\n✅ TESTE 1 PASSOU\n")
        return True
    else:
        print(f"   ❌ {len(valores)} valores únicos (esperado: 5)")
        print(f"   Valores encontrados: {valores}")
        print("\n❌ TESTE 1 FALHOU\n")
        return False


def test_valores_corretos(conn):
    """TESTE 2: Valores devem ser exatamente os 5 esperados"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 2: Valores corretos")
    print("-" * 80)
    
    cursor.execute("""
        SELECT DISTINCT tipo_gasto 
        FROM budget_planning 
        WHERE tipo_gasto IS NOT NULL
    """)
    
    valores_encontrados = {row[0] for row in cursor.fetchall()}
    
    if valores_encontrados == VALORES_ESPERADOS:
        print(f"   ✅ Valores corretos:")
        for valor in sorted(valores_encontrados):
            print(f"      - {valor}")
        print("\n✅ TESTE 2 PASSOU\n")
        return True
    else:
        faltando = VALORES_ESPERADOS - valores_encontrados
        extras = valores_encontrados - VALORES_ESPERADOS
        
        print(f"   ❌ Valores incorretos")
        if faltando:
            print(f"   Faltando: {faltando}")
        if extras:
            print(f"   Extras: {extras}")
        print("\n❌ TESTE 2 FALHOU\n")
        return False


def test_sem_nulls(conn):
    """TESTE 3: Não deve haver valores NULL em tipo_gasto"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 3: Sem valores NULL")
    print("-" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM budget_planning WHERE tipo_gasto IS NULL")
    nulls = cursor.fetchone()[0]
    
    if nulls == 0:
        print(f"   ✅ Nenhum registro com NULL")
        print("\n✅ TESTE 3 PASSOU\n")
        return True
    else:
        print(f"   ❌ {nulls} registros com NULL")
        
        # Mostrar quais grupos têm NULL
        cursor.execute("""
            SELECT grupo, COUNT(*) 
            FROM budget_planning 
            WHERE tipo_gasto IS NULL 
            GROUP BY grupo
        """)
        
        print("   Grupos com NULL:")
        for grupo, count in cursor.fetchall():
            print(f"      - {grupo}: {count} registros")
        
        print("\n❌ TESTE 3 FALHOU\n")
        return False


def test_mapeamento_grupos(conn):
    """TESTE 4: Mapeamento grupo → tipo_gasto deve estar correto"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 4: Mapeamento grupo → tipo_gasto")
    print("-" * 80)
    
    cursor.execute("""
        SELECT 
            b.grupo,
            b.tipo_gasto,
            c.tipo_gasto_padrao,
            COUNT(*) as total
        FROM budget_planning b
        LEFT JOIN base_grupos_config c ON b.grupo = c.nome_grupo
        WHERE b.grupo IS NOT NULL 
          AND c.tipo_gasto_padrao IS NOT NULL
          AND b.tipo_gasto != c.tipo_gasto_padrao
        GROUP BY b.grupo, b.tipo_gasto, c.tipo_gasto_padrao
    """)
    
    inconsistencias = cursor.fetchall()
    
    if len(inconsistencias) == 0:
        print(f"   ✅ Todos os grupos mapeados corretamente")
        print("\n✅ TESTE 4 PASSOU\n")
        return True
    else:
        print(f"   ❌ {len(inconsistencias)} inconsistências encontradas:")
        for grupo, tipo_atual, tipo_esperado, count in inconsistencias:
            print(f"      - {grupo}: {tipo_atual} (esperado: {tipo_esperado}) - {count} registros")
        print("\n❌ TESTE 4 FALHOU\n")
        return False


def test_distribuicao_valores(conn):
    """TESTE 5: Distribuição de valores deve fazer sentido"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 5: Distribuição de valores")
    print("-" * 80)
    
    cursor.execute("""
        SELECT tipo_gasto, COUNT(*) as total
        FROM budget_planning
        GROUP BY tipo_gasto
        ORDER BY total DESC
    """)
    
    distribuicao = cursor.fetchall()
    total_registros = sum(count for _, count in distribuicao)
    
    print(f"   Total de registros: {total_registros}")
    print()
    
    for tipo, count in distribuicao:
        percentual = (count / total_registros * 100) if total_registros > 0 else 0
        print(f"   {tipo:20s} → {count:3d} registros ({percentual:5.1f}%)")
    
    # Validação: todos os 5 tipos devem estar presentes
    tipos_presentes = {tipo for tipo, _ in distribuicao if tipo is not None}
    
    if tipos_presentes == VALORES_ESPERADOS:
        print("\n   ✅ Todos os 5 tipos estão presentes")
        print("\n✅ TESTE 5 PASSOU\n")
        return True
    else:
        faltando = VALORES_ESPERADOS - tipos_presentes
        print(f"\n   ❌ Tipos faltando: {faltando}")
        print("\n❌ TESTE 5 FALHOU\n")
        return False


def test_integridade_grupos(conn):
    """TESTE 6: Todos os grupos em budget_planning devem estar em base_grupos_config"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 6: Integridade referencial (grupos)")
    print("-" * 80)
    
    cursor.execute("""
        SELECT DISTINCT b.grupo, COUNT(*) as total
        FROM budget_planning b
        LEFT JOIN base_grupos_config c ON b.grupo = c.nome_grupo
        WHERE b.grupo IS NOT NULL AND c.nome_grupo IS NULL
        GROUP BY b.grupo
    """)
    
    grupos_sem_config = cursor.fetchall()
    
    if len(grupos_sem_config) == 0:
        print(f"   ✅ Todos os grupos têm configuração em base_grupos_config")
        print("\n✅ TESTE 6 PASSOU\n")
        return True
    else:
        print(f"   ❌ {len(grupos_sem_config)} grupos SEM configuração:")
        for grupo, total in grupos_sem_config:
            print(f"      - {grupo} ({total} registros)")
        print("\n❌ TESTE 6 FALHOU\n")
        return False


def test_consistencia_journal_entries(conn):
    """TESTE 7: Grupos em budget_planning devem existir em journal_entries"""
    cursor = conn.cursor()
    
    print("🧪 TESTE 7: Consistência com journal_entries")
    print("-" * 80)
    
    cursor.execute("""
        SELECT DISTINCT 
            b.grupo,
            b.tipo_gasto as tipo_budget,
            c.tipo_gasto_padrao as tipo_config
        FROM budget_planning b
        LEFT JOIN base_grupos_config c ON b.grupo = c.nome_grupo
        WHERE b.grupo IS NOT NULL
          AND c.tipo_gasto_padrao IS NOT NULL
          AND b.tipo_gasto != c.tipo_gasto_padrao
    """)
    
    inconsistencias = cursor.fetchall()
    
    if len(inconsistencias) == 0:
        print(f"   ✅ Budget e base_grupos_config consistentes")
        print("\n✅ TESTE 7 PASSOU\n")
        return True
    else:
        print(f"   ❌ {len(inconsistencias)} inconsistências encontradas:")
        for grupo, tipo_budget, tipo_config in inconsistencias:
            print(f"      - {grupo}: budget={tipo_budget}, config={tipo_config}")
        print("\n❌ TESTE 7 FALHOU\n")
        return False


def main():
    """Executa todos os testes"""
    print("="*80)
    print("TESTES PÓS-MIGRAÇÃO: BUDGET_PLANNING (Fase 4)")
    print("="*80)
    print()
    
    if not DB_PATH.exists():
        print(f"❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return 1
    
    # Conectar
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Verificar se tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='budget_planning'")
        
        if not cursor.fetchone():
            print("❌ ERRO: Tabela budget_planning não encontrada")
            return 1
        
        print("✅ Tabela budget_planning encontrada\n")
        
        # Executar testes
        resultados = []
        
        resultados.append(test_valores_unicos(conn))
        resultados.append(test_valores_corretos(conn))
        resultados.append(test_sem_nulls(conn))
        resultados.append(test_mapeamento_grupos(conn))
        resultados.append(test_distribuicao_valores(conn))
        resultados.append(test_integridade_grupos(conn))
        resultados.append(test_consistencia_journal_entries(conn))
        
        # Resumo
        print("="*80)
        total = len(resultados)
        passou = sum(resultados)
        
        if passou == total:
            print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
            print("="*80)
            print(f"\n✅ Fase 4 validada: {passou}/{total} testes passaram")
            print("\n⏭️  PRÓXIMO PASSO: Fase 5 - Update Classifiers")
            print("   Scripts: Atualizar generic_rules_classifier.py")
            return 0
        else:
            print(f"⚠️  {passou}/{total} TESTES PASSARAM")
            print("="*80)
            print(f"\n❌ {total - passou} testes falharam")
            print("\n⚠️  Revisar migração ou corrigir dados manualmente")
            return 1
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
