#!/usr/bin/env python3
"""
Exporta base_parcelas do SQLite local para SQL compatível com PostgreSQL.

Use quando: Local tem Base Parcelas (15) mas Produção tem (0).
O mesmo arquivo dá resultados diferentes porque base_parcelas é por ambiente.

Uso:
  1. Local:  cd app_dev/backend && python ../../scripts/diagnostic/exportar_base_parcelas_para_producao.py
  2. Gera: temp/export_base_parcelas_producao.sql
  3. No servidor: psql $DATABASE_URL -f temp/export_base_parcelas_producao.sql
     (ou copie o arquivo e execute no PostgreSQL)

IMPORTANTE: Ajuste user_id no SQL se o usuário de produção for diferente do local.
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)


def escape_sql(val):
    """Escapa valor para SQL string"""
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val) if val is not None else "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"


def main(user_id_filter=None):
    """
    Args:
        user_id_filter: Se informado (ex: 1), exporta apenas parcelas desse user_id
    """
    import sqlite3

    db_local = ROOT / "app_dev" / "backend" / "database" / "financas_dev.db"
    suffix = f"_user{user_id_filter}" if user_id_filter else ""
    out_file = ROOT / "temp" / f"export_base_parcelas_producao{suffix}.sql"

    if not db_local.exists():
        print(f"❌ Banco local não encontrado: {db_local}")
        return 1

    out_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_local)
    conn.row_factory = sqlite3.Row
    if user_id_filter is not None:
        rows = conn.execute("""
            SELECT id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas,
                   grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                   qtd_pagas, valor_total_plano, data_inicio, status,
                   user_id, categoria_geral_sugerida
            FROM base_parcelas
            WHERE user_id = ?
            ORDER BY id_parcela
        """, (user_id_filter,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas,
                   grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido,
                   qtd_pagas, valor_total_plano, data_inicio, status,
                   user_id, categoria_geral_sugerida
            FROM base_parcelas
            ORDER BY user_id, id_parcela
        """).fetchall()
    conn.close()

    if not rows:
        print("❌ base_parcelas está vazia no banco local. Nada para exportar.")
        return 1

    # PostgreSQL: INSERT ... ON CONFLICT (id_parcela, user_id) DO UPDATE
    # Nota: base_parcelas pode não ter UNIQUE em (id_parcela, user_id) - usar INSERT simples
    # Se houver duplicatas, o script no servidor pode precisar de ON CONFLICT
    lines = [
        "-- Export base_parcelas para PostgreSQL",
        "-- Gerado por exportar_base_parcelas_para_producao.py",
        "-- Execute: psql $DATABASE_URL -f temp/export_base_parcelas_producao.sql",
        "",
        "BEGIN;",
        "-- Limpar parcelas existentes (opcional - comente se quiser manter e adicionar)",
        "-- DELETE FROM base_parcelas WHERE user_id IN (SELECT DISTINCT user_id FROM base_parcelas);",
        "",
    ]

    for r in rows:
        cols = [
            escape_sql(r["id_parcela"]),
            escape_sql(r["estabelecimento_base"]),
            r["valor_parcela"] if r["valor_parcela"] is not None else "NULL",
            r["qtd_parcelas"] if r["qtd_parcelas"] is not None else "NULL",
            escape_sql(r["grupo_sugerido"]),
            escape_sql(r["subgrupo_sugerido"]),
            escape_sql(r["tipo_gasto_sugerido"]),
            r["qtd_pagas"] if r["qtd_pagas"] is not None else "0",
            r["valor_total_plano"] if r["valor_total_plano"] is not None else "NULL",
            escape_sql(r["data_inicio"]),
            escape_sql(r["status"]) if r["status"] else "'ativo'",
            r["user_id"] if r["user_id"] is not None else "NULL",
            escape_sql(r["categoria_geral_sugerida"]),
        ]
        lines.append(
            f"INSERT INTO base_parcelas (id_parcela, estabelecimento_base, valor_parcela, qtd_parcelas, "
            f"grupo_sugerido, subgrupo_sugerido, tipo_gasto_sugerido, qtd_pagas, valor_total_plano, "
            f"data_inicio, status, user_id, categoria_geral_sugerida) "
            f"VALUES ({', '.join(str(c) for c in cols)});"
        )

    lines.append("COMMIT;")
    lines.append("")
    lines.append(f"-- Total: {len(rows)} registros exportados")

    out_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Exportado {len(rows)} registros para {out_file}")
    print(f"\nPróximo passo: copie o arquivo para o servidor e execute:")
    print(f"  psql $DATABASE_URL -f export_base_parcelas_producao.sql")
    print(f"\nOu via SSH:")
    print(f"  scp temp/export_base_parcelas_producao.sql user@servidor:/tmp/")
    print(f"  ssh user@servidor 'cd /var/www/finup && psql $DATABASE_URL -f /tmp/export_base_parcelas_producao.sql'")
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=int, help="Exportar apenas user_id (ex: --user 1)")
    args = parser.parse_args()
    try:
        sys.exit(main(user_id_filter=args.user))
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
