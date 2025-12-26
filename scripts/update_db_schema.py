import sqlite3
import os

DB_PATH = 'financas.db'

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados {DB_PATH} não encontrado.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Adicionar coluna IgnorarDashboard se não existir
    try:
        cursor.execute("ALTER TABLE journal_entries ADD COLUMN IgnorarDashboard BOOLEAN DEFAULT 0")
        print("✅ Coluna IgnorarDashboard adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Coluna IgnorarDashboard já existe.")
        else:
            print(f"❌ Erro ao adicionar coluna: {e}")

    # 2. Atualizar registros existentes
    # Marcar como IgnorarDashboard=1 onde GRUPO é 'Transferências' ou 'Investimentos'
    try:
        cursor.execute("""
            UPDATE journal_entries 
            SET IgnorarDashboard = 1 
            WHERE GRUPO IN ('Transferências', 'Investimentos')
        """)
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros atualizados com IgnorarDashboard=1.")
        
        conn.commit()
    except Exception as e:
        print(f"❌ Erro ao atualizar registros: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
