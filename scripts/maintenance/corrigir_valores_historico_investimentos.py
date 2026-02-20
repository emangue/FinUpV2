#!/usr/bin/env python3
"""
Corrige investimentos_historico: garante valor_total = valor_unitario × quantidade.

Regra: valor_total é a fonte da verdade. Se valor_unitario for NULL ou 0 mas valor_total
existir, define valor_unitario = valor_total / (quantidade ou 1).

Uso:
  cd app_dev/backend && python ../../scripts/maintenance/corrigir_valores_historico_investimentos.py [--dry-run]
  # Para PostgreSQL (produção):
  DATABASE_URL=postgresql://user:pass@host:5432/db python ../../scripts/maintenance/corrigir_valores_historico_investimentos.py
"""
import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND = ROOT / "app_dev" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv
load_dotenv(BACKEND / ".env")

from sqlalchemy import create_engine, text
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Corrige valor_unitario em investimentos_historico")
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que seria alterado")
    parser.add_argument("--url", help="URL do banco (sobrescreve DATABASE_URL)")
    args = parser.parse_args()

    db_url = args.url or os.environ.get("DATABASE_URL") or str(settings.DATABASE_URL)
    print(f"Usando: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # 1. Corrigir quantidade NULL/0 → 1
        r1 = conn.execute(text("""
            UPDATE investimentos_historico SET quantidade = 1
            WHERE quantidade IS NULL OR quantidade = 0
        """))
        conn.commit()

        # 2. Buscar registros onde valor_unitario precisa ser derivado de valor_total
        r = conn.execute(text("""
            SELECT id, investimento_id, anomes, quantidade, valor_unitario, valor_total
            FROM investimentos_historico
            WHERE valor_total IS NOT NULL AND valor_total != 0
              AND (valor_unitario IS NULL OR valor_unitario = 0)
        """))
        rows = r.fetchall()

        if not rows:
            print("✅ Nenhum registro com valor_unitario NULL/0 encontrado. Base já consistente.")
            return 0

        print(f"Encontrados {len(rows)} registros para corrigir:")
        print("-" * 80)

        for row in rows:
            id_, inv_id, anomes, qty, vu, vt = row
            qty = float(qty) if qty is not None and qty > 0 else 1.0
            vt = float(vt)
            novo_vu = vt / qty
            print(f"  id={id_} investimento_id={inv_id} anomes={anomes} | "
                  f"valor_total={vt:,.2f} qty={qty} → valor_unitario={novo_vu:,.2f}")

        if args.dry_run:
            print("\n[DRY-RUN] Nenhuma alteração feita. Execute sem --dry-run para aplicar.")
            return 0

        # 3. Aplicar: valor_unitario = valor_total / quantidade
        conn.execute(text("""
            UPDATE investimentos_historico
            SET valor_unitario = valor_total / COALESCE(NULLIF(quantidade, 0), 1)
            WHERE valor_total IS NOT NULL AND valor_total != 0
              AND (valor_unitario IS NULL OR valor_unitario = 0)
        """))
        conn.commit()
        print(f"\n✅ {len(rows)} registros corrigidos na base.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
