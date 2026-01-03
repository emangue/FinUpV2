#!/usr/bin/env python3
"""
Script para criar usuário admin

Cria usuário administrador no sistema
"""
from app.models import User, get_db_session
import sys

def create_admin():
    """Cria usuário admin padrão"""
    db = get_db_session()
    
    try:
        # Verificar se já existe admin
        existing = db.query(User).filter_by(email='admin@email.com').first()
        if existing:
            print(f"✅ Usuário admin já existe: {existing.email}")
            print(f"   ID: {existing.id}")
            print(f"   Nome: {existing.nome}")
            print(f"   Role: {existing.role}")
            print(f"   Ativo: {existing.ativo}")
            
            # Resetar senha se solicitado
            if len(sys.argv) > 1 and sys.argv[1] == '--reset-password':
                existing.set_password('admin123')
                db.commit()
                print(f"\n🔄 Senha resetada para: admin123")
            return existing
        
        # Criar novo admin
        admin = User(
            email='admin@email.com',
            nome='Administrador',
            ativo=True,
            role='admin'
        )
        admin.set_password('admin123')
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuário admin criado com sucesso!")
        print(f"   Email: admin@email.com")
        print(f"   Senha: admin123")
        print(f"   ID: {admin.id}")
        print(f"   Role: {admin.role}")
        
        return admin
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar admin: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    create_admin()
