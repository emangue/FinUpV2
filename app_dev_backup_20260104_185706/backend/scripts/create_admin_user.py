"""
Script para criar usuário admin padrão
"""
import sqlite3
import os
import hashlib
from datetime import datetime

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'financas_dev.db')

def hash_password(password: str) -> str:
    """Hash de senha usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """Cria ou atualiza o usuário admin com ID 1"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se usuário ID 1 existe
        cursor.execute("SELECT id, nome, email FROM users WHERE id = 1")
        existing = cursor.fetchone()
        
        if existing:
            print(f"ℹ️  Usuário admin já existe:")
            print(f"   ID: {existing[0]}")
            print(f"   Nome: {existing[1]}")
            print(f"   Email: {existing[2]}")
        else:
            # Criar usuário admin
            now = datetime.now().isoformat()
            password_hash = hash_password("admin123")  # Senha padrão
            
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, nome, ativo, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, "admin@financas.com", password_hash, "Administrador", 1, "admin", now, now))
            
            conn.commit()
            print("✅ Usuário admin criado com sucesso!")
            print(f"   Email: admin@financas.com")
            print(f"   Senha: admin123")
            print(f"   ⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin_user()
