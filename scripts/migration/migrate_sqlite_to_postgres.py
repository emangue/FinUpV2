#!/usr/bin/env python3
"""
Script de Migração Completa SQLite → PostgreSQL

Migra TODOS os dados do SQLite local para PostgreSQL de produção.
Preserva integridade referencial e valida após migração.

Uso:
    python migrate_sqlite_to_postgres.py [--dry-run]
"""

import sqlite3
import psycopg2
from psycopg2 import extras
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

# Configurações
SQLITE_PATH = Path(__file__).parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"
POSTGRES_DSN = "postgresql://finup_user:FinUp2026SecurePass@148.230.78.91:5432/finup_db"

# Tabelas a migrar (ordem importa - respeita foreign keys)
TABLES_TO_MIGRATE = [
    # Tabelas base (sem dependências)
    "users",
    "base_marcacoes",
    "base_grupos_config",
    "cartoes",
    "bank_format_compatibility",
    "screen_visibility",
    "generic_classification_rules",
    "error_codes",
    "estabelecimento_logo",
    
    # Tabelas com dependências
    "journal_entries",  # Depende de users
    "base_parcelas",
    "transacoes_exclusao",
    "ignorar_estabelecimentos",
    
    # Budget
    "budget_geral",
    "budget_geral_historico",
    "budget_categoria_config",
    "budget_planning",
    
    # Investimentos
    "investimentos_portfolio",
    "investimentos_historico",
    "investimentos_aportes_extraordinarios",
    "investimentos_cenarios",
    "investimentos_planejamento",
    
    # Upload e auth
    "upload_history",
    "refresh_tokens",
    "user_relationships",
    
    # Audit
    "audit_log",
]

class MigrationStats:
    def __init__(self):
        self.tables_migrated = 0
        self.total_rows_migrated = 0
        self.errors = []
        self.start_time = datetime.now()
    
    def add_table(self, table: str, rows: int):
        self.tables_migrated += 1
        self.total_rows_migrated += rows
        print(f"  ✅ {table}: {rows:,} registros")
    
    def add_error(self, table: str, error: str):
        self.errors.append((table, error))
        print(f"  ⚠️  {table}: {error}")
    
    def print_summary(self):
        duration = (datetime.now() - self.start_time).total_seconds()
        print("\n" + "="*70)
        print("📊 RESUMO DA MIGRAÇÃO")
        print("="*70)
        print(f"Tabelas migradas: {self.tables_migrated}/{len(TABLES_TO_MIGRATE)}")
        print(f"Total de registros: {self.total_rows_migrated:,}")
        print(f"Tempo total: {duration:.2f}s")
        if self.errors:
            print(f"\n⚠️  Erros encontrados: {len(self.errors)}")
            for table, error in self.errors:
                print(f"  - {table}: {error}")
        else:
            print("\n✅ Migração concluída sem erros!")
        print("="*70)


def get_table_columns(cursor, table: str) -> List[str]:
    """Busca nomes das colunas de uma tabela"""
    cursor.execute(f"PRAGMA table_info({table})")
    return [col[1] for col in cursor.fetchall()]


def migrate_table(
    sqlite_conn,
    postgres_conn,
    table: str,
    stats: MigrationStats,
    dry_run: bool = False
) -> bool:
    """Migra uma tabela do SQLite para PostgreSQL"""
    
    try:
        sqlite_cur = sqlite_conn.cursor()
        postgres_cur = postgres_conn.cursor()
        
        # Buscar colunas
        columns = get_table_columns(sqlite_cur, table)
        if not columns:
            stats.add_error(table, "Tabela não encontrada no SQLite")
            return False
        
        # Contar registros no SQLite
        sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cur.fetchone()[0]
        
        if count == 0:
            print(f"  ⏭️  {table}: Vazia, pulando...")
            return True
        
        # Buscar todos os dados
        columns_str = ", ".join(columns)
        sqlite_cur.execute(f"SELECT {columns_str} FROM {table}")
        rows = sqlite_cur.fetchall()
        
        if dry_run:
            print(f"  🔍 [DRY-RUN] {table}: {count:,} registros seriam migrados")
            return True
        
        # Limpar tabela no PostgreSQL
        postgres_cur.execute(f"TRUNCATE TABLE {table} CASCADE")
        
        # Inserir dados no PostgreSQL
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        extras.execute_batch(postgres_cur, insert_sql, rows, page_size=1000)
        postgres_conn.commit()
        
        # Validar migração
        postgres_cur.execute(f"SELECT COUNT(*) FROM {table}")
        pg_count = postgres_cur.fetchone()[0]
        
        if pg_count != count:
            stats.add_error(table, f"Contagens diferentes: SQLite={count}, PostgreSQL={pg_count}")
            return False
        
        stats.add_table(table, count)
        return True
        
    except Exception as e:
        stats.add_error(table, str(e))
        postgres_conn.rollback()
        return False


def reset_sequences(postgres_conn):
    """Reseta sequences do PostgreSQL após migração"""
    print("\n🔄 Resetando sequences...")
    cursor = postgres_conn.cursor()
    
    # Buscar todas as sequences
    cursor.execute("""
        SELECT 
            c.relname as sequence_name,
            t.relname as table_name,
            a.attname as column_name
        FROM pg_class c
        JOIN pg_depend d ON d.objid = c.oid
        JOIN pg_class t ON d.refobjid = t.oid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
        WHERE c.relkind = 'S'
        AND t.relname IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
    """)
    
    sequences = cursor.fetchall()
    
    for seq_name, table_name, col_name in sequences:
        try:
            cursor.execute(f"""
                SELECT setval('{seq_name}', 
                    COALESCE((SELECT MAX({col_name}) FROM {table_name}), 1), 
                    true
                )
            """)
            postgres_conn.commit()
            print(f"  ✅ {seq_name} → {table_name}.{col_name}")
        except Exception as e:
            print(f"  ⚠️  Erro ao resetar {seq_name}: {e}")


def validate_migration(sqlite_conn, postgres_conn) -> Dict[str, Tuple[int, int]]:
    """Valida migração comparando contagens"""
    print("\n🔍 Validando migração...")
    
    sqlite_cur = sqlite_conn.cursor()
    postgres_cur = postgres_conn.cursor()
    
    validation = {}
    all_ok = True
    
    for table in TABLES_TO_MIGRATE:
        try:
            sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cur.fetchone()[0]
            
            postgres_cur.execute(f"SELECT COUNT(*) FROM {table}")
            postgres_count = postgres_cur.fetchone()[0]
            
            validation[table] = (sqlite_count, postgres_count)
            
            if sqlite_count != postgres_count:
                print(f"  ❌ {table}: SQLite={sqlite_count}, PostgreSQL={postgres_count}")
                all_ok = False
            else:
                print(f"  ✅ {table}: {sqlite_count:,} registros OK")
                
        except Exception as e:
            print(f"  ⚠️  {table}: Erro na validação - {e}")
            all_ok = False
    
    return validation, all_ok


def main():
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🔍 MODO DRY-RUN - Nenhuma alteração será feita\n")
    
    print("="*70)
    print("🚀 MIGRAÇÃO COMPLETA: SQLite → PostgreSQL")
    print("="*70)
    print(f"📂 SQLite:     {SQLITE_PATH}")
    print(f"🐘 PostgreSQL: 148.230.78.91:5432/finup_db")
    print(f"📊 Tabelas:    {len(TABLES_TO_MIGRATE)}")
    print("="*70)
    
    if not dry_run:
        confirm = input("\n⚠️  Esta operação vai SOBRESCREVER dados no PostgreSQL. Continuar? (sim/não): ")
        if confirm.lower() not in ['sim', 's', 'yes', 'y']:
            print("❌ Migração cancelada pelo usuário")
            return 1
    
    # Conectar aos bancos
    print("\n📡 Conectando aos bancos de dados...")
    try:
        sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
        postgres_conn = psycopg2.connect(POSTGRES_DSN)
        print("  ✅ Conexões estabelecidas")
    except Exception as e:
        print(f"  ❌ Erro ao conectar: {e}")
        return 1
    
    # Migrar tabelas
    print("\n📦 Migrando tabelas...")
    stats = MigrationStats()
    
    for table in TABLES_TO_MIGRATE:
        migrate_table(sqlite_conn, postgres_conn, table, stats, dry_run)
    
    # Resetar sequences (só se não for dry-run)
    if not dry_run:
        reset_sequences(postgres_conn)
        
        # Validar migração
        validation, all_ok = validate_migration(sqlite_conn, postgres_conn)
    
    # Fechar conexões
    sqlite_conn.close()
    postgres_conn.close()
    
    # Resumo
    stats.print_summary()
    
    return 0 if not stats.errors else 1


if __name__ == "__main__":
    sys.exit(main())
