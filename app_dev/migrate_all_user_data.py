#!/usr/bin/env python3
"""
Script para migrar TODOS os dados de user_id=1 para user_id=3 (admin)
"""

import sqlite3
import sys

def migrate_all_user_data():
    print("🔍 Iniciando migração completa de dados user_id=1 → user_id=3...")
    
    conn = sqlite3.connect('backend/database/financas_dev.db')
    cursor = conn.cursor()
    
    try:
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Total de tabelas encontradas: {len(tables)}")
        
        migrated_total = 0
        
        for table in tables:
            try:
                # Verificar se tabela tem coluna user_id
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' in columns:
                    # Contar registros com user_id=1
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = 1")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        print(f"📦 {table}: {count} registros com user_id=1")
                        
                        # Migrar
                        cursor.execute(f"UPDATE {table} SET user_id = 3 WHERE user_id = 1")
                        migrated = cursor.rowcount
                        print(f"   ✅ Migrados: {migrated}")
                        migrated_total += migrated
                    else:
                        # Verificar se tem dados user_id=3
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = 3")
                        count_3 = cursor.fetchone()[0]
                        if count_3 > 0:
                            print(f"   ✅ {table}: {count_3} registros já em user_id=3")
                
            except Exception as e:
                print(f"❌ Erro em {table}: {e}")
                continue
        
        # Commit das mudanças
        conn.commit()
        print(f"\n🎉 Migração completa! {migrated_total} registros migrados para user_id=3")
        
        # Verificação final
        print("\n📊 VERIFICAÇÃO FINAL - Contagem por tabela:")
        for table in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' in columns:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = 3")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"   {table}: {count} registros user_id=3")
            except:
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_all_user_data()
    sys.exit(0 if success else 1)