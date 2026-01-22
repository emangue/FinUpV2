#!/usr/bin/env python3
"""
Script para atualizar senha do admin@financas.com (ID: 1)
"""
import sys
from pathlib import Path

# Adicionar app ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.domains.users.models import User
from app.domains.auth.password_utils import hash_password

def update_admin_password():
    """Atualiza senha do admin@financas.com"""
    
    # Nova senha
    nova_senha = "cahriZqonby8"
    
    print("🔐 Atualizando senha do admin@financas.com...")
    print(f"   Nova senha: {nova_senha}")
    
    # Criar sessão
    db = SessionLocal()
    
    try:
        # Buscar usuário admin@financas.com especificamente (ID: 1)
        admin = db.query(User).filter(User.email == 'admin@financas.com').first()
        
        if not admin:
            print("❌ Usuário admin@financas.com não encontrado!")
            return False
        
        print(f"✅ Admin encontrado: {admin.email} (ID: {admin.id})")
        
        # Hash da nova senha usando função do sistema
        password_hash = hash_password(nova_senha)
        print(f"✅ Hash gerado: {password_hash[:50]}...")
        
        # Atualizar senha
        admin.password_hash = password_hash
        db.commit()
        
        print(f"\n✅ Senha atualizada com sucesso!")
        print(f"   Email: {admin.email}")
        print(f"   Senha: {nova_senha}")
        print(f"   Ativo: {admin.ativo}")
        print(f"   Role: {admin.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = update_admin_password()
    sys.exit(0 if success else 1)
