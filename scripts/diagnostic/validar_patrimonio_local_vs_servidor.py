#!/usr/bin/env python3
"""
Validação: Patrimônio Local vs Servidor

Compara dados de investimentos (ativos, passivos, PL) entre:
- LOCAL: SQLite (financas_dev.db)
- SERVIDOR: PostgreSQL (finup_db)

Uso:
  # Local - precisa de PROD_DATABASE_URL no .env para conectar ao servidor
  cd app_dev/backend && python ../../scripts/diagnostic/validar_patrimonio_local_vs_servidor.py

  # Ou definir na hora:
  PROD_DATABASE_URL=postgresql://finup_user:xxx@148.230.78.91:5432/finup_db python scripts/diagnostic/validar_patrimonio_local_vs_servidor.py
"""
import sys
import os
from pathlib import Path
from decimal import Decimal

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Carregar .env do backend
from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")


def get_patrimonio_raw(engine, user_id: int):
    """Executa a mesma lógica do get_portfolio_resumo via SQL puro."""
    from sqlalchemy import text

    with engine.connect() as conn:
        # Último mês disponível
        r = conn.execute(text("""
            SELECT MAX(h.anomes) as ultimo_mes
            FROM investimentos_historico h
            JOIN investimentos_portfolio p ON p.id = h.investimento_id
            WHERE p.user_id = :uid
        """), {"uid": user_id})
        ultimo_mes = r.scalar()
        if not ultimo_mes:
            return None, None

        # Valores por classe_ativo
        r = conn.execute(text("""
            SELECT p.classe_ativo, SUM(h.valor_total) as total
            FROM investimentos_portfolio p
            JOIN investimentos_historico h ON h.investimento_id = p.id
            WHERE p.user_id = :uid AND h.anomes = :anomes
            GROUP BY p.classe_ativo
        """), {"uid": user_id, "anomes": ultimo_mes})
        rows = r.fetchall()

        total_ativos = 0.0
        total_passivos = 0.0
        for row in rows:
            classe = (row[0] or "").strip()
            valor = float(row[1] or 0)
            if classe == "Ativo" or classe.lower() == "ativo":
                total_ativos += valor
            elif classe == "Passivo" or classe.lower() == "passivo":
                total_passivos += valor

        pl = total_ativos + total_passivos
        return {
            "ativos": total_ativos,
            "passivos": total_passivos,
            "pl": pl,
            "ultimo_mes": ultimo_mes,
        }, ultimo_mes


def main():
    from sqlalchemy import create_engine, text

    # Local: SQLite
    local_path = BACKEND / "database" / "financas_dev.db"
    if not local_path.exists():
        print(f"❌ Banco local não encontrado: {local_path}")
        return 1

    local_url = f"sqlite:///{local_path}"
    prod_url = os.getenv("PROD_DATABASE_URL", "").strip()

    if not prod_url:
        print("⚠️  PROD_DATABASE_URL não definido.")
        print("   Para comparar com o servidor, defina no .env:")
        print("   PROD_DATABASE_URL=postgresql://finup_user:SENHA@148.230.78.91:5432/finup_db")
        print("\n   Ou (se o Postgres estiver no localhost):")
        print("   PROD_DATABASE_URL=postgresql://finup_user:SENHA@127.0.0.1:5432/finup_db")
        print("\n📊 Validando apenas LOCAL...\n")

    print("=" * 70)
    print("VALIDAÇÃO: Patrimônio Local vs Servidor")
    print("=" * 70)

    local_engine = create_engine(local_url)

    # Listar user_ids que têm investimentos
    with local_engine.connect() as conn:
        r = conn.execute(text("""
            SELECT DISTINCT p.user_id, u.email
            FROM investimentos_portfolio p
            LEFT JOIN users u ON u.id = p.user_id
            ORDER BY p.user_id
        """))
        users = r.fetchall()

    if not users:
        print("\n❌ Nenhum usuário com investimentos no LOCAL.")
        return 1

    print(f"\n📌 LOCAL: {local_path.name}")
    if prod_url:
        mask = prod_url
        if "@" in mask:
            parts = mask.split("@")
            if ":" in parts[0]:
                user_part = parts[0].split("//")[-1]
                if ":" in user_part:
                    user = user_part.split(":")[0]
                    mask = mask.replace(user_part, f"{user}:****")
        print(f"📌 SERVIDOR: {mask[:60]}...")
    print()

    all_ok = True
    for user_id, email in users:
        email = email or "(sem email)"
        print(f"--- user_id={user_id} ({email}) ---")

        local_data, _ = get_patrimonio_raw(local_engine, user_id)
        if not local_data:
            print("  LOCAL:   Sem dados de investimentos")
        else:
            print(f"  LOCAL:   Ativos R$ {local_data['ativos']:,.2f} | Passivos R$ {local_data['passivos']:,.2f} | PL R$ {local_data['pl']:,.2f} (anomes={local_data['ultimo_mes']})")

        if prod_url:
            try:
                prod_engine = create_engine(prod_url)
                prod_data, _ = get_patrimonio_raw(prod_engine, user_id)
                if not prod_data:
                    print("  SERVIDOR: Sem dados de investimentos")
                    all_ok = False
                else:
                    print(f"  SERVIDOR: Ativos R$ {prod_data['ativos']:,.2f} | Passivos R$ {prod_data['passivos']:,.2f} | PL R$ {prod_data['pl']:,.2f} (anomes={prod_data['ultimo_mes']})")

                    # Comparar
                    tol = 0.01
                    diff_a = abs(local_data["ativos"] - prod_data["ativos"])
                    diff_p = abs(local_data["passivos"] - prod_data["passivos"])
                    diff_pl = abs(local_data["pl"] - prod_data["pl"])
                    if diff_a > tol or diff_p > tol or diff_pl > tol:
                        print("  ❌ DIFERENÇA DETECTADA!")
                        all_ok = False
                    else:
                        print("  ✅ Valores batem")
            except Exception as e:
                print(f"  SERVIDOR: Erro ao conectar - {e}")
                all_ok = False
        print()

    print("=" * 70)
    if all_ok and prod_url:
        print("✅ LOCAL e SERVIDOR com mesmos valores de patrimônio")
    elif prod_url:
        print("❌ Diferenças encontradas - verificar migração/sincronização")
    else:
        print("✅ Validação local concluída (servidor não configurado)")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
