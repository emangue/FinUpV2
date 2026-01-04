"""
Script para migrar banco de dados adicionando campo tipo_documento
"""
import sys
import os
import sqlite3
from datetime import datetime

# Caminho do banco de dados
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'financas_dev.db')

def migrate_database():
    """Adiciona coluna tipo_documento se não existir"""
    print(f"Conectando ao banco: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes_exclusao'")
        if not cursor.fetchone():
            print("❌ Tabela transacoes_exclusao não existe. Execute create_tables.py primeiro.")
            return False
        
        # Verificar estrutura atual
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Colunas atuais: {', '.join(column_names)}")
        
        # Adicionar coluna tipo_documento se não existir
        if 'tipo_documento' not in column_names:
            print("\nAdicionando coluna tipo_documento...")
            cursor.execute("""
                ALTER TABLE transacoes_exclusao 
                ADD COLUMN tipo_documento TEXT DEFAULT 'ambos'
            """)
            conn.commit()
            print("✅ Coluna tipo_documento adicionada com sucesso!")
            
            # Atualizar registros existentes
            cursor.execute("UPDATE transacoes_exclusao SET tipo_documento = 'ambos' WHERE tipo_documento IS NULL")
            conn.commit()
            print(f"✅ {cursor.rowcount} registros atualizados")
        else:
            print("ℹ️  Coluna tipo_documento já existe")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = cursor.fetchall()
        print("\nEstrutura final da tabela:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
