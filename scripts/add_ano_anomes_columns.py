"""
Script para adicionar colunas ano e anomes à tabela investimentos_portfolio
"""
import sqlite3
import sys
from pathlib import Path

# Path do banco de dados
DB_PATH = Path(__file__).parent.parent / 'app_dev' / 'backend' / 'database' / 'financas_dev.db'

def main():
    print(f"📂 Conectando ao banco: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Erro: Banco de dados não encontrado em {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(investimentos_portfolio)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Colunas existentes: {columns}")
        
        # Adicionar coluna ano se não existir
        if 'ano' not in columns:
            print("➕ Adicionando coluna 'ano'...")
            cursor.execute("""
                ALTER TABLE investimentos_portfolio 
                ADD COLUMN ano INTEGER
            """)
            print("✅ Coluna 'ano' adicionada!")
        else:
            print("ℹ️  Coluna 'ano' já existe")
        
        # Adicionar coluna anomes se não existir
        if 'anomes' not in columns:
            print("➕ Adicionando coluna 'anomes'...")
            cursor.execute("""
                ALTER TABLE investimentos_portfolio 
                ADD COLUMN anomes INTEGER
            """)
            print("✅ Coluna 'anomes' adicionada!")
        else:
            print("ℹ️  Coluna 'anomes' já existe")
        
        conn.commit()
        
        # Criar índice idx_user_anomes se não existir
        print("📑 Criando índice idx_user_anomes...")
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_anomes 
                ON investimentos_portfolio(user_id, anomes)
            """)
            conn.commit()
            print("✅ Índice criado!")
        except Exception as e:
            print(f"⚠️  Erro ao criar índice (pode já existir): {e}")
        
        # Verificar resultado final
        cursor.execute("PRAGMA table_info(investimentos_portfolio)")
        columns_final = [row[1] for row in cursor.fetchall()]
        print(f"\n✅ Schema atualizado! Colunas finais: {columns_final}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n🎉 Migração concluída com sucesso!")

if __name__ == "__main__":
    main()
