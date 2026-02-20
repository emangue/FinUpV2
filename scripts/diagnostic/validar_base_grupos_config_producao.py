#!/usr/bin/env python3
"""
Valida se base_grupos_config existe e está acessível em produção.
Usado para diagnosticar erro 500 em GET /budget/planning.

Uso:
  cd app_dev/backend && python ../../scripts/diagnostic/validar_base_grupos_config_producao.py

  # Ou com URL explícita:
  PROD_DATABASE_URL=postgresql://user:pass@host:5432/db python scripts/diagnostic/validar_base_grupos_config_producao.py
"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")


def main():
    from sqlalchemy import create_engine, text

    prod_url = os.getenv("PROD_DATABASE_URL", "").strip()
    if not prod_url:
        print("❌ PROD_DATABASE_URL não definido no .env")
        print("   Defina: PROD_DATABASE_URL=postgresql://finup_user:SENHA@148.230.78.91:5432/finup_db")
        return 1

    print("=" * 60)
    print("Validação: base_grupos_config em PRODUÇÃO")
    print("=" * 60)

    engine = create_engine(prod_url)
    try:
        with engine.connect() as conn:
            # 1. Tabela existe?
            r = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'base_grupos_config'
                )
            """))
            exists = r.scalar()
            print(f"\n1. Tabela base_grupos_config existe: {'✅ SIM' if exists else '❌ NÃO'}")

            if not exists:
                print("\n   → CAUSA DO 500: Tabela ausente. Migration não rodou ou nome diferente.")
                return 1

            # 2. Estrutura (colunas)
            r = conn.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'base_grupos_config'
                ORDER BY ordinal_position
            """))
            cols = r.fetchall()
            print(f"\n2. Colunas ({len(cols)}):")
            for c in cols:
                print(f"   - {c[0]}: {c[1]}")

            required = {"nome_grupo", "categoria_geral"}
            have = {c[0] for c in cols}
            missing = required - have
            if missing:
                print(f"\n   ⚠️ Colunas esperadas ausentes: {missing}")
            else:
                print(f"\n   ✅ Colunas nome_grupo e categoria_geral presentes")

            # 3. Quantos registros
            r = conn.execute(text("SELECT COUNT(*) FROM base_grupos_config"))
            count = r.scalar()
            print(f"\n3. Registros: {count}")

            if count == 0:
                print("   ⚠️ Tabela vazia - get_budget_planning usa grupos_config vazio (fallback OK)")

            # 4. Teste de query idêntica ao service
            r = conn.execute(text("SELECT nome_grupo, categoria_geral FROM base_grupos_config"))
            rows = r.fetchall()
            grupos_config = {nome: cat for nome, cat in rows}
            print(f"\n4. Query simulada (nome_grupo, categoria_geral): {len(grupos_config)} grupos")
            if grupos_config:
                for k, v in list(grupos_config.items())[:5]:
                    print(f"   - {k} → {v}")
                if len(grupos_config) > 5:
                    print(f"   ... e mais {len(grupos_config) - 5}")

        print("\n✅ Validação OK - base_grupos_config acessível")
        return 0

    except Exception as e:
        print(f"\n❌ Erro ao conectar/consultar: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
