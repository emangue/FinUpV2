#!/usr/bin/env python3
"""
Script para adicionar coluna user_id nas tabelas de investimentos que não têm
E popular com os valores corretos baseado nas foreign keys
"""

import sqlite3

DB_PATH = "app_dev/backend/database/financas_dev.db"

def adicionar_user_id():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"\n{'='*70}")
    print("ADICIONANDO user_id EM TABELAS DE INVESTIMENTOS")
    print(f"{'='*70}\n")
    
    try:
        # 1. investimentos_historico (via investimentos_portfolio)
        print("📋 investimentos_historico:")
        
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(investimentos_historico)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in colunas:
            print("  ➕ Adicionando coluna user_id...")
            cursor.execute("ALTER TABLE investimentos_historico ADD COLUMN user_id INTEGER")
            
            print("  🔗 Populando user_id via foreign key (investimento_id → portfolio)...")
            cursor.execute("""
                UPDATE investimentos_historico
                SET user_id = (
                    SELECT p.user_id 
                    FROM investimentos_portfolio p 
                    WHERE p.id = investimentos_historico.investimento_id
                )
            """)
            
            print("  📊 Criando índice...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_investimentos_historico_user_id ON investimentos_historico (user_id)")
            
            cursor.execute("SELECT COUNT(*) FROM investimentos_historico")
            total = cursor.fetchone()[0]
            print(f"  ✅ {total} registros atualizados\n")
        else:
            print("  ✓ Coluna user_id já existe\n")
        
        # 2. investimentos_aportes_extraordinarios (via investimentos_cenarios)
        print("📋 investimentos_aportes_extraordinarios:")
        
        cursor.execute("PRAGMA table_info(investimentos_aportes_extraordinarios)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in colunas:
            print("  ➕ Adicionando coluna user_id...")
            cursor.execute("ALTER TABLE investimentos_aportes_extraordinarios ADD COLUMN user_id INTEGER")
            
            print("  🔗 Populando user_id via foreign key (cenario_id → cenarios)...")
            cursor.execute("""
                UPDATE investimentos_aportes_extraordinarios
                SET user_id = (
                    SELECT c.user_id 
                    FROM investimentos_cenarios c 
                    WHERE c.id = investimentos_aportes_extraordinarios.cenario_id
                )
            """)
            
            print("  📊 Criando índice...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_investimentos_aportes_extraordinarios_user_id ON investimentos_aportes_extraordinarios (user_id)")
            
            cursor.execute("SELECT COUNT(*) FROM investimentos_aportes_extraordinarios")
            total = cursor.fetchone()[0]
            print(f"  ✅ {total} registros atualizados\n")
        else:
            print("  ✓ Coluna user_id já existe\n")
        
        conn.commit()
        
        print(f"{'='*70}")
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        
        # Verificar resultado final
        print("📊 VALIDAÇÃO FINAL:\n")
        for tabela in ['investimentos_historico', 'investimentos_aportes_extraordinarios']:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE user_id IS NOT NULL")
            com_user = cursor.fetchone()[0]
            print(f"  • {tabela}:")
            print(f"      Total: {total} | Com user_id: {com_user}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    adicionar_user_id()
