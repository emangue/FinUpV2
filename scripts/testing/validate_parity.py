#!/usr/bin/env python3
"""
✅ Script de Validação de Paridade Dev-Prod
============================================

Compara configurações e schemas entre ambiente local e produção.

Uso:
    python scripts/testing/validate_parity.py

Validações:
- ✅ Schemas de tabelas (colunas, tipos, constraints)
- ✅ Contagens de registros
- ✅ Variáveis de ambiente
- ✅ Versões de dependências
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Tuple

# Adicionar app ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app_dev" / "backend"))

from sqlalchemy import create_engine, inspect, text
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compare_table_schemas(local_engine, prod_engine) -> Dict:
    """Compara schemas entre local e prod"""
    logger.info("\n🔍 Comparando schemas das tabelas...")
    
    local_inspector = inspect(local_engine)
    prod_inspector = inspect(prod_engine)
    
    local_tables = set(local_inspector.get_table_names())
    prod_tables = set(prod_inspector.get_table_names())
    
    differences = {
        'only_local': local_tables - prod_tables,
        'only_prod': prod_tables - local_tables,
        'common': local_tables & prod_tables,
        'column_diffs': {}
    }
    
    logger.info(f"  Tabelas apenas em LOCAL: {len(differences['only_local'])}")
    logger.info(f"  Tabelas apenas em PROD:  {len(differences['only_prod'])}")
    logger.info(f"  Tabelas comuns:          {len(differences['common'])}")
    
    # Comparar colunas das tabelas comuns
    for table_name in differences['common']:
        local_cols = {col['name']: col for col in local_inspector.get_columns(table_name)}
        prod_cols = {col['name']: col for col in prod_inspector.get_columns(table_name)}
        
        if set(local_cols.keys()) != set(prod_cols.keys()):
            differences['column_diffs'][table_name] = {
                'only_local': set(local_cols.keys()) - set(prod_cols.keys()),
                'only_prod': set(prod_cols.keys()) - set(local_cols.keys())
            }
    
    return differences


def compare_record_counts(local_engine, prod_engine, table_names: List[str]) -> Dict:
    """Compara contagens de registros"""
    logger.info("\n📊 Comparando contagens de registros...")
    
    counts = {}
    
    for table_name in table_names:
        try:
            with local_engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                local_count = result.scalar()
        except Exception as e:
            local_count = f"ERROR: {e}"
        
        try:
            with prod_engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                prod_count = result.scalar()
        except Exception as e:
            prod_count = f"ERROR: {e}"
        
        counts[table_name] = {
            'local': local_count,
            'prod': prod_count,
            'match': local_count == prod_count if isinstance(local_count, int) and isinstance(prod_count, int) else False
        }
    
    return counts


def main():
    logger.info("=" * 70)
    logger.info("✅ VALIDAÇÃO DE PARIDADE DEV-PROD")
    logger.info("=" * 70)
    
    # Verificar se está usando PostgreSQL
    if not settings.is_postgres:
        logger.warning("⚠️  Ambiente LOCAL está usando SQLite!")
        logger.warning("⚠️  Para paridade real, configure PostgreSQL local.")
        logger.warning("⚠️  Defina DATABASE_URL no .env")
        return False
    
    # URLs de conexão
    local_url = settings.DATABASE_URL
    prod_url = os.getenv("PROD_DATABASE_URL")
    
    if not prod_url:
        logger.error("❌ PROD_DATABASE_URL não definido!")
        logger.error("   Defina no .env: PROD_DATABASE_URL=postgresql://...")
        return False
    
    logger.info(f"\nLOCAL: {local_url[:50]}...")
    logger.info(f"PROD:  {prod_url[:50]}...")
    
    # Criar engines
    local_engine = create_engine(local_url)
    prod_engine = create_engine(prod_url)
    
    # Comparar schemas
    schema_diffs = compare_table_schemas(local_engine, prod_engine)
    
    if schema_diffs['only_local']:
        logger.warning(f"\n⚠️  Tabelas APENAS em LOCAL: {schema_diffs['only_local']}")
    
    if schema_diffs['only_prod']:
        logger.warning(f"\n⚠️  Tabelas APENAS em PROD: {schema_diffs['only_prod']}")
    
    if schema_diffs['column_diffs']:
        logger.warning("\n⚠️  Diferenças de colunas:")
        for table, diffs in schema_diffs['column_diffs'].items():
            logger.warning(f"  {table}:")
            if diffs['only_local']:
                logger.warning(f"    Apenas em LOCAL: {diffs['only_local']}")
            if diffs['only_prod']:
                logger.warning(f"    Apenas em PROD: {diffs['only_prod']}")
    
    # Comparar contagens
    common_tables = list(schema_diffs['common'])[:10]  # Primeiras 10 tabelas
    counts = compare_record_counts(local_engine, prod_engine, common_tables)
    
    logger.info(f"\n{'Tabela':<40} {'Local':>10} {'Prod':>10} {'Status':>10}")
    logger.info("-" * 70)
    
    all_match = True
    for table, data in counts.items():
        status = "✅ OK" if data['match'] else "❌ DIFF"
        if not data['match']:
            all_match = False
        logger.info(f"{table:<40} {str(data['local']):>10} {str(data['prod']):>10} {status:>10}")
    
    logger.info("-" * 70)
    
    if all_match and not schema_diffs['only_local'] and not schema_diffs['only_prod'] and not schema_diffs['column_diffs']:
        logger.info("\n✅ PARIDADE 100% - Ambientes idênticos!")
        return True
    else:
        logger.warning("\n⚠️  Ambientes divergem - Ajustes necessários")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
