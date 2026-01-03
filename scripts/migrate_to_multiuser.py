#!/usr/bin/env python3
"""
Script de Migração para Sistema Multi-Usuário

Versão: 2.1.0-dev
Data: 28/12/2025

Migra dados existentes para sistema multi-usuário:
1. Cria tabela users no banco
2. Cria usuário admin padrão
3. Atribui todos os dados existentes ao admin
4. Adiciona colunas user_id nas tabelas relevantes

IMPORTANTE: Faça backup do banco antes de rodar!
"""
import sys
import os
from datetime import datetime

# Adiciona path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models import User, Base, get_db_session


def backup_database(db_path='financas.db'):
    """Cria backup do banco de dados"""
    import shutil
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    return backup_path


def migrate_to_multiuser():
    """Executa migração completa para multi-usuário"""
    print("\n" + "="*70)
    print("🔄 MIGRAÇÃO PARA SISTEMA MULTI-USUÁRIO")
    print("="*70 + "\n")
    
    # 1. Backup
    print("📦 Passo 1: Criando backup do banco...")
    backup_path = backup_database()
    
    # 2. Criar/atualizar tabelas
    print("\n🗄️  Passo 2: Atualizando schema do banco...")
    engine = create_engine('sqlite:///financas.db', echo=False)
    Base.metadata.create_all(engine)
    
    # Adicionar colunas user_id nas tabelas existentes
    db = get_db_session()
    
    # Lista de colunas a adicionar
    alterations = [
        ("journal_entries", "user_id", "INTEGER"),
        ("base_parcelas", "user_id", "INTEGER"),
        ("base_padroes", "user_id", "INTEGER"),
        ("base_padroes", "shared", "BOOLEAN DEFAULT 0"),
        ("audit_log", "user_id", "INTEGER"),
    ]
    
    for table, column, col_type in alterations:
        try:
            # Verifica se coluna já existe
            result = db.execute(text(f"PRAGMA table_info({table})"))
            columns = [row[1] for row in result]
            
            if column not in columns:
                db.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                db.commit()
                print(f"   ✅ Coluna {column} adicionada em {table}")
            else:
                print(f"   ℹ️  Coluna {column} já existe em {table}")
        except Exception as e:
            print(f"   ⚠️  Aviso ao adicionar {column} em {table}: {e}")
    
    print("✅ Schema atualizado")
    
    # 3. Criar usuário admin
    print("\n👤 Passo 3: Criando usuário administrador...")
    db = get_db_session()
    
    # Verifica se já existe admin
    admin = db.query(User).filter_by(email='admin@financas.com').first()
    
    if admin:
        print(f"ℹ️  Usuário admin já existe: {admin.email}")
    else:
        admin = User(
            email='admin@financas.com',
            nome='Administrador',
            role='admin',
            ativo=True
        )
        admin.set_password('admin123')  # MUDAR DEPOIS DO PRIMEIRO LOGIN!
        db.add(admin)
        db.commit()
        print(f"✅ Usuário admin criado: {admin.email}")
        print(f"🔑 Senha temporária: admin123")
        print(f"⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
    
    # 4. Atribuir dados existentes ao admin
    print("\n📝 Passo 4: Atribuindo dados existentes ao admin...")
    
    # JournalEntry
    result = db.execute(text("UPDATE journal_entries SET user_id = :user_id WHERE user_id IS NULL"),
                       {'user_id': admin.id})
    db.commit()
    print(f"   ✅ {result.rowcount} transações atribuídas")
    
    # BaseParcelas
    result = db.execute(text("UPDATE base_parcelas SET user_id = :user_id WHERE user_id IS NULL"),
                       {'user_id': admin.id})
    db.commit()
    print(f"   ✅ {result.rowcount} contratos de parcelas atribuídos")
    
    # BasePadrao - mantém NULL para padrões globais compartilhados
    # Não atribui user_id, deixa como padrões globais
    padroes_count = db.execute(text("SELECT COUNT(*) FROM base_padroes WHERE user_id IS NULL")).scalar()
    print(f"   ✅ {padroes_count} padrões globais mantidos (compartilhados)")
    
    # AuditLog
    result = db.execute(text("UPDATE audit_log SET user_id = :user_id WHERE user_id IS NULL"),
                       {'user_id': admin.id})
    db.commit()
    print(f"   ✅ {result.rowcount} registros de auditoria atribuídos")
    
    # 5. Criar índices
    print("\n🔍 Passo 5: Criando índices para performance...")
    try:
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_parcelas_user ON base_parcelas(user_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_padroes_user ON base_padroes(user_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)"))
        db.commit()
        print("✅ Índices criados")
    except Exception as e:
        print(f"⚠️  Aviso: {e}")
    
    # 6. Estatísticas
    print("\n📊 Estatísticas da migração:")
    stats = {
        'usuarios': db.execute(text("SELECT COUNT(*) FROM users")).scalar(),
        'transacoes': db.execute(text("SELECT COUNT(*) FROM journal_entries")).scalar(),
        'parcelas': db.execute(text("SELECT COUNT(*) FROM base_parcelas")).scalar(),
        'padroes': db.execute(text("SELECT COUNT(*) FROM base_padroes")).scalar(),
        'audit_logs': db.execute(text("SELECT COUNT(*) FROM audit_log")).scalar()
    }
    
    for key, value in stats.items():
        print(f"   - {key.capitalize()}: {value}")
    
    print("\n" + "="*70)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70 + "\n")
    
    print("🔐 Credenciais de acesso:")
    print(f"   Email: admin@financas.com")
    print(f"   Senha: admin123")
    print(f"\n⚠️  ATENÇÃO: Altere a senha imediatamente após o primeiro login!\n")
    print(f"📦 Backup salvo em: {backup_path}")
    print(f"💾 Para reverter: mv {backup_path} financas.db\n")
    
    return True


def create_second_user(nome, email, password):
    """Cria segundo usuário (esposa) com dados em branco"""
    print(f"\n👥 Criando segundo usuário: {nome}...")
    
    db = get_db_session()
    
    # Verifica se já existe
    user = db.query(User).filter_by(email=email).first()
    if user:
        print(f"ℹ️  Usuário já existe: {email}")
        return user
    
    # Cria novo usuário
    user = User(
        email=email,
        nome=nome,
        role='user',
        ativo=True
    )
    user.set_password(password)
    db.add(user)
    db.commit()
    
    print(f"✅ Usuário criado: {email}")
    print(f"🔑 Senha: {password}")
    print(f"📊 Este usuário começa com dados em branco")
    
    return user


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migração Multi-Usuário')
    parser.add_argument('--skip-backup', action='store_true', help='Pular criação de backup')
    parser.add_argument('--create-user', nargs=3, metavar=('NOME', 'EMAIL', 'SENHA'),
                       help='Criar usuário adicional')
    
    args = parser.parse_args()
    
    try:
        # Migração principal
        migrate_to_multiuser()
        
        # Criar usuário adicional se solicitado
        if args.create_user:
            nome, email, senha = args.create_user
            create_second_user(nome, email, senha)
        
        print("✅ Processo finalizado com sucesso!\n")
        
    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        print(f"💾 Restaure o backup se necessário: mv financas.db.backup_* financas.db")
        sys.exit(1)
