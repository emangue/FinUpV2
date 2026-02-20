#!/usr/bin/env python3
"""
Script para copiar TODOS os dados do admin para o usuário teste@email.com
EXCETO journal_entries (transações)

Data: 14/02/2026
Autor: Sistema FinUp
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Criar conexão direta com SQLite (sem depender de config)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Path do banco de dados
DB_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criar engine e session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

# IDs dos usuários
USER_ID_ADMIN = 1
USER_ID_TESTE = 4

# Tabelas que NÃO devem ser copiadas
EXCLUIR_TABELAS = [
    'users',              # Não copiar usuários
    'journal_entries',    # NÃO copiar transações (pedido do usuário)
    'alembic_version',    # Metadados do Alembic
]

def get_all_tables_with_user_id(db):
    """Retorna todas as tabelas que possuem coluna user_id"""
    tables_query = text("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        AND name NOT LIKE 'alembic_%'
        ORDER BY name
    """)
    
    all_tables = db.execute(tables_query).fetchall()
    tables_with_user_id = []
    
    for table in all_tables:
        table_name = table[0]
        if table_name in EXCLUIR_TABELAS:
            continue
            
        try:
            # Verificar se tem coluna user_id
            cols = db.execute(text(f'PRAGMA table_info({table_name})')).fetchall()
            has_user_id = any(col[1] == 'user_id' for col in cols)
            
            if has_user_id:
                tables_with_user_id.append(table_name)
        except Exception as e:
            print(f"⚠️  Erro ao verificar tabela {table_name}: {e}")
    
    return tables_with_user_id

def get_table_columns(db, table_name):
    """Retorna lista de colunas da tabela"""
    cols = db.execute(text(f'PRAGMA table_info({table_name})')).fetchall()
    return [col[1] for col in cols]

def copy_table_data(db, table_name, source_user_id, target_user_id, dry_run=False):
    """Copia dados de uma tabela de um usuário para outro"""
    
    # Contar registros existentes
    count_source = db.execute(
        text(f'SELECT COUNT(*) FROM {table_name} WHERE user_id = :user_id'),
        {'user_id': source_user_id}
    ).scalar()
    
    count_target_before = db.execute(
        text(f'SELECT COUNT(*) FROM {table_name} WHERE user_id = :user_id'),
        {'user_id': target_user_id}
    ).scalar()
    
    if count_source == 0:
        print(f"  ℹ️  {table_name:30} - Nenhum registro do admin para copiar")
        return 0
    
    # Obter colunas (exceto id que é autoincrement)
    columns = get_table_columns(db, table_name)
    columns_without_id = [col for col in columns if col != 'id']
    
    if dry_run:
        print(f"  🔍 {table_name:30} - {count_source:4} registros seriam copiados (target atual: {count_target_before:4})")
        return count_source
    
    # Copiar dados
    columns_str = ', '.join(columns_without_id)
    columns_select = ', '.join([
        f':{col}' if col == 'user_id' else col 
        for col in columns_without_id
    ])
    
    # Buscar dados do admin
    query_select = text(f'SELECT {columns_str} FROM {table_name} WHERE user_id = :source_user_id')
    rows = db.execute(query_select, {'source_user_id': source_user_id}).fetchall()
    
    # Inserir para o usuário teste (substituindo user_id)
    copied = 0
    for row in rows:
        try:
            # Criar dict dos valores
            values = {}
            for i, col in enumerate(columns_without_id):
                if col == 'user_id':
                    values[col] = target_user_id
                else:
                    values[col] = row[i]
            
            # Construir query de insert
            cols_list = ', '.join(columns_without_id)
            placeholders = ', '.join([f':{col}' for col in columns_without_id])
            query_insert = text(f'INSERT INTO {table_name} ({cols_list}) VALUES ({placeholders})')
            
            db.execute(query_insert, values)
            copied += 1
        except Exception as e:
            print(f"    ⚠️  Erro ao copiar registro: {e}")
    
    db.commit()
    
    count_target_after = db.execute(
        text(f'SELECT COUNT(*) FROM {table_name} WHERE user_id = :user_id'),
        {'user_id': target_user_id}
    ).scalar()
    
    print(f"  ✅ {table_name:30} - {copied:4} copiados (antes: {count_target_before:4}, depois: {count_target_after:4})")
    return copied

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Copiar dados do admin para teste@email.com')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem fazer mudanças')
    parser.add_argument('--execute', action='store_true', help='Executar de verdade (obrigatório)')
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Use --dry-run para simular ou --execute para executar de verdade")
        sys.exit(1)
    
    db = SessionLocal()
    
    try:
        # Verificar usuários existem
        admin = db.execute(
            text('SELECT id, email FROM users WHERE id = :id'),
            {'id': USER_ID_ADMIN}
        ).fetchone()
        
        teste = db.execute(
            text('SELECT id, email FROM users WHERE id = :id'),
            {'id': USER_ID_TESTE}
        ).fetchone()
        
        if not admin:
            print(f"❌ Usuário admin (ID={USER_ID_ADMIN}) não encontrado!")
            sys.exit(1)
        
        if not teste:
            print(f"❌ Usuário teste (ID={USER_ID_TESTE}) não encontrado!")
            sys.exit(1)
        
        print("=" * 80)
        print("📋 CÓPIA DE DADOS DO ADMIN PARA TESTE@EMAIL.COM")
        print("=" * 80)
        print(f"Origem:  {admin[1]} (ID={admin[0]})")
        print(f"Destino: {teste[1]} (ID={teste[0]})")
        print(f"Modo:    {'DRY-RUN (simulação)' if args.dry_run else 'EXECUÇÃO REAL'}")
        print("=" * 80)
        print()
        
        # Obter tabelas com user_id
        tables = get_all_tables_with_user_id(db)
        
        if not tables:
            print("⚠️  Nenhuma tabela com user_id encontrada!")
            return
        
        print(f"📊 Tabelas a processar: {len(tables)}")
        print()
        
        total_copied = 0
        
        for table in tables:
            copied = copy_table_data(db, table, USER_ID_ADMIN, USER_ID_TESTE, args.dry_run)
            total_copied += copied
        
        print()
        print("=" * 80)
        if args.dry_run:
            print(f"✅ DRY-RUN COMPLETO - {total_copied} registros seriam copiados")
            print(f"💡 Execute com --execute para aplicar de verdade")
        else:
            print(f"✅ CÓPIA COMPLETA - {total_copied} registros copiados com sucesso!")
            print(f"📝 Tabelas processadas: {len(tables)}")
            print(f"❌ Tabelas excluídas: {', '.join(EXCLUIR_TABELAS)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    main()
