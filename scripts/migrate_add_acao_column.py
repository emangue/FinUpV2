#!/usr/bin/env python3
"""
Migration: Adiciona coluna 'acao' em transacoes_exclusao
Versão: 1.0.0
Data: 04/01/2026

Objetivo:
- Adicionar coluna 'acao' (VARCHAR) com valores: 'EXCLUIR' ou 'IGNORAR'
- Default: 'EXCLUIR' (preserva comportamento atual)
- Todos os registros existentes ficam como 'EXCLUIR'
- Não mexe no histórico de transações
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_migration():
    """Executa migração para adicionar coluna acao"""
    
    # Determinar caminho do banco
    db_paths = [
        'app_dev/backend/database/financas_dev.db',
        'app/financas.db',
        'database/financas_dev.db'
    ]
    
    db_path = None
    for path in db_paths:
        full_path = os.path.join(project_root, path)
        if os.path.exists(full_path):
            db_path = full_path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        print(f"   Procurei em: {db_paths}")
        return False
    
    print(f"📂 Usando banco: {db_path}")
    
    # Backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"💾 Criando backup: {backup_path}")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print("✅ Backup criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False
    
    # Conectar ao banco
    print("\n🔧 Iniciando migração...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='transacoes_exclusao'
        """)
        
        if not cursor.fetchone():
            print("⚠️  Tabela transacoes_exclusao não existe")
            print("   Esta migração será executada quando a tabela for criada")
            conn.close()
            return True
        
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(transacoes_exclusao)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'acao' in columns:
            print("ℹ️  Coluna 'acao' já existe - nada a fazer")
            conn.close()
            return True
        
        # Adicionar coluna
        print("📝 Adicionando coluna 'acao'...")
        cursor.execute("""
            ALTER TABLE transacoes_exclusao 
            ADD COLUMN acao VARCHAR(10) DEFAULT 'EXCLUIR'
        """)
        
        # Atualizar registros existentes para garantir default
        cursor.execute("""
            UPDATE transacoes_exclusao 
            SET acao = 'EXCLUIR' 
            WHERE acao IS NULL
        """)
        
        rows_updated = cursor.rowcount
        
        conn.commit()
        
        print(f"✅ Coluna 'acao' adicionada com sucesso")
        print(f"✅ {rows_updated} registros existentes configurados como 'EXCLUIR'")
        print(f"\n📊 Valores permitidos:")
        print(f"   - 'EXCLUIR': Remove da importação (comportamento atual)")
        print(f"   - 'IGNORAR': Importa mas marca IgnorarDashboard=True")
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM transacoes_exclusao WHERE acao = 'EXCLUIR'")
        count = cursor.fetchone()[0]
        print(f"\n✅ Total de exclusões ativas: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        conn.rollback()
        conn.close()
        
        # Restaurar backup
        print("🔄 Restaurando backup...")
        try:
            shutil.copy2(backup_path, db_path)
            print("✅ Backup restaurado")
        except Exception as e2:
            print(f"❌ Erro ao restaurar backup: {e2}")
        
        return False


if __name__ == '__main__':
    print("\n" + "="*70)
    print("⚠️  MIGRAÇÃO: Adicionar coluna 'acao' em transacoes_exclusao")
    print("="*70)
    print("\nMudanças:")
    print("  1. Adiciona coluna 'acao' (VARCHAR)")
    print("  2. Valores: 'EXCLUIR' (default) ou 'IGNORAR'")
    print("  3. Todos os registros existentes: 'EXCLUIR'")
    print("  4. NÃO mexe no histórico de transações")
    print("\nBackup automático será criado.")
    
    resposta = input("\n⚠️  Deseja continuar? (sim/não): ")
    
    if resposta.lower() in ['sim', 's', 'yes', 'y']:
        sucesso = run_migration()
        sys.exit(0 if sucesso else 1)
    else:
        print("\n❌ Migração cancelada pelo usuário")
        sys.exit(1)
