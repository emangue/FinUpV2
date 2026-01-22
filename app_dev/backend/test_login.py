#!/usr/bin/env python3
"""
Script para testar login diretamente
"""
import sys
from pathlib import Path

# Adicionar app ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.domains.users.models import User
from app.domains.auth.password_utils import verify_password

def test_login():
    """Testa login do admin"""
    
    email = "admin@financas.com"
    senha = "cahriZqonby8"
    
    print(f"🔐 Testando login...")
    print(f"   Email: {email}")
    print(f"   Senha: {senha}")
    print()
    
    db = SessionLocal()
    
    try:
        # Buscar usuário
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ Usuário não encontrado!")
            return False
        
        print(f"✅ Usuário encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.nome}")
        print(f"   Role: {user.role}")
        print(f"   Ativo: {user.ativo} (tipo: {type(user.ativo)})")
        print(f"   Hash: {user.password_hash[:50]}...")
        print()
        
        # Verificar se está ativo
        if not user.ativo:
            print(f"❌ Usuário INATIVO!")
            print(f"   user.ativo = {user.ativo}")
            print(f"   not user.ativo = {not user.ativo}")
            return False
        else:
            print(f"✅ Usuário ATIVO!")
        
        # Verificar senha
        print(f"\n🔐 Verificando senha...")
        senha_correta = verify_password(senha, user.password_hash)
        
        if senha_correta:
            print(f"✅ Senha CORRETA!")
            return True
        else:
            print(f"❌ Senha INCORRETA!")
            print(f"   Senha testada: {senha}")
            print(f"   Hash no banco: {user.password_hash}")
            return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_login()
    sys.exit(0 if success else 1)
