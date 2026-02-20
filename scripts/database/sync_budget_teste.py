#!/usr/bin/env python3
"""
Sincroniza budget_planning para o usuário teste (teste@email.com, user_id=4).
Cria linhas com valor_planejado=0 para todos os (grupo, mês) que têm transações,
para que as metas apareçam na tela com valor realizado.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent.parent / "app_dev" / "backend" / "database" / "financas_dev.db"
USER_ID_TESTE = 4  # teste@email.com


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Buscar (grupo, mes_fatura) distintos do usuário teste
    cur.execute("""
        SELECT DISTINCT GRUPO, MesFatura
        FROM journal_entries
        WHERE user_id = ? AND GRUPO IS NOT NULL AND GRUPO != '' AND MesFatura IS NOT NULL
    """, (USER_ID_TESTE,))
    rows = cur.fetchall()

    criados = 0
    now = datetime.now().isoformat()
    for row in rows:
        grupo, mes_fatura = row[0], row[1]
        if not grupo or not mes_fatura or len(mes_fatura) != 6:
            continue
        mes_referencia = f"{mes_fatura[:4]}-{mes_fatura[4:6]}"

        cur.execute("""
            SELECT 1 FROM budget_planning
            WHERE user_id = ? AND grupo = ? AND mes_referencia = ?
        """, (USER_ID_TESTE, grupo, mes_referencia))
        if cur.fetchone():
            continue

        cur.execute("""
            INSERT INTO budget_planning (user_id, grupo, mes_referencia, valor_planejado, valor_medio_3_meses, ativo, created_at, updated_at)
            VALUES (?, ?, ?, 0.0, 0.0, 1, ?, ?)
        """, (USER_ID_TESTE, grupo, mes_referencia, now, now))
        criados += 1
        print(f"  ➕ {grupo} {mes_referencia}")

    conn.commit()
    conn.close()
    print(f"\n✅ {criados} linhas de budget criadas para teste@email.com (user_id={USER_ID_TESTE})")


if __name__ == "__main__":
    main()
