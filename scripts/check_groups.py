import sqlite3

def check_groups():
    conn = sqlite3.connect('financas.db')
    cursor = conn.cursor()
    
    query = """
    SELECT GRUPO, IgnorarDashboard, COUNT(*) as count
    FROM journal_entries
    GROUP BY GRUPO, IgnorarDashboard
    ORDER BY GRUPO
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"{'GRUPO':<30} | {'IGNORAR':<10} | {'COUNT':<5}")
    print("-" * 50)
    
    for row in results:
        grupo = row[0] if row[0] else "None"
        ignorar = str(row[1])
        count = row[2]
        print(f"{grupo:<30} | {ignorar:<10} | {count:<5}")
        
    conn.close()

if __name__ == "__main__":
    check_groups()
