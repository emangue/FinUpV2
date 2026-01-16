#!/usr/bin/env python3
"""
FASE 4: MIGRAÇÃO BUDGET_PLANNING - Adicionar GRUPO + Recalcular
================================================================

Este script migra budget_planning de tipo_gasto → grupo:
1. Adiciona coluna 'grupo' VARCHAR(100)
2. Mapeia tipo_gasto antigo → grupo (ex: "Ajustável - Carro" → "Carro")
3. Recalcula valor_medio_3_meses baseado em journal_entries por GRUPO
4. Atualiza tipo_gasto para 5 valores via base_grupos_config
5. Registros não mapeados → valor zerado
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("⚠️  Instalando python-dateutil...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
    from dateutil.relativedelta ilta

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def criar_backup():
    """Cria backup do banco antes da migração"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH.parent / f"financas_dev.db.backup_antes_fase4_{timestamp}"
    
    print(f"🔒 Criando backup: {backup_path.name}")
    shutil.copy2(DB_PATH, backup_path)
    
    backup_size = backup_path.stat().st_size / 1024 / 1024
    print(f"   ✅ Backup criado: {backup_size:.2f} MB")
    
    return backup_path


def validar_dependencias(conn):
    """Valida que fase 3 foi executada com sucesso"""
    cursor = conn.cursor()
    
    print("🔍 Validandoexcept .")
    
    cursor.execute("SELECT COUNT(DISTINCT TipoGasto) FROM journal_entries WHERE TipoGasto IS NOT NULL")
    tipos_journal = cursor.fetchone()[0]
    
    if tipos_journal == 5:
        print(f"   ✅ journal_entries OK (5 valores de TipoGasto)")
    else:
        print(f"   ⚠️  journal_entries tem {tipos_journal} valores (esperado: 5)")
        return False
    
    cursor.execute("SELECT COUNT(*) FROM budget_planning")
    total_budget = cursor.fetchone()[0]
    
    if total_budget == 0:
        print(f"   ⚠️  budget_planning está vazio (0 registros)")
        return False
    else:
        print(f"   ✅ budget_planning OK ({total_budget} registros)")
    
    cursor.execute("PRAGMA table_info(budget_planning)")
    colunas = [row[1] for row in cursor.fetchall()]
    
    if 'grupo' in colunas:
        print(f"   ⚠️  Coluna 'grupo' já e    """Valida que fase 3 foi e Migração já foi executada")
        return False
    else:
        print(f"   ✅ Coluna 'grupo' não existe (pronto para migração)")
    
    return True


def mapear_tipo_gasto_para_grupo(tipo_gasto_antigo):
    """Mapeia tipo_gasto antigo → grupo"""
    if not tipo_gasto_antigo:
        return None
    
    mapeamentos = {
        'Pagamento Fatura': 'Fatura',
        'Débito': 'Transferência Entre Contas',
        'Fixo': 'Moradia',
        'Ajustável': 'Outros',
        'Ajustavel - Casa': 'Casa',
    }
    
    if tipo_gasto_antigo in mapeamentos:
        return mapeamentos[tipo_gasto_antigo]
    
    if ' - ' in tipo_gasto_antigo:
        partes = tipo_gasto_antigo.split(' - ', 1)
        return partes[1]
    
    return None


def recalcular_media_3_meses(conn, user_id, grupo,    colunas = [row[1] for row in cursor.fetchall( em journal_entries dos últimos 3 meses"""
    cursor = conn.cursor()
    
    ano_ref, mes_ref = map(int, mes_referencia.split('-'))
    
    data_ref = datetime(ano_ref, mes_ref, 1)
    data_inicio = data_ref - relativedelta(months=3)
    data_fim = data_ref
    
    cursor.execute("""
        SELECT COALESCE(SUM(ABS(Valor)), 0) / 3.0 as media
        FROM journal_entries
        WHERE user_id = ?
          AND GRUPO = ?
          AND Ano * 100 + Mes >= ?
          AND Ano * 100 + Mes < ?
          AND IgnorarDashboard = 0
    """, (
        user_id,
        grupo,
        data_inicio.year * 100 + data_inicio.month,
        data_fim.year * 100 + data_fim.month
    ))
    
    media = cursor.fetchone()[0]
    return round(media, 2)


def executar_migracao(conn):
    """Executa a migração completa"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    p    
    return None


ÃO")
    print("="*80)
    
    # 1. Adicionar coluna grupo
    print("\n1️⃣  Adicionando coluna 'grupo'...")
    cursor.execute("ALTER TABLE budget_planning ADD COLUMN grupo VARCHAR(100)")
    print("   ✅ Coluna 'grupo' adicionada")
    
    # 2. Mapear tipo_gasto → grupo
    print("\n2️⃣  Mapeando tipo_gasto → grupo...")
    
    cursor.execute("SELECT id, tipo_gasto FROM budget_planning")
    registros = cursor.fetchall()
    
    mapeados = 0
    nao_mapeados = 0
    
    for id_registro, tipo_antigo in registros:
        grupo = mapear_tipo_gasto_para_grupo(tipo_antigo)
        
        if grupo:
            cursor.execute("UPDATE budget_planning SET grupo = ? WHERE id = ?", (grupo, id_registro))
            mapeados += 1
        else:
            nao_mapeados += 1
    
    print(f"   ✅ {mapeados} registros 

def executar_migracao(c  print(f"   ⚠️  {nao_mapeados} registros não mapeados (grupo = NULL)")
    
    conn.commit()
    
    # 3. Recalcular valor_medio_3_meses
    print("\n3️⃣  Recalculando valor_medio_3_meses...")
    
    cursor.execute("""
        SELECT id, user_id, grupo, mes_referencia, valor_planejado
        FROM budget_planning
        WHERE grupo IS NOT NULL
    """)
    
    registros_para_recalcular = cursor.fetchall()
    recalculados = 0
    zerados = 0
    
    for id_registro, user_id, grupo,    registros = cursor.fetchall()
    
    mapeados = 0
    naoursor.execute("SELECT 1 FROM base_grupos_config WHERE nome_grupo = ?", (grupo,))
        
        if cursor.fetchone():
            try:
                media = recalcular_media_3_meses(conn, user_id, grupo, mes_referencia)
                cursor.execute("""
                    UPDATE budget_planning 
                    SET valor_medio_3_meses = ?
                    WHERE id = ?
                """, (media, id_registro))
                recalculados += 1
            except Exception as e:
                cursor.execute("""
                    UPDATE budget_planning 
                    SET valor_medio_3_meses = 0, valor_planejado = 0
                    WHERE id = ?
                """, (id_registro,))
                zerados += 1
        else:
            cursor.execute("""
                UPDATE budget_planning 
         recalculados = 0
    zer_meses = 0, valor_planejado = 0
                WHERE id = ?
            """, (id_registro,))
            zerados += 1
    
    print(f"   ✅ {recalculados} registros recalculados")
    if zerados > 0:
        print(f"   ⚠️  {zerados} registros zerados (grupo inválido)")
    
    conn.commit()
    
    # 4. Atualizar tipo_gasto
    print("\n4️⃣  Atualizando tipo_gasto (22→5 valores)...")
    
    cursor.execute("""
        UPDATE budget_planning
        SET tipo_gasto = (
            SELECT tipo_gasto_padrao 
            FROM base_grupos_config 
            WHERE nome_grupo = budget_planning.grupo
        )
        WHERE grupo IS NOT NULL
          AND EXISTS (
              SELECT 1 
              FROM base_grupos_config 
              WHERE nome_grupo = budget_planning.grupo
                       """, (id_registursor.rowcount
    print(f"   ✅ {tipos_atualizados} tipo_gasto atualizados")
    
    conn.commit()
    
    return mapeados + recalculados


def main():
    """Executa a migração completa"""
    print("="*80)
    print("FASE 4: MIGRAÇÃO BUDGET_PLANNING - Adicionar GRUPO + Recalcular")
    print("="*80)
    print(f"Banco: {DB_PATH}")
    print()
    
    if not DB_PATH.exists():
        print(f"❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        if not validar_dependencias(conn):
            return 1
        
        print("\n" + "="*80)
        resposta = input("Confirma execução da migração? (sim/não): ").strip().lower()
        
        if resposta not in ['sim', 's', 'yes', 'y']:
            print("❌ Migração cancelada pelo usuário")
            return 1
               FROM basp()
        executar_migracao(conn)
        
        print("\n" + "="*80)
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*80)
        print(f"\n📊 Backup: {backup_path.name}")
        print("\n✅ PRÓXIMO PASSO: Executar testes de validação")
        print("   Script: python test_budget_planning_migration.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
