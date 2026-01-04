#!/usr/bin/env python3
"""
Migration: Criar tabela preview_transacoes

Cria tabela temporária para armazenar preview de uploads antes da confirmação

Run: python scripts/migrate_create_preview_table.py
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Caminho do banco de dados
DB_PATH = Path(__file__).parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"

def criar_tabela_preview():
    """Cria tabela preview_transacoes"""
    
    print(f"🔍 Conectando ao banco: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Erro: Banco de dados não encontrado em {DB_PATH}")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verifica se tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='preview_transacoes'
        """)
        
        if cursor.fetchone():
            print("⚠️  Tabela 'preview_transacoes' já existe")
            resposta = input("Deseja recriar a tabela? (s/N): ").lower()
            if resposta != 's':
                print("❌ Operação cancelada")
                conn.close()
                return
            
            # Drop tabela existente
            cursor.execute("DROP TABLE preview_transacoes")
            print("🗑️  Tabela existente removida")
        
        # Criar tabela
        cursor.execute("""
            CREATE TABLE preview_transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                banco TEXT,
                cartao TEXT,
                nome_arquivo TEXT,
                mes_fatura TEXT,
                data TEXT,
                lancamento TEXT,
                valor REAL,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Criar índices
        cursor.execute("CREATE INDEX idx_preview_session ON preview_transacoes(session_id)")
        cursor.execute("CREATE INDEX idx_preview_user ON preview_transacoes(user_id)")
        
        conn.commit()
        print("✅ Tabela 'preview_transacoes' criada com sucesso")
        print("✅ Índices criados: idx_preview_session, idx_preview_user")
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(preview_transacoes)")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura da tabela:")
        for col in colunas:
            print(f"  - {col[1]} ({col[2]})")
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao criar tabela: {e}")
        conn.rollback()
        sys.exit(1)
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION: Criar tabela preview_transacoes")
    print("=" * 60)
    print()
    
    criar_tabela_preview()
    
    print()
    print("=" * 60)
    print("✅ Migration concluída")
    print("=" * 60)
