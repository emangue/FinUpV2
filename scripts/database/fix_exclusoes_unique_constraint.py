#!/usr/bin/env python3
"""
Fix UNIQUE constraint in transacoes_exclusao table
- Remove UNIQUE constraint from nome_transacao alone
- Add UNIQUE constraint on (user_id, nome_transacao) pair
"""
import sqlite3
import sys
from pathlib import Path

# Path do banco
DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"

def fix_unique_constraint():
    """Corrige a constraint UNIQUE na tabela transacoes_exclusao"""
    
    print(f"🔧 Corrigindo constraint UNIQUE em transacoes_exclusao...")
    print(f"📂 Banco: {DB_PATH}\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Backup dos dados
        print("1️⃣ Fazendo backup dos dados...")
        cursor.execute("SELECT * FROM transacoes_exclusao")
        backup_data = cursor.fetchall()
        print(f"   ✅ {len(backup_data)} registros salvos\n")
        
        # 2. Criar tabela nova com constraint correta
        print("2️⃣ Criando nova tabela com constraint correta...")
        cursor.execute("""
            CREATE TABLE transacoes_exclusao_new (
                id INTEGER NOT NULL PRIMARY KEY,
                nome_transacao VARCHAR NOT NULL,
                banco VARCHAR,
                descricao TEXT,
                user_id INTEGER NOT NULL,
                ativo INTEGER DEFAULT 1,
                tipo_documento TEXT DEFAULT 'ambos',
                acao VARCHAR(10) DEFAULT 'EXCLUIR',
                created_at DATETIME,
                updated_at DATETIME,
                UNIQUE (user_id, nome_transacao)
            )
        """)
        print("   ✅ Tabela nova criada\n")
        
        # 3. Copiar dados
        print("3️⃣ Copiando dados para nova tabela...")
        cursor.execute("""
            INSERT INTO transacoes_exclusao_new 
            SELECT * FROM transacoes_exclusao
        """)
        print(f"   ✅ {cursor.rowcount} registros copiados\n")
        
        # 4. Dropar tabela antiga
        print("4️⃣ Removendo tabela antiga...")
        cursor.execute("DROP TABLE transacoes_exclusao")
        print("   ✅ Tabela antiga removida\n")
        
        # 5. Renomear nova tabela
        print("5️⃣ Renomeando nova tabela...")
        cursor.execute("ALTER TABLE transacoes_exclusao_new RENAME TO transacoes_exclusao")
        print("   ✅ Tabela renomeada\n")
        
        # 6. Recriar índices
        print("6️⃣ Recriando índices...")
        cursor.execute("CREATE INDEX ix_transacoes_exclusao_id ON transacoes_exclusao (id)")
        cursor.execute("CREATE INDEX ix_transacoes_exclusao_user_id ON transacoes_exclusao (user_id)")
        cursor.execute("CREATE INDEX ix_transacoes_exclusao_nome_transacao ON transacoes_exclusao (nome_transacao)")
        print("   ✅ Índices recriados\n")
        
        # 7. Commit
        conn.commit()
        
        # 8. Verificar novo schema
        print("7️⃣ Verificando novo schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transacoes_exclusao'")
        schema = cursor.fetchone()[0]
        print("   Schema atualizado:")
        for line in schema.split('\n'):
            print(f"   {line}")
        print()
        
        # 9. Verificar dados
        cursor.execute("SELECT COUNT(*) FROM transacoes_exclusao")
        count = cursor.fetchone()[0]
        print(f"8️⃣ Verificando dados: {count} registros")
        
        if count == len(backup_data):
            print("   ✅ Todos os registros foram preservados\n")
        else:
            print(f"   ⚠️  ATENÇÃO: Esperados {len(backup_data)}, encontrados {count}\n")
        
        print("✅ Constraint UNIQUE corrigida com sucesso!")
        print("   Agora cada usuário pode ter exclusões com o mesmo nome\n")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(fix_unique_constraint())
