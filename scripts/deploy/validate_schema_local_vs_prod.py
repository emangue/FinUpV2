#!/usr/bin/env python3
"""
Validação de Schema: SQLite (local) vs PostgreSQL (produção)
============================================================

Compara estrutura das tabelas entre base local e produção.
NÃO compara dados, apenas: tabelas existentes e colunas.

Uso:
    # No servidor ou com PROD_DATABASE_URL no .env
    cd app_dev/backend && python ../../scripts/deploy/validate_schema_local_vs_prod.py

Requisitos:
    - Local: SQLite em database/financas_dev.db (ou DATABASE_URL)
    - Prod: PROD_DATABASE_URL no .env (postgresql://...)
"""

import os
import sys
from pathlib import Path

# Adicionar backend ao path
backend_path = Path(__file__).parent.parent.parent / "app_dev" / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

from sqlalchemy import create_engine, inspect
from app.core.config import settings


def get_local_url():
    """URL do banco local (SQLite padrão)"""
    return settings.DATABASE_URL


def get_prod_url():
    return os.getenv("PROD_DATABASE_URL")


def normalize_type(t):
    """Normaliza tipo para comparação (SQLite vs PostgreSQL)"""
    if t is None:
        return "unknown"
    s = str(t).upper()
    if "INT" in s or "INTEGER" in s:
        return "INTEGER"
    if "VARCHAR" in s or "TEXT" in s or "CHAR" in s:
        return "TEXT"
    if "NUMERIC" in s or "DECIMAL" in s or "REAL" in s or "FLOAT" in s:
        return "NUMERIC"
    if "BOOL" in s:
        return "BOOLEAN"
    if "DATE" in s or "TIMESTAMP" in s or "DATETIME" in s:
        return "DATETIME"
    return s


def compare_schemas(local_engine, prod_engine):
    """Compara schemas e retorna diferenças"""
    local_insp = inspect(local_engine)
    prod_insp = inspect(prod_engine)

    local_tables = set(local_insp.get_table_names())
    prod_tables = set(prod_insp.get_table_names())

    only_local = local_tables - prod_tables
    only_prod = prod_tables - local_tables
    common = local_tables & prod_tables

    column_diffs = {}
    for table in sorted(common):
        lcols = {c["name"]: normalize_type(c.get("type")) for c in local_insp.get_columns(table)}
        pcols = {c["name"]: normalize_type(c.get("type")) for c in prod_insp.get_columns(table)}
        only_local_cols = set(lcols.keys()) - set(pcols.keys())
        only_prod_cols = set(pcols.keys()) - set(lcols.keys())
        if only_local_cols or only_prod_cols:
            column_diffs[table] = {
                "only_local": only_local_cols,
                "only_prod": only_prod_cols,
            }

    return {
        "only_local": only_local,
        "only_prod": only_prod,
        "common": common,
        "column_diffs": column_diffs,
    }


def main():
    print("=" * 70)
    print("🔍 VALIDAÇÃO DE SCHEMA: Local (SQLite) vs Produção (PostgreSQL)")
    print("=" * 70)

    local_url = get_local_url()
    prod_url = get_prod_url()

    if not prod_url:
        print("\n❌ PROD_DATABASE_URL não definido!")
        print("   No .env do backend, adicione:")
        print("   PROD_DATABASE_URL=postgresql://user:pass@host:5432/finup_db")
        return 1

    # Mascarar senha na exibição
    local_display = local_url[:60] + "..." if len(local_url) > 60 else local_url
    prod_display = prod_url.split("@")[-1] if "@" in prod_url else prod_url[:50] + "..."

    print(f"\nLocal:  {local_display}")
    print(f"Prod:   ...@{prod_display}")

    try:
        local_engine = create_engine(local_url)
        prod_engine = create_engine(prod_url)
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")
        return 1

    diffs = compare_schemas(local_engine, prod_engine)

    has_issues = False

    if diffs["only_local"]:
        print(f"\n⚠️  Tabelas APENAS no LOCAL (faltam no prod): {sorted(diffs['only_local'])}")
        has_issues = True

    if diffs["only_prod"]:
        print(f"\n⚠️  Tabelas APENAS no PROD (extras): {sorted(diffs['only_prod'])}")
        # Menos crítico - prod pode ter tabelas legadas
        # has_issues = True

    if diffs["column_diffs"]:
        print("\n⚠️  Diferenças de colunas:")
        for table, d in diffs["column_diffs"].items():
            if d["only_local"]:
                print(f"   {table}: colunas só no LOCAL: {d['only_local']}")
                has_issues = True
            if d["only_prod"]:
                print(f"   {table}: colunas só no PROD: {d['only_prod']}")

    if not has_issues and not diffs["column_diffs"]:
        print("\n✅ SCHEMAS COMPATÍVEIS - Local e Prod têm mesma estrutura de tabelas/colunas")
        print(f"   Tabelas comuns: {len(diffs['common'])}")
        return 0

    if has_issues:
        print("\n❌ SCHEMAS DIVERGENTES - Rodar migrations no servidor:")
        print("   cd app_dev/backend && alembic upgrade head")
        return 1

    print("\n✅ Validação concluída (pequenas diferenças aceitáveis)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
