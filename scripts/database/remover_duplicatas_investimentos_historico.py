#!/usr/bin/env python3
"""
Remove duplicatas em investimentos_historico (local SQLite).

Mantém apenas 1 registro por (investimento_id, anomes), deletando os demais.

Uso:
    cd app_dev/backend && python ../../scripts/database/remover_duplicatas_investimentos_historico.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"


def main():
    if not DB_PATH.exists():
        print(f"❌ Banco não encontrado: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Contar duplicatas antes
    cur.execute("""
        SELECT COUNT(*) FROM investimentos_historico h1
        WHERE EXISTS (
            SELECT 1 FROM investimentos_historico h2
            WHERE h1.investimento_id = h2.investimento_id
              AND h1.anomes = h2.anomes
              AND h1.id > h2.id
        )
    """)
    duplicatas = cur.fetchone()[0]

    if duplicatas == 0:
        print("✅ Nenhuma duplicata encontrada.")
        conn.close()
        return 0

    print(f"📊 Duplicatas a remover: {duplicatas}")

    # Deletar duplicatas (manter o de menor id por grupo)
    # Criar tabela temporária com ids a manter
    cur.execute("""
        CREATE TEMP TABLE ids_manter AS
        SELECT MIN(id) as id FROM investimentos_historico
        GROUP BY investimento_id, anomes
    """)
    cur.execute("""
        DELETE FROM investimentos_historico
        WHERE id NOT IN (SELECT id FROM ids_manter)
    """)
    deleted = cur.rowcount
    conn.commit()

    print(f"✅ Removidos {deleted} registros duplicados.")

    # Validar
    cur.execute("""
        SELECT investimento_id, anomes, COUNT(*) as cnt
        FROM investimentos_historico
        GROUP BY investimento_id, anomes
        HAVING COUNT(*) > 1
    """)
    restantes = cur.fetchall()
    if restantes:
        print(f"⚠️  Ainda há {len(restantes)} grupos com duplicatas!")
    else:
        print("✅ Nenhuma duplicata restante.")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
