#!/usr/bin/env python3
"""
FASE 4: MIGRAÇÃO BUDGET_PLANNING - tipo_gasto → grupo
======================================================

Recria budget_planning trocando tipo_gasto por grupo:
- Tabela antiga: (user_id, tipo_gasto, mes_referencia) → 18 valores
- Tabela nova: (user_id, grupo, mes_referencia) → 27 grupos
- Consolida valores duplicados (soma valor_planejado)
- Recalcula valor_medio_3_meses por grupo dos últimos 3 meses
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
    from dateutil.relativedelta import relativedelta

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DB_PATH = PROJECT_ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def mapear_tipo_gasto_para_grupo(tipo_gasto):
    """Mapeia tipo_gasto antigo → grupo"""
    if not tipo_gasto:
        return None
    
    mapeamentos = {
        'Pagamento Fatura': 'Fatura',
        'Débito': 'Transferência Entre Contas',
        'Fixo': 'Moradia',
        'Ajustável': 'Outros',
        'Ajustavel - Casa': 'Casa',
    }
    
    if tipo_gasto in mapeamentos:
        return mapeamentos[tipo_gasto]
    
    if ' - ' in tipo_gasto:
        return tipo_gasto.split(' - ', 1)[1]
    
    return None


def recalcular_media_3_meses(conn, user_id, grupo, mes_referencia):
    """Calcula média dos últimos 3 meses por grupo"""
    cursor = conn.cursor()
    
    ano_ref, mes_ref = map(int, mes_referencia.split('-'))
    data_ref = datetime(ano_ref, mes_ref, 1)
    data_inicio = data_ref - relativedelta(months=3)
    
    # Usar MesFatura (formato YYYYMM) ou extrair de Data (DD/MM/YYYY)
    cursor.execute("""
        SELECT COALESCE(SUM(ABS(Valor)), 0) / 3.0
        FROM journal_entries
        WHERE user_id = ?
          AND GRUPO = ?
          AND CAST(MesFatura AS INTEGER) >= ?
          AND CAST(MesFatura AS INTEGER) < ?
          AND IgnorarDashboard = 0
    """, (user_id, grupo, data_inicio.year * 100 + data_inicio.month, ano_ref * 100 + mes_ref))
    
    return round(cursor.fetchone()[0], 2)


def main():
    print("="*80)
    print("FASE 4: BUDGET_PLANNING - tipo_gasto → grupo")
    print("="*80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = DB_PATH.parent / f"financas_dev.db.backup_fase4_{timestamp}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup: {backup_path.name}\n")
        
        # 1. Criar tabela nova
        print("1️⃣  Criando budget_planning_new...")
        cursor.execute("""
            CREATE TABLE budget_planning_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                grupo VARCHAR(100) NOT NULL,
                mes_referencia VARCHAR(7) NOT NULL,
                valor_planejado DECIMAL(10, 2) DEFAULT 0,
                valor_medio_3_meses DECIMAL(10, 2) DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, grupo, mes_referencia),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("   ✅ Tabela criada\n")
        
        # 2. Migrar dados consolidando duplicatas
        print("2️⃣  Migrando dados (consolidando duplicatas)...")
        
        # Mapear tipo_gasto → grupo e agrupar
        cursor.execute("""
            SELECT user_id, tipo_gasto, mes_referencia, SUM(valor_planejado) as total_planejado
            FROM budget_planning
            GROUP BY user_id, tipo_gasto, mes_referencia
        """)
        
        registros_antigos = cursor.fetchall()
        grupos_consolidados = {}
        
        for user_id, tipo_gasto, mes_ref, valor_plan in registros_antigos:
            grupo = mapear_tipo_gasto_para_grupo(tipo_gasto)
            
            if grupo:
                chave = (user_id, grupo, mes_ref)
                if chave in grupos_consolidados:
                    grupos_consolidados[chave] += valor_plan
                else:
                    grupos_consolidados[chave] = valor_plan
        
        print(f"   📊 {len(registros_antigos)} registros antigos → {len(grupos_consolidados)} grupos únicos")
        
        # 3. Inserir dados consolidados
        print("\n3️⃣  Inserindo dados consolidados...")
        
        inseridos = 0
        zerados = 0
        
        for (user_id, grupo, mes_ref), valor_plan in grupos_consolidados.items():
            # Verificar se grupo existe em base_grupos_config
            cursor.execute("SELECT 1 FROM base_grupos_config WHERE nome_grupo = ?", (grupo,))
            
            if cursor.fetchone():
                try:
                    # Recalcular média
                    media = recalcular_media_3_meses(conn, user_id, grupo, mes_ref)
                    
                    cursor.execute("""
                        INSERT INTO budget_planning_new 
                        (user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, grupo, mes_ref, valor_plan, media))
                    inseridos += 1
                except Exception as e:
                    print(f"   ⚠️  Erro ao inserir {grupo}: {e}")
            else:
                # Grupo não existe - inserir com valores zerados
                try:
                    cursor.execute("""
                        INSERT INTO budget_planning_new 
                        (user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses)
                        VALUES (?, ?, ?, 0, 0)
                    """, (user_id, grupo, mes_ref))
                    zerados += 1
                except Exception as e:
                    print(f"   ⚠️  Erro ao inserir {grupo} (zerado): {e}")
        
        conn.commit()
        print(f"   ✅ {inseridos} registros inseridos")
        if zerados > 0:
            print(f"   ⚠️  {zerados} grupos sem config (valores zerados)")
        
        # 4. Substituir tabela antiga
        print("\n4️⃣  Substituindo tabela antiga...")
        cursor.execute("DROP TABLE budget_planning")
        cursor.execute("ALTER TABLE budget_planning_new RENAME TO budget_planning")
        conn.commit()
        print("   ✅ Tabela substituída\n")
        
        # 5. Validação
        print("="*80)
        print("✅ VALIDAÇÃO")
        print("="*80)
        
        cursor.execute("SELECT COUNT(*) FROM budget_planning")
        total = cursor.fetchone()[0]
        print(f"Total de registros: {total}")
        
        cursor.execute("SELECT COUNT(DISTINCT grupo) FROM budget_planning")
        grupos = cursor.fetchone()[0]
        print(f"Grupos únicos: {grupos}")
        
        cursor.execute("""
            SELECT grupo, COUNT(*) as total
            FROM budget_planning
            GROUP BY grupo
            ORDER BY total DESC
            LIMIT 10
        """)
        
        print("\nTop 10 grupos:")
        for grupo, count in cursor.fetchall():
            print(f"  {grupo:30s} → {count:3d} registros")
        
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
