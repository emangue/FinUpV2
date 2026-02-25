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
    from dateutil.relativedelta import relativedelta

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def mapear_tipo_gasto_para_grupo(tipo_gasto_antigo):
    """Mapeia tipo_gasto antigo → grupo"""
    if not tipo_gasto_antigo:
        return None
    
    mapeamentos = {
        'Pagamento Fatura': 'Transferência Entre Contas',
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


def recalcular_media_3_meses(conn, user_id, grupo, mes_referencia):
    """Recalcula valor_medio_3_meses baseado em journal_entries dos últimos 3 meses"""
    cursor = conn.cursor()
    
    ano_ref, mes_ref = map(int, mes_referencia.split('-'))
    
    data_ref = datetime(ano_ref, mes_ref, 1)
    data_inicio = data_ref - relativedelta(months=3)
    
    cursor.execute("""
        SELECT COALESCE(SUM(ABS(Valor)), 0) / 3.0 as media
        FROM journal_entries
        WHERE user_id = ?
          AND GRUPO = ?
          AND Ano * 100 + Mes >= ?
          AND Ano * 100 + Mes < ?
          AND IgnorarDashboard = 0
    """, (user_id, grupo, data_inicio.year * 100 + data_inicio.month, ano_ref * 100 + mes_ref))
    
    media = cursor.fetchone()[0]
    return round(media, 2)


def main():
    print("="*80)
    print("FASE 4: MIGRAÇÃO BUDGET_PLANNING - Adicionar GRUPO + Recalcular")
    print("="*80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = DB_PATH.parent / f"financas_dev.db.backup_fase4_{timestamp}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup: {backup_path.name}")
        
        # 1. Adicionar coluna
        print("\n1️⃣  Adicionando coluna 'grupo'...")
        cursor.execute("ALTER TABLE budget_planning ADD COLUMN grupo VARCHAR(100)")
        print("   ✅ Coluna adicionada")
        
        # 2. Mapear
        print("\n2️⃣  Mapeando tipo_gasto → grupo...")
        cursor.execute("SELECT id, tipo_gasto FROM budget_planning")
        for id_reg, tipo in cursor.fetchall():
            grupo = mapear_tipo_gasto_para_grupo(tipo)
            if grupo:
                conn.execute("UPDATE budget_planning SET grupo = ? WHERE id = ?", (grupo, id_reg))
        conn.commit()
        print("   ✅ Mapeamento concluído")
        
        # 3. Recalcular
        print("\n3️⃣  Recalculando valor_medio_3_meses...")
        cursor.execute("SELECT id, user_id, grupo, mes_referencia FROM budget_planning WHERE grupo IS NOT NULL")
        for id_reg, user_id, grupo, mes_ref in cursor.fetchall():
            cursor.execute("SELECT 1 FROM base_grupos_config WHERE nome_grupo = ?", (grupo,))
            if cursor.fetchone():
                try:
                    media = recalcular_media_3_meses(conn, user_id, grupo, mes_ref)
                    conn.execute("UPDATE budget_planning SET valor_medio_3_meses = ? WHERE id = ?", (media, id_reg))
                except:
                    conn.execute("UPDATE budget_planning SET valor_medio_3_meses = 0, valor_planejado = 0 WHERE id = ?", (id_reg,))
            else:
                conn.execute("UPDATE budget_planning SET valor_medio_3_meses = 0, valor_planejado = 0 WHERE id = ?", (id_reg,))
        conn.commit()
        print("   ✅ Recálculo concluído")
        
        # 4. Atualizar tipo_gasto
        print("\n4️⃣  Atualizando tipo_gasto...")
        cursor.execute("""
            UPDATE budget_planning
            SET tipo_gasto = (SELECT tipo_gasto_padrao FROM base_grupos_config WHERE nome_grupo = budget_planning.grupo)
            WHERE grupo IS NOT NULL AND EXISTS (SELECT 1 FROM base_grupos_config WHERE nome_grupo = budget_planning.grupo)
        """)
        conn.commit()
        print(f"   ✅ {cursor.rowcount} registros atualizados")
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA!")
        print("\n⏭️  PRÓXIMO: python test_budget_planning_migration.py")
        
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
