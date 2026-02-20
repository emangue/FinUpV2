#!/usr/bin/env python3
"""
Sincroniza investimentos do SQLite local para PostgreSQL do servidor.

Substitui investimentos_portfolio, investimentos_historico e investimentos_planejamento
no servidor pelos dados do local (que tem os valores corretos).

Uso:
    cd app_dev/backend && python ../../scripts/migration/sync_investimentos_local_para_servidor.py

    # Dry-run (sem alterar):
    python sync_investimentos_local_para_servidor.py --dry-run

    # Sem confirmação (para scripts/CI):
    python sync_investimentos_local_para_servidor.py --yes
"""
import sqlite3
import psycopg2
from psycopg2 import extras
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
SQLITE_PATH = ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"

# OBRIGATÓRIO: usar variável de ambiente (nunca hardcodar senha)
import os
POSTGRES_DSN = os.getenv("PROD_DATABASE_URL") or os.getenv("DATABASE_URL")
if not POSTGRES_DSN or "postgresql://" not in POSTGRES_DSN:
    print("❌ Defina PROD_DATABASE_URL ou DATABASE_URL (ex: export PROD_DATABASE_URL='postgresql://user:senha@host:5432/db')")
    sys.exit(1)

# Colunas que no SQLite são 0/1 mas no PostgreSQL são boolean
BOOLEAN_COLUMNS = {
    "investimentos_portfolio": ["ativo"],
    "investimentos_historico": [],
    "investimentos_planejamento": [],
}


def get_columns(cursor, table: str):
    cursor.execute(f"PRAGMA table_info({table})")
    return [col[1] for col in cursor.fetchall()]


def sync_table(sqlite_conn, pg_conn, table: str, dry_run: bool) -> int:
    """Sincroniza uma tabela: truncate no PG e insert a partir do SQLite."""
    sqlite_cur = sqlite_conn.cursor()
    pg_cur = pg_conn.cursor()

    columns = get_columns(sqlite_cur, table)
    if not columns:
        print(f"  ⚠️  {table}: não encontrada no SQLite")
        return 0

    sqlite_cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = sqlite_cur.fetchone()[0]
    if count == 0:
        print(f"  ⏭️  {table}: vazia no local, pulando")
        return 0

    if dry_run:
        print(f"  🔍 [DRY-RUN] {table}: {count} registros seriam copiados")
        return count

    # Buscar dados
    cols_str = ", ".join(columns)
    sqlite_cur.execute(f"SELECT {cols_str} FROM {table}")
    rows = sqlite_cur.fetchall()

    # Converter colunas boolean (SQLite 0/1 -> PostgreSQL True/False)
    bool_cols = BOOLEAN_COLUMNS.get(table, [])
    bool_idxs = [columns.index(c) for c in bool_cols if c in columns]
    rows_conv = []
    for row in rows:
        r = list(row)
        for i in bool_idxs:
            if r[i] is not None:
                r[i] = bool(r[i])
        rows_conv.append(tuple(r))

    # Truncate CASCADE (historico depende de portfolio; planejamento é independente)
    pg_cur.execute(f"TRUNCATE TABLE {table} CASCADE")
    pg_conn.commit()

    # Insert
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    extras.execute_batch(pg_cur, insert_sql, rows_conv, page_size=500)
    pg_conn.commit()

    # Validar
    pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
    pg_count = pg_cur.fetchone()[0]
    if pg_count != count:
        raise RuntimeError(f"{table}: contagem divergente - local={count}, servidor={pg_count}")

    print(f"  ✅ {table}: {count} registros sincronizados")
    return count


def reset_sequences(pg_conn):
    """Reseta sequences do PostgreSQL."""
    cur = pg_conn.cursor()
    for table, col in [
        ("investimentos_portfolio", "id"),
        ("investimentos_historico", "id"),
        ("investimentos_planejamento", "id"),
    ]:
        try:
            cur.execute(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', '{col}'),
                    COALESCE((SELECT MAX({col}) FROM {table}), 1),
                    true
                )
            """)
            pg_conn.commit()
            print(f"  ✅ Sequence {table}.{col} resetada")
        except Exception as e:
            print(f"  ⚠️  {table}.{col}: {e}")


def main():
    dry_run = "--dry-run" in sys.argv
    skip_confirm = "--yes" in sys.argv or "-y" in sys.argv

    print("=" * 70)
    print("🔄 SYNC INVESTIMENTOS: Local → Servidor")
    print("=" * 70)
    print(f"📂 Local:    {SQLITE_PATH}")
    print(f"🐘 Servidor: {POSTGRES_DSN.split('@')[-1] if '@' in POSTGRES_DSN else '...'}")
    print("=" * 70)

    if not dry_run and not skip_confirm:
        confirm = input("\n⚠️  Isso vai SUBSTITUIR investimentos no servidor. Continuar? (sim/não): ")
        if confirm.lower() not in ("sim", "s", "yes", "y"):
            print("❌ Cancelado")
            return 1

    if not SQLITE_PATH.exists():
        print(f"❌ SQLite não encontrado: {SQLITE_PATH}")
        return 1

    try:
        sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
        pg_conn = psycopg2.connect(POSTGRES_DSN)
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return 1

    try:
        # Ordem: portfolio, historico (historico referencia portfolio), planejamento
        print("\n📦 Sincronizando...")
        sync_table(sqlite_conn, pg_conn, "investimentos_portfolio", dry_run)
        sync_table(sqlite_conn, pg_conn, "investimentos_historico", dry_run)
        sync_table(sqlite_conn, pg_conn, "investimentos_planejamento", dry_run)

        if not dry_run:
            print("\n🔄 Resetando sequences...")
            reset_sequences(pg_conn)

        print("\n✅ Sync concluído!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        pg_conn.rollback()
        import traceback
        traceback.print_exc()
        return 1
    finally:
        sqlite_conn.close()
        pg_conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
