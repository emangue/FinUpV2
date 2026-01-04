"""
Script para garantir que todos os registros tenham user_id = 1
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'financas_dev.db')

def update_all_user_ids():
    """Atualiza user_id para 1 em todas as tabelas"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Listar todas as tabelas que têm coluna user_id
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📊 Encontradas {len(tables)} tabelas no banco")
        
        for table in tables:
            # Verificar se a tabela tem coluna user_id
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' in columns:
                # Atualizar todos os registros para user_id = 1
                cursor.execute(f"UPDATE {table} SET user_id = 1 WHERE user_id IS NULL OR user_id != 1")
                affected = cursor.rowcount
                if affected > 0:
                    print(f"✅ {table}: {affected} registros atualizados para user_id = 1")
                else:
                    print(f"ℹ️  {table}: já estava correto")
        
        conn.commit()
        print("\n✅ Todas as tabelas atualizadas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    update_all_user_ids()
