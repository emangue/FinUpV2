#!/usr/bin/env python3
"""
Migração: Simplificação de Grupos (PostgreSQL Produção)
========================================================
Aplicações → Investimentos
Fatura → Transferência Entre Contas
Movimentações → DELETE (não usado)

Uso:
  cd app_dev/backend && python ../../scripts/migration/migrate_grupos_producao.py [--dry-run]

  Requer PROD_DATABASE_URL no .env (postgresql://user:pass@host:5432/db)
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Carregar .env antes de importar app (opcional - servidor pode ter env via systemd)
try:
    from dotenv import load_dotenv
    load_dotenv(BACKEND / ".env")
except ImportError:
    pass


def main():
    from sqlalchemy import create_engine, text

    # No servidor, DATABASE_URL aponta para o banco de produção
    db_url = os.getenv("PROD_DATABASE_URL", "").strip() or os.getenv("DATABASE_URL", "").strip()
    if not db_url or "postgresql" not in db_url:
        print("❌ PROD_DATABASE_URL ou DATABASE_URL (PostgreSQL) não definido no .env")
        print("   Ex: PROD_DATABASE_URL=postgresql://finup_user:SENHA@host:5432/finup_db")
        return 1

    parser = argparse.ArgumentParser(description="Migração grupos: Aplicações→Investimentos, Fatura→Transferência")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostrar o que seria feito")
    args = parser.parse_args()
    dry_run = args.dry_run

    print("=" * 60)
    print("MIGRAÇÃO: Simplificação de Grupos (Produção)")
    print("=" * 60)
    print(f"Banco: {db_url.split('@')[-1] if '@' in db_url else '***'}")
    print(f"Modo: {'DRY RUN (sem alterações)' if dry_run else 'EXECUÇÃO REAL'}")
    print()

    engine = create_engine(db_url)
    try:
        # 1. Verificar estado atual (read-only)
        with engine.connect() as conn:
            print("1. Estado atual (grupos deprecados)...")
            for tabela, col, valor in [
                ("journal_entries", '"GRUPO"', "Aplicações"),
                ("journal_entries", '"GRUPO"', "Fatura"),
                ("base_grupos_config", "nome_grupo", "Movimentações"),
            ]:
                r = conn.execute(text(f'SELECT COUNT(*) FROM {tabela} WHERE {col} = :v'), {"v": valor})
                count = r.scalar()
                print(f"   {tabela} {valor}: {count} registros")

        if dry_run:
            print("\n[DRY RUN] Executaria os seguintes updates:")
            print("   - journal_entries: Aplicações → Investimentos")
            print("   - journal_entries: Fatura → Transferência Entre Contas")
            print("   - base_marcacoes: Fatura → Transferência Entre Contas")
            print("   - generic_classification_rules: Aplicações → Investimentos, Fatura → Transferência")
            print("   - budget_planning: Aplicações → Investimentos, Fatura → Transferência")
            print("   - base_grupos_config: DELETE Movimentações, Aplicações, Fatura")
            return 0

        # 2. Executar migração (engine.begin() gerencia transação automaticamente)
        with engine.begin() as conn:
            r = conn.execute(text("""
                UPDATE journal_entries SET "GRUPO" = 'Investimentos', "CategoriaGeral" = 'Investimentos'
                WHERE "GRUPO" = 'Aplicações'
            """))
            print(f"\n2. journal_entries Aplicações→Investimentos: {r.rowcount} linhas")

            r = conn.execute(text("""
                UPDATE journal_entries SET "GRUPO" = 'Transferência Entre Contas', "CategoriaGeral" = 'Transferência'
                WHERE "GRUPO" = 'Fatura'
            """))
            print(f"3. journal_entries Fatura→Transferência: {r.rowcount} linhas")

            r = conn.execute(text('''
                UPDATE base_marcacoes SET "GRUPO" = 'Transferência Entre Contas'
                WHERE "GRUPO" = 'Fatura'
            '''))
            print(f"4. base_marcacoes Fatura→Transferência: {r.rowcount} linhas")

            r = conn.execute(text("UPDATE generic_classification_rules SET grupo = 'Investimentos' WHERE grupo = 'Aplicações'"))
            n1 = r.rowcount
            r = conn.execute(text("UPDATE generic_classification_rules SET grupo = 'Transferência Entre Contas' WHERE grupo = 'Fatura'"))
            n2 = r.rowcount
            print(f"5. generic_classification_rules: {n1 + n2} linhas")

            r = conn.execute(text("UPDATE budget_planning SET grupo = 'Investimentos' WHERE grupo = 'Aplicações'"))
            n1 = r.rowcount
            r = conn.execute(text("UPDATE budget_planning SET grupo = 'Transferência Entre Contas' WHERE grupo = 'Fatura'"))
            n2 = r.rowcount
            print(f"6. budget_planning: {n1 + n2} linhas")

            for nome in ["Movimentações", "Aplicações", "Fatura"]:
                r = conn.execute(text("DELETE FROM base_grupos_config WHERE nome_grupo = :n"), {"n": nome})
                if r.rowcount:
                    print(f"7. base_grupos_config DELETE {nome}: {r.rowcount} linhas")

        print("\n✅ Migração concluída!")

    except Exception as e:
        print(f"\n❌ Erro ao conectar/executar: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
