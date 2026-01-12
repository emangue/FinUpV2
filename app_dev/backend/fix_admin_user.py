#!/usr/bin/env python3
"""
Script para corrigir/criar usuário admin
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import necessários
from app.core.database import SessionLocal
from app.domains.users.models import User
from app.domains.users.service import hash_password

def fix_admin_user():
    db = SessionLocal()
    
    try:
        # Buscar usuário admin
        admin = db.query(User).filter(User.email == 'admin@email.com').first()
        
        if admin:
            print(f"Admin encontrado:")
            print(f"  ID: {admin.id}")
            print(f"  Email: {admin.email}")
            print(f"  Nome: {admin.nome}")
            print(f"  Ativo: {admin.ativo}")
            print(f"  Role: {admin.role}")
            
            # Atualizar senha e ativar usuário
            admin.password_hash = hash_password('admin123')
            admin.ativo = 1
            admin.role = 'admin'
            
            db.commit()
            print(f"✅ Usuário admin atualizado: senha=admin123, ativo=1, role=admin")
        else:
            # Criar usuário admin
            new_admin = User(
                email='admin@email.com',
                nome='Admin',
                password_hash=hash_password('admin123'),
                ativo=1,
                role='admin'
            )
            db.add(new_admin)
            db.commit()
            print(f"✅ Usuário admin criado: email=admin@email.com, senha=admin123, ativo=1, role=admin")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_user()