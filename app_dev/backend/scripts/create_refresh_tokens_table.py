"""
Script para criar tabela refresh_tokens no banco de dados existente
Data: 2026-01-12
"""
import sys
import os
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.domains.users.models import User, RefreshToken
from sqlalchemy import inspect

def create_refresh_tokens_table():
    """
    Cria tabela refresh_tokens se não existir
    """
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"📊 Tabelas existentes: {existing_tables}")
    
    if "refresh_tokens" in existing_tables:
        print("✅ Tabela 'refresh_tokens' já existe")
        return
    
    print("🔨 Criando tabela 'refresh_tokens'...")
    
    # Criar apenas tabela refresh_tokens
    RefreshToken.__table__.create(engine, checkfirst=True)
    
    print("✅ Tabela 'refresh_tokens' criada com sucesso!")
    print("\n📋 Estrutura da tabela:")
    print("   - id (PK)")
    print("   - user_id (FK → users.id)")
    print("   - token_hash (hash bcrypt do refresh token)")
    print("   - expires_at (data/hora de expiração)")
    print("   - created_at (data/hora de criação)")
    print("   - revoked (0=ativo, 1=revogado)")

if __name__ == "__main__":
    print("🚀 Iniciando criação da tabela refresh_tokens...")
    print(f"📂 Database: {engine.url.database}\n")
    
    try:
        create_refresh_tokens_table()
        print("\n✅ Processo concluído com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao criar tabela: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
