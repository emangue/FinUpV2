#!/usr/bin/env python3
"""
Copia base_grupos_template e base_marcacoes_template para usuários existentes (2, 3, 4...).
Executar APÓS migrations de template e user_id.

Uso: cd app_dev/backend && python ../../scripts/migration/copiar_template_para_usuarios_existentes.py
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

    cur.execute("SELECT id FROM users ORDER BY id")
    user_ids = [r[0] for r in cur.fetchall()]
    # Pular user_id=1 (já tem dados da migração)
    dest_users = [u for u in user_ids if u != 1]

    if not dest_users:
        print("ℹ️  Apenas user_id=1 existe. Nada a copiar.")
        conn.close()
        return

    print(f"📋 Usuários a popular: {dest_users}")

    for user_id in dest_users:
        # Grupos
        cur.execute("SELECT COUNT(*) FROM base_grupos_config WHERE user_id = ?", (user_id,))
        if cur.fetchone()[0] > 0:
            print(f"   user_id={user_id}: já tem grupos, pulando")
            continue

        cur.execute("""
            INSERT INTO base_grupos_config (nome_grupo, tipo_gasto_padrao, categoria_geral, cor, user_id, is_padrao)
            SELECT nome_grupo, tipo_gasto_padrao, categoria_geral, cor, ?, 1
            FROM base_grupos_template
        """, (user_id,))

        cur.execute("""
            INSERT OR IGNORE INTO base_marcacoes (GRUPO, SUBGRUPO, user_id)
            SELECT GRUPO, SUBGRUPO, ?
            FROM base_marcacoes_template
        """, (user_id,))

        cur.execute("SELECT COUNT(*) FROM base_grupos_config WHERE user_id = ?", (user_id,))
        n_g = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM base_marcacoes WHERE user_id = ?", (user_id,))
        n_m = cur.fetchone()[0]
        print(f"   user_id={user_id}: {n_g} grupos, {n_m} marcações")

    conn.commit()
    print("✅ Concluído")
    conn.close()


if __name__ == "__main__":
    main()
