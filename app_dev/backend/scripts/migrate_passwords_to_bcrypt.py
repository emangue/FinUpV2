#!/usr/bin/env python3
"""
Script de Migração: SHA256 → bcrypt
Converte todos os hashes de senha de SHA256 para bcrypt
Com backup automático antes da migração
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import shutil

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domains.users.models import User
from app.domains.auth.password_utils import hash_password, is_bcrypt_hash


def create_backup():
    """Cria backup do banco de dados antes da migração"""
    db_path = settings.DATABASE_PATH
    backup_path = db_path.parent / f"financas_dev_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    print(f"📦 Criando backup: {backup_path.name}")
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado com sucesso!")
    return backup_path


def migrate_passwords():
    """Migra todas as senhas de SHA256 para bcrypt"""
    
    print("\n" + "="*70)
    print("🔐 MIGRAÇÃO DE SENHAS: SHA256 → bcrypt")
    print("="*70 + "\n")
    
    # Criar backup
    backup_path = create_backup()
    
    # Conectar ao banco
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar todos os usuários
        users = session.query(User).all()
        
        if not users:
            print("⚠️  Nenhum usuário encontrado no banco de dados")
            return
        
        print(f"👥 Encontrados {len(users)} usuários\n")
        
        migrated = 0
        already_bcrypt = 0
        errors = 0
        
        for user in users:
            try:
                # Verificar se já é bcrypt
                if is_bcrypt_hash(user.password_hash):
                    print(f"⏭️  {user.email:30} - Já está em bcrypt, pulando")
                    already_bcrypt += 1
                    continue
                
                # Detectar formato do hash
                hash_format = "desconhecido"
                if len(user.password_hash) == 64:
                    hash_format = "SHA256"
                elif user.password_hash.startswith("pbkdf2:sha"):
                    hash_format = "pbkdf2 (Flask/Werkzeug)"
                else:
                    print(f"⚠️  {user.email:30} - Hash com formato inesperado ({len(user.password_hash)} chars)")
                    errors += 1
                    continue
                
                # IMPORTANTE: Não podemos converter hashes antigos para bcrypt
                # Precisamos definir uma senha temporária
                print(f"🔄 {user.email:30} - Formato antigo detectado: {hash_format}")
                
                # Senha temporária: mesma do email ou "changeme123"
                if user.email == "admin@financas.com":
                    temp_password = "admin123"  # Manter senha conhecida do admin
                elif user.email == "admin@email.com":
                    temp_password = "admin123"  # Admin alternativo
                else:
                    temp_password = "changeme123"  # Senha padrão para outros
                
                # Bcrypt limita senhas a 72 bytes
                if len(temp_password.encode('utf-8')) > 72:
                    temp_password = temp_password[:72]
                    print(f"   ⚠️  Senha truncada para 72 bytes")
                
                # Gerar novo hash bcrypt
                new_hash = hash_password(temp_password)
                
                # Atualizar no banco
                user.password_hash = new_hash
                
                print(f"✅ {user.email:30} - Senha atualizada (bcrypt)")
                print(f"   Nova senha temporária: {temp_password}")
                migrated += 1
                
            except Exception as e:
                print(f"❌ {user.email:30} - Erro: {str(e)}")
                errors += 1
        
        # Commit das mudanças
        if migrated > 0:
            session.commit()
            print(f"\n💾 Banco de dados atualizado com sucesso!")
        
        # Resumo
        print("\n" + "="*70)
        print("📊 RESUMO DA MIGRAÇÃO")
        print("="*70)
        print(f"✅ Migrados:        {migrated}")
        print(f"⏭️  Já em bcrypt:    {already_bcrypt}")
        print(f"❌ Erros:           {errors}")
        print(f"📦 Backup em:       {backup_path}")
        print("="*70)
        
        if migrated > 0:
            print("\n⚠️  IMPORTANTE:")
            print("   - Usuário admin: email=admin@financas.com, senha=admin123")
            print("   - Outros usuários: senha temporária = changeme123")
            print("   - Recomenda-se trocar a senha no primeiro login")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        print(f"💾 Banco de dados NÃO foi alterado")
        print(f"📦 Backup disponível em: {backup_path}")
        raise
    
    finally:
        session.close()


if __name__ == "__main__":
    try:
        migrate_passwords()
        print("\n✅ Migração concluída com sucesso!")
    except Exception as e:
        print(f"\n❌ Migração falhou: {str(e)}")
        sys.exit(1)
