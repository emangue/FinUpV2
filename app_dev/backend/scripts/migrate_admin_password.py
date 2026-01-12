"""
Script de migração urgente: Atualizar senha do admin de SHA256 para bcrypt

Este script é temporário para resolver o problema do admin que ainda tem
senha SHA256 (64 caracteres hex) que excede o limite de 72 bytes do bcrypt.

Após executar, o admin poderá fazer login normalmente.
"""
import sys
from pathlib import Path

# Adicionar app ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.domains.users.models import User
from app.domains.users.service import hash_password


def migrate_admin():
    """Migra senha do admin de SHA256 para bcrypt"""
    db = SessionLocal()
    
    try:
        # Buscar admin
        admin = db.query(User).filter(User.email == "admin@email.com").first()
        
        if not admin:
            print("❌ Admin não encontrado!")
            return False
        
        # Verificar se já está em bcrypt (começa com $2b$)
        if admin.password_hash.startswith("$2b$"):
            print("✅ Admin já está com bcrypt!")
            return True
        
        # Se tem 64 caracteres hex, é SHA256
        if len(admin.password_hash) == 64 and all(c in "0123456789abcdef" for c in admin.password_hash):
            print(f"🔄 Migrando admin de SHA256 para bcrypt...")
            
            # Resetar para senha padrão "admin123"
            new_hash = hash_password("admin123")
            admin.password_hash = new_hash
            db.commit()
            
            print("✅ Admin migrado com sucesso!")
            print(f"   Email: admin@email.com")
            print(f"   Senha: admin123")
            print(f"   Hash: {new_hash[:20]}... (bcrypt)")
            return True
        else:
            print(f"⚠️ Hash do admin não é SHA256 nem bcrypt conhecido: {admin.password_hash[:20]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao migrar: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("🔐 Migrando senha do admin para bcrypt...")
    print()
    
    success = migrate_admin()
    
    if success:
        print()
        print("🎉 Migração concluída! Agora você pode fazer login:")
        print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"email": "admin@email.com", "password": "admin123"}\'')
        sys.exit(0)
    else:
        print()
        print("❌ Falha na migração!")
        sys.exit(1)
