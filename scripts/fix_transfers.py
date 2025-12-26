import sqlite3

def update_transfers():
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()
    
    # Atualiza registros onde GRUPO é 'Transferência Entre Contas'
    cursor.execute("""
        UPDATE journal_entries 
        SET IgnorarDashboard = 1 
        WHERE GRUPO = 'Transferência Entre Contas'
    """)
    
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ {rows} registros de 'Transferência Entre Contas' atualizados para IgnorarDashboard=1.")

if __name__ == "__main__":
    update_transfers()
