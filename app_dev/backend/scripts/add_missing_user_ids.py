"""
Script para adicionar user_id às tabelas que faltam
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'financas_dev.db')

def add_user_id_columns():
    """Adiciona coluna user_id às tabelas que não têm"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables_to_update = ['ignorar_estabelecimentos', 'duplicados_temp']
    
    try:
        for table in tables_to_update:
            # Verificar se tabela existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"⚠️  Tabela {table} não existe")
                continue
            
            # Verificar se já tem user_id
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print(f"📝 Adicionando user_id em {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER DEFAULT 1")
                cursor.execute(f"UPDATE {table} SET user_id = 1 WHERE user_id IS NULL")
                print(f"✅ {table}: user_id adicionado e registros atualizados")
            else:
                # Atualizar registros NULL para 1
                cursor.execute(f"UPDATE {table} SET user_id = 1 WHERE user_id IS NULL")
                affected = cursor.rowcount
                if affected > 0:
                    print(f"✅ {table}: {affected} registros atualizados para user_id = 1")
                else:
                    print(f"ℹ️  {table}: já estava correto")
        
        conn.commit()
        print("\n✅ Todas as tabelas atualizadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    add_user_id_columns()
