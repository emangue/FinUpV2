#!/usr/bin/env python3
"""
Migration: Adiciona fonte e is_demo em journal_entries (SQLite).
Para onboarding modo demo.

Uso: cd app_dev/backend && python ../../scripts/migration/migrate_fonte_is_demo_sqlite.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"

if not DB_PATH.exists():
    print(f"❌ Banco não encontrado: {DB_PATH}")
    sys.exit(1)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(journal_entries)")
    cols = [r[1] for r in cur.fetchall()]

    if "fonte" in cols:
        print("⚠️  journal_entries já tem fonte e is_demo. Nada a fazer.")
        conn.close()
        return

    print("📦 Adicionando fonte e is_demo em journal_entries...")
    cur.execute("ALTER TABLE journal_entries ADD COLUMN fonte VARCHAR")
    cur.execute("ALTER TABLE journal_entries ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0")
    cur.execute("CREATE INDEX ix_journal_entries_fonte ON journal_entries(fonte)")
    conn.commit()
    print("✅ Migração concluída.")
    conn.close()


if __name__ == "__main__":
    main()
