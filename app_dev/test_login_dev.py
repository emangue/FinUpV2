"""
Script para testar e criar usuário admin no app_dev
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app_dev.backend.models import User, Base
import bcrypt

# Conectar ao banco
engine = create_engine('sqlite:///financas.db')
Session = sessionmaker(bind=engine)
session = Session()

# Verificar se usuário admin existe
admin = session.query(User).filter_by(email='admin@email.com').first()

if admin:
    print(f"✅ Usuário encontrado: {admin.email}")
    print(f"Nome: {admin.nome}")
    
    # Testar senha
    senha_correta = bcrypt.checkpw('admin123'.encode('utf-8'), admin.password_hash.encode('utf-8') if isinstance(admin.password_hash, str) else admin.password_hash)
    print(f"Senha 'admin123' correta: {senha_correta}")
    
    if not senha_correta:
        print("\n❌ Senha incorreta! Atualizando para 'admin123'...")
        admin.password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        session.commit()
        print("✅ Senha atualizada com sucesso!")
else:
    print("❌ Usuário admin não encontrado. Criando...")
    
    # Criar usuário admin
    novo_admin = User(
        email='admin@email.com',
        nome='Administrador',
        password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        ativo=True
    )
    session.add(novo_admin)
    session.commit()
    print(f"✅ Usuário criado com sucesso! ID: {novo_admin.id}")

# Listar todos os usuários
print("\n📋 Usuários no banco:")
usuarios = session.query(User).all()
for u in usuarios:
    print(f"  - ID: {u.id} | Email: {u.email} | Nome: {u.nome} | Ativo: {u.ativo}")

session.close()
