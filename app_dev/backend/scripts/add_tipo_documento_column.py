"""
Script para adicionar coluna tipo_documento à tabela transacoes_exclusao
"""
import sqlite3
import os

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'financas_dev.db')

def add_tipo_documento_column():
    """Adiciona coluna tipo_documento à tabela transacoes_exclusao"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tipo_documento' not in columns:
            print("Adicionando coluna tipo_documento...")
            cursor.execute("""
                ALTER TABLE transacoes_exclusao 
                ADD COLUMN tipo_documento TEXT DEFAULT 'ambos'
            """)
            conn.commit()
            print("✅ Coluna tipo_documento adicionada com sucesso!")
        else:
            print("ℹ️  Coluna tipo_documento já existe")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_tipo_documento_column()
