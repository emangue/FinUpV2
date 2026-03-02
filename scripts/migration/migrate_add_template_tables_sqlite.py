#!/usr/bin/env python3
"""
Migration: Cria base_grupos_template e base_marcacoes_template (SQLite).
Para uso local quando alembic está configurado apenas para PostgreSQL.

Uso: cd app_dev/backend && python ../../scripts/migration/migrate_add_template_tables_sqlite.py
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

    # Verificar se já existe
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='base_grupos_template'")
    if cur.fetchone():
        print("⚠️  Tabelas template já existem. Nada a fazer.")
        conn.close()
        return

    print("📦 Criando base_grupos_template...")
    cur.execute("""
        CREATE TABLE base_grupos_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_grupo VARCHAR(100) NOT NULL UNIQUE,
            tipo_gasto_padrao VARCHAR(50) NOT NULL,
            categoria_geral VARCHAR(50) NOT NULL,
            cor VARCHAR(7)
        )
    """)

    print("📦 Criando base_marcacoes_template...")
    cur.execute("""
        CREATE TABLE base_marcacoes_template (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            GRUPO VARCHAR(100) NOT NULL,
            SUBGRUPO VARCHAR(100) NOT NULL,
            UNIQUE(GRUPO, SUBGRUPO)
        )
    """)

    print("📝 Populando base_grupos_template de base_grupos_config...")
    cur.execute("""
        INSERT INTO base_grupos_template (nome_grupo, tipo_gasto_padrao, categoria_geral, cor)
        SELECT nome_grupo, tipo_gasto_padrao, categoria_geral, cor FROM base_grupos_config
    """)

    print("📝 Populando base_marcacoes_template de base_marcacoes...")
    cur.execute("""
        INSERT OR IGNORE INTO base_marcacoes_template (GRUPO, SUBGRUPO)
        SELECT DISTINCT GRUPO, SUBGRUPO FROM base_marcacoes
    """)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM base_grupos_template")
    n_grupos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM base_marcacoes_template")
    n_marc = cur.fetchone()[0]
    print(f"✅ Concluído: {n_grupos} grupos, {n_marc} marcações no template")
    conn.close()


if __name__ == "__main__":
    main()
