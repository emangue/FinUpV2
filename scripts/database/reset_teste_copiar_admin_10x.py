#!/usr/bin/env python3
"""
Limpa TODOS os dados do teste@email.com e copia do admin com valores ~10x menores.
Executa em SQLite (local) e PostgreSQL (servidor).

Uso:
  # Local (SQLite) - padrão:
  cd app_dev/backend && python ../../scripts/database/reset_teste_copiar_admin_10x.py

  # Servidor (PostgreSQL) - define DATABASE_URL:
  cd app_dev/backend && DATABASE_URL='postgresql://...' python ../../scripts/database/reset_teste_copiar_admin_10x.py

  # Ou carrega .env automaticamente:
  cd app_dev/backend && python ../../scripts/database/reset_teste_copiar_admin_10x.py --postgres
"""
import os
import sys
import random
import uuid
from pathlib import Path
from decimal import Decimal

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "app_dev" / "backend"))

# Carregar .env se existir
_env = ROOT / "app_dev" / "backend" / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

USER_ID_ADMIN = 1
USER_ID_TESTE = 4
FATOR_RANGE = (0.08, 0.12)  # 8% a 12% do valor original (~10x menor)

VALUE_COLS = {
    "journal_entries": ["Valor", "ValorPositivo"],
    "base_parcelas": ["valor_parcela", "valor_total_plano"],
    "budget_planning": ["valor_planejado", "valor_medio_3_meses"],
    "investimentos_portfolio": ["quantidade", "valor_unitario_inicial", "valor_total_inicial"],
    "investimentos_historico": ["quantidade", "valor_unitario", "valor_total", "aporte_mes", "rendimento_mes", "rendimento_acumulado"],
    "investimentos_cenarios": ["patrimonio_inicial", "aporte_mensal"],
    "investimentos_aportes_extraordinarios": ["valor"],
    "investimentos_planejamento": ["meta_aporte_mensal", "meta_rendimento_pct", "meta_patrimonio", "aporte_realizado", "rendimento_realizado", "patrimonio_realizado"],
}


def scale(val):
    if val is None or val == 0:
        return val
    f = random.uniform(*FATOR_RANGE)
    if isinstance(val, (int, float)):
        new = abs(val) * f
        return round(new, 2) if val > 0 else round(-new, 2)
    if isinstance(val, Decimal):
        new = abs(float(val)) * f
        return Decimal(str(round(new, 2))) if val > 0 else Decimal(str(round(-new, 2)))
    return val


def get_db_url():
    if "--postgres" in sys.argv:
        return os.getenv("PROD_DATABASE_URL") or os.getenv("DATABASE_URL")
    url = os.getenv("DATABASE_URL") or os.getenv("PROD_DATABASE_URL")
    if url and "postgresql" in url:
        return url
    return f"sqlite:///{ROOT / 'app_dev' / 'backend' / 'database' / 'financas_dev.db'}"


def main():
    from sqlalchemy import create_engine, text

    db_url = get_db_url()
    if not db_url:
        print("❌ Defina DATABASE_URL ou use --postgres com PROD_DATABASE_URL no .env")
        sys.exit(1)

    use_sqlite = "sqlite" in db_url
    engine = create_engine(db_url, echo=False)

    def run(sql, params=None):
        with engine.connect() as conn:
            r = conn.execute(text(sql), params or {})
            conn.commit()
            return r

    def run_returning(sql, params=None):
        """Executa INSERT...RETURNING id e retorna o id."""
        with engine.connect() as conn:
            r = conn.execute(text(sql), params or {})
            row = r.fetchone()
            conn.commit()
            return row[0] if row else None

    def fetch(sql, params=None):
        with engine.connect() as conn:
            return conn.execute(text(sql), params or {}).fetchall()

    def fetchone(sql, params=None):
        rows = fetch(sql, params)
        return rows[0] if rows else None

    def get_cols(table):
        if use_sqlite:
            r = fetch(f"PRAGMA table_info({table})")
            return [row[1] for row in r]
        r = fetch("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = :t ORDER BY ordinal_position
        """, {"t": table})
        return [row[0] for row in r]

    def q(col):
        """PostgreSQL: colunas com maiúsculas precisam de aspas duplas."""
        return f'"{col}"' if not use_sqlite and col != col.lower() else col

    # Verificar usuários
    admin = fetchone("SELECT id, email FROM users WHERE id = :id", {"id": USER_ID_ADMIN})
    teste = fetchone("SELECT id, email FROM users WHERE id = :id", {"id": USER_ID_TESTE})
    if not admin or not teste:
        print("❌ Usuários admin ou teste não encontrados!")
        sys.exit(1)

    print("=" * 70)
    print("🔄 RESET TESTE + COPIAR ADMIN (valores ~10x menores)")
    print("=" * 70)
    print(f"Admin: {admin[1]} (ID={admin[0]})")
    print(f"Teste: {teste[1]} (ID={teste[0]})")
    print(f"Banco: {'SQLite' if use_sqlite else 'PostgreSQL'}")
    print("=" * 70)

    # 1. LIMPAR dados do teste (ordem respeitando FKs)
    print("\n📌 1. Limpando dados do teste@email.com...")
    deletes = [
        ("investimentos_aportes_extraordinarios", "cenario_id IN (SELECT id FROM investimentos_cenarios WHERE user_id = :uid)"),
        ("investimentos_historico", "investimento_id IN (SELECT id FROM investimentos_portfolio WHERE user_id = :uid)"),
        ("investimentos_cenarios", "user_id = :uid"),
        ("investimentos_portfolio", "user_id = :uid"),
        ("investimentos_planejamento", "user_id = :uid"),
        ("journal_entries", "user_id = :uid"),
        ("base_parcelas", "user_id = :uid"),
        ("budget_planning", "user_id = :uid"),
        ("preview_transacoes", "user_id = :uid"),
        ("transacoes_exclusao", "user_id = :uid"),
        ("cartoes", "user_id = :uid"),
        ("upload_history", "user_id = :uid"),
    ]
    for table, where in deletes:
        try:
            r = run(f"DELETE FROM {table} WHERE {where}", {"uid": USER_ID_TESTE})
            n = r.rowcount if hasattr(r, 'rowcount') else 0
            print(f"   🗑️  {table}: {n} removidos")
        except Exception as e:
            if "no such column" not in str(e).lower() and "user_id" not in str(e):
                print(f"   ⚠️  {table}: {e}")

    # 2. COPIAR investimentos_portfolio (mapear id antigo -> novo)
    print("\n📌 2. Copiando investimentos_portfolio...")
    cols = get_cols("investimentos_portfolio")
    rows = fetch("SELECT * FROM investimentos_portfolio WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    id_map = {}
    for row in rows:
        d = dict(zip(cols, row))
        old_id = d.pop("id")
        d["user_id"] = USER_ID_TESTE
        d["balance_id"] = f"teste_{uuid.uuid4().hex[:16]}"
        for c in VALUE_COLS.get("investimentos_portfolio", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        sql = f"INSERT INTO investimentos_portfolio ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})"
        if use_sqlite:
            run(sql, d)
            new_id = fetchone("SELECT last_insert_rowid()")[0]
        else:
            new_id = run_returning(sql + " RETURNING id", d)
        id_map[old_id] = new_id
    print(f"   ✅ {len(id_map)} portfolios copiados")

    # 3. investimentos_historico
    print("\n📌 3. Copiando investimentos_historico...")
    cols = get_cols("investimentos_historico")
    rows = fetch("""
        SELECT h.* FROM investimentos_historico h
        JOIN investimentos_portfolio p ON h.investimento_id = p.id
        WHERE p.user_id = :uid
    """, {"uid": USER_ID_ADMIN})
    count = 0
    for row in rows:
        d = dict(zip(cols, row))
        if d["investimento_id"] not in id_map:
            continue
        d["investimento_id"] = id_map[d["investimento_id"]]
        d.pop("id", None)
        for c in VALUE_COLS.get("investimentos_historico", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        run(f"INSERT INTO investimentos_historico ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
        count += 1
    print(f"   ✅ {count} históricos copiados")

    # 4. journal_entries
    print("\n📌 4. Copiando journal_entries...")
    cols = get_cols("journal_entries")
    rows = fetch("SELECT * FROM journal_entries WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    count = 0
    for i, row in enumerate(rows):
        d = dict(zip(cols, row))
        d.pop("id", None)
        d["user_id"] = USER_ID_TESTE
        d["upload_history_id"] = None
        d["IdTransacao"] = f"teste_{i}_{uuid.uuid4().hex[:8]}"
        if d.get("IdParcela"):
            d["IdParcela"] = f"teste_{i}_{d['IdParcela']}"
        for c in VALUE_COLS.get("journal_entries", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        run(f"INSERT INTO journal_entries ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
        count += 1
    print(f"   ✅ {count} transações copiadas")

    # 5. base_parcelas
    print("\n📌 5. Copiando base_parcelas...")
    cols = get_cols("base_parcelas")
    rows = fetch("SELECT * FROM base_parcelas WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    count = 0
    for i, row in enumerate(rows):
        d = dict(zip(cols, row))
        d.pop("id", None)
        d["user_id"] = USER_ID_TESTE
        if "id_parcela" in d and d["id_parcela"]:
            d["id_parcela"] = f"teste_{i}_{d['id_parcela']}"
        for c in VALUE_COLS.get("base_parcelas", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        run(f"INSERT INTO base_parcelas ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
        count += 1
    print(f"   ✅ {count} parcelas copiadas")

    # 6. budget_planning
    print("\n📌 6. Copiando budget_planning...")
    cols = get_cols("budget_planning")
    rows = fetch("SELECT * FROM budget_planning WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    count = 0
    for row in rows:
        d = dict(zip(cols, row))
        d.pop("id", None)
        d["user_id"] = USER_ID_TESTE
        for c in VALUE_COLS.get("budget_planning", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        run(f"INSERT INTO budget_planning ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
        count += 1
    print(f"   ✅ {count} budget copiados")

    # 7. investimentos_cenarios + aportes
    print("\n📌 7. Copiando investimentos_cenarios...")
    cols = get_cols("investimentos_cenarios")
    rows = fetch("SELECT * FROM investimentos_cenarios WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    cenario_map = {}
    count = 0
    for row in rows:
        d = dict(zip(cols, row))
        old_id = d.pop("id")
        d["user_id"] = USER_ID_TESTE
        for c in VALUE_COLS.get("investimentos_cenarios", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        sql = f"INSERT INTO investimentos_cenarios ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})"
        if use_sqlite:
            run(sql, d)
            new_id = fetchone("SELECT last_insert_rowid()")[0]
        else:
            new_id = run_returning(sql + " RETURNING id", d)
        cenario_map[old_id] = new_id
        count += 1
    print(f"   ✅ {count} cenários copiados")

    if cenario_map:
        print("\n📌 8. Copiando investimentos_aportes_extraordinarios...")
        cols = get_cols("investimentos_aportes_extraordinarios")
        ids = list(cenario_map.keys())
        if use_sqlite:
            ph = ",".join(f":p{i}" for i in range(len(ids)))
            params = {f"p{i}": ids[i] for i in range(len(ids))}
            rows = fetch(f"SELECT * FROM investimentos_aportes_extraordinarios WHERE cenario_id IN ({ph})", params)
        else:
            rows = fetch("SELECT * FROM investimentos_aportes_extraordinarios WHERE cenario_id = ANY(:ids)", {"ids": ids})
        count = 0
        for row in rows:
            d = dict(zip(cols, row))
            d.pop("id", None)
            d["cenario_id"] = cenario_map[d["cenario_id"]]
            if "valor" in d and d["valor"]:
                d["valor"] = scale(d["valor"])
            cols_ins = list(d.keys())
            placeholders = ", ".join(f":{k}" for k in cols_ins)
            run(f"INSERT INTO investimentos_aportes_extraordinarios ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
            count += 1
        print(f"   ✅ {count} aportes copiados")

    # 9. investimentos_planejamento
    print("\n📌 9. Copiando investimentos_planejamento...")
    cols = get_cols("investimentos_planejamento")
    rows = fetch("SELECT * FROM investimentos_planejamento WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
    count = 0
    for row in rows:
        d = dict(zip(cols, row))
        d.pop("id", None)
        d["user_id"] = USER_ID_TESTE
        for c in VALUE_COLS.get("investimentos_planejamento", []):
            if c in d and d[c] is not None:
                d[c] = scale(d[c])
        cols_ins = list(d.keys())
        placeholders = ", ".join(f":{k}" for k in cols_ins)
        run(f"INSERT INTO investimentos_planejamento ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
        count += 1
    print(f"   ✅ {count} planejamentos copiados")

    # 10. cartoes, transacoes_exclusao
    for table in ["cartoes", "transacoes_exclusao"]:
        cols = get_cols(table)
        if "user_id" not in cols:
            continue
        print(f"\n📌 Copiando {table}...")
        rows = fetch(f"SELECT * FROM {table} WHERE user_id = :uid", {"uid": USER_ID_ADMIN})
        count = 0
        for row in rows:
            d = dict(zip(cols, row))
            d.pop("id", None)
            d["user_id"] = USER_ID_TESTE
            cols_ins = list(d.keys())
            placeholders = ", ".join(f":{k}" for k in cols_ins)
            run(f"INSERT INTO {table} ({','.join(q(c) for c in cols_ins)}) VALUES ({placeholders})", d)
            count += 1
        print(f"   ✅ {count} copiados")

    print("\n" + "=" * 70)
    print("✅ CONCLUÍDO! teste@email.com resetado com dados do admin (~10x menores)")
    print("=" * 70)


if __name__ == "__main__":
    main()
