"""
Script para adicionar coluna IdParcela na tabela journal_entries
"""
import sqlite3
import sys
from pathlib import Path

# Caminho do banco de dados
DB_PATH = Path(__file__).parent.parent / 'financas.db'


def adicionar_coluna_idparcela():
    """Adiciona coluna IdParcela se não existir"""
    
    print("=" * 70)
    print("🔧 Adicionando coluna IdParcela no banco de dados")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        cursor.execute("PRAGMA table_info(journal_entries)")
        colunas = [row[1] for row in cursor.fetchall()]
        
        if 'IdParcela' in colunas:
            print("✅ Coluna IdParcela já existe no banco de dados")
            conn.close()
            return True
        
        print("⏳ Adicionando coluna IdParcela...")
        
        # Adiciona a coluna
        cursor.execute("""
            ALTER TABLE journal_entries 
            ADD COLUMN IdParcela TEXT
        """)
        
        # Cria índice para performance
        print("⏳ Criando índice para IdParcela...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_journal_entries_idparcela 
            ON journal_entries(IdParcela)
        """)
        
        conn.commit()
        
        print("✅ Coluna IdParcela adicionada com sucesso!")
        print("✅ Índice criado com sucesso!")
        print("=" * 70)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print(f"\n📁 Banco de dados: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        sys.exit(1)
    
    sucesso = adicionar_coluna_idparcela()
    
    if sucesso:
        print("\n✅ Migração de schema concluída!")
        print("Agora você pode executar: python scripts/populate_id_parcela.py")
    else:
        print("\n❌ Falha na migração de schema")
        sys.exit(1)
