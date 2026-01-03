#!/usr/bin/env python3
"""
Migração: Adiciona tabela UserRelationship para contas conectadas

Cria estrutura para permitir que usuários conectem suas contas e vejam
dados separados ou consolidados.

Data: 2025-12-28
Versão: 3.0.1
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models import get_db_session
import shutil
from datetime import datetime


def backup_database():
    """Cria backup antes da migração"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"financas.db.backup_{timestamp}"
    
    if os.path.exists('financas.db'):
        shutil.copy2('financas.db', backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    else:
        print("⚠️  Banco de dados não encontrado")
        return None


def migrate_add_user_relationships():
    """Adiciona tabela user_relationships"""
    print("\n" + "="*70)
    print("🔄 MIGRAÇÃO: Adiciona User Relationships (Contas Conectadas)")
    print("="*70)
    
    # Backup
    backup_path = backup_database()
    if not backup_path:
        print("❌ Falha ao criar backup. Abortando migração.")
        return False
    
    db = get_db_session()
    
    try:
        # Verificar se tabela já existe
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_relationships'
        """)).fetchone()
        
        if result:
            print("\n⚠️  Tabela 'user_relationships' já existe!")
            return True
        
        # Criar tabela user_relationships
        print("\n📋 Criando tabela 'user_relationships'...")
        db.execute(text("""
            CREATE TABLE user_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                connected_user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                view_consolidated INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accepted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (connected_user_id) REFERENCES users (id)
            )
        """))
        
        # Criar índices
        print("📊 Criando índices...")
        db.execute(text("""
            CREATE INDEX idx_user_relationships_user_id 
            ON user_relationships(user_id)
        """))
        
        db.execute(text("""
            CREATE INDEX idx_user_relationships_connected_user_id 
            ON user_relationships(connected_user_id)
        """))
        
        db.execute(text("""
            CREATE INDEX idx_user_relationships_status 
            ON user_relationships(status)
        """))
        
        db.commit()
        
        print("\n✅ Tabela 'user_relationships' criada com sucesso!")
        
        # Verificar criação
        print("\n🔍 Verificando estrutura...")
        result = db.execute(text("PRAGMA table_info(user_relationships)")).fetchall()
        
        print("\n📋 Colunas criadas:")
        for col in result:
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n" + "="*70)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"\n📦 Backup disponível em: {backup_path}")
        print("\n🎯 Funcionalidades habilitadas:")
        print("   - Conexão entre contas de usuários")
        print("   - Solicitação e aceitação de conexões")
        print("   - Toggle de visão consolidada")
        print("   - Visão separada (apenas seus dados)")
        print("   - Visão consolidada (seus dados + dados de conta conectada)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante migração: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n🔄 Para reverter, use: cp {backup_path} financas.db")
        return False
    
    finally:
        db.close()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("⚠️  ATENÇÃO: Esta migração irá adicionar tabela user_relationships")
    print("="*70)
    print("\nMudanças:")
    print("  1. Criar tabela user_relationships")
    print("  2. Criar índices para performance")
    print("  3. Habilitar sistema de contas conectadas")
    print("\nUm backup será criado automaticamente.")
    
    resposta = input("\n⚠️  Deseja continuar? (sim/não): ")
    
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        sucesso = migrate_add_user_relationships()
        sys.exit(0 if sucesso else 1)
    else:
        print("\n❌ Migração cancelada pelo usuário")
        sys.exit(1)
