#!/usr/bin/env python3
"""
Migration: Adiciona user_id e is_padrao em base_grupos_config, user_id em base_marcacoes (SQLite).
Executar APÓS migrate_add_template_tables_sqlite.py.

Uso: cd app_dev/backend && python ../../scripts/migration/migrate_user_id_grupos_sqlite.py
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

    # Verificar se user_id já existe
    cur.execute("PRAGMA table_info(base_grupos_config)")
    cols = [r[1] for r in cur.fetchall()]
    if "user_id" in cols:
        print("⚠️  base_grupos_config já tem user_id. Nada a fazer.")
        conn.close()
        return

    print("📦 Adicionando user_id e is_padrao em base_grupos_config...")
    cur.execute("ALTER TABLE base_grupos_config ADD COLUMN user_id INTEGER")
    cur.execute("ALTER TABLE base_grupos_config ADD COLUMN is_padrao INTEGER DEFAULT 0")
    cur.execute("UPDATE base_grupos_config SET user_id = 1, is_padrao = 1 WHERE user_id IS NULL")

    # Recriar tabela para UNIQUE(user_id, nome_grupo) — SQLite não permite ALTER para mudar constraints
    cur.execute("PRAGMA table_info(base_grupos_config)")
    # Criar nova tabela
    cur.execute("""
        CREATE TABLE base_grupos_config_new (
            id INTEGER PRIMARY KEY,
            nome_grupo VARCHAR NOT NULL,
            tipo_gasto_padrao VARCHAR NOT NULL,
            categoria_geral VARCHAR NOT NULL,
            cor VARCHAR(7),
            user_id INTEGER NOT NULL DEFAULT 1,
            is_padrao INTEGER NOT NULL DEFAULT 0,
            UNIQUE(user_id, nome_grupo)
        )
    """)
    cur.execute("""
        INSERT INTO base_grupos_config_new (id, nome_grupo, tipo_gasto_padrao, categoria_geral, cor, user_id, is_padrao)
        SELECT id, nome_grupo, tipo_gasto_padrao, categoria_geral, cor, COALESCE(user_id, 1), COALESCE(is_padrao, 1)
        FROM base_grupos_config
    """)
    cur.execute("DROP TABLE base_grupos_config")
    cur.execute("ALTER TABLE base_grupos_config_new RENAME TO base_grupos_config")
    cur.execute("CREATE INDEX ix_base_grupos_config_user_id ON base_grupos_config(user_id)")

    print("📦 Adicionando user_id em base_marcacoes...")
    cur.execute("PRAGMA table_info(base_marcacoes)")
    cols_m = [r[1] for r in cur.fetchall()]
    if "user_id" not in cols_m:
        cur.execute("ALTER TABLE base_marcacoes ADD COLUMN user_id INTEGER")
        cur.execute("UPDATE base_marcacoes SET user_id = 1 WHERE user_id IS NULL")

        # Recriar com UNIQUE(user_id, GRUPO, SUBGRUPO)
        cur.execute("""
            CREATE TABLE base_marcacoes_new (
                id INTEGER PRIMARY KEY,
                GRUPO VARCHAR(100) NOT NULL,
                SUBGRUPO VARCHAR(100) NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 1,
                UNIQUE(user_id, GRUPO, SUBGRUPO)
            )
        """)
        cur.execute("""
            INSERT OR IGNORE INTO base_marcacoes_new (id, GRUPO, SUBGRUPO, user_id)
            SELECT id, GRUPO, SUBGRUPO, COALESCE(user_id, 1) FROM base_marcacoes
        """)
        cur.execute("DROP TABLE base_marcacoes")
        cur.execute("ALTER TABLE base_marcacoes_new RENAME TO base_marcacoes")
        cur.execute("CREATE INDEX ix_base_marcacoes_user_id ON base_marcacoes(user_id)")

    conn.commit()
    print("✅ Concluído: user_id adicionado em base_grupos_config e base_marcacoes")
    conn.close()


if __name__ == "__main__":
    main()
