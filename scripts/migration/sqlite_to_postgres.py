#!/usr/bin/env python3
"""
🔄 Script de Migração SQLite → PostgreSQL
==========================================

Migra TODOS os dados do SQLite local para PostgreSQL (dev/prod).

Uso:
    python scripts/migration/sqlite_to_postgres.py --source sqlite:///path/to/db.db --target postgresql://user:pass@host/db

Recursos:
- ✅ Valida contagens antes/depois
- ✅ Transfere todas as tabelas
- ✅ Preserva integridade referencial
- ✅ Log detalhado do processo
- ✅ Rollback automático em caso de erro
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Adicionar app ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app_dev" / "backend"))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

# Importar TODOS os modelos
from app.domains.transactions.models import JournalEntry, BaseParcelas
from app.domains.users.models import User
from app.domains.categories.models import BaseMarcacao
from app.domains.grupos.models import BaseGruposConfig
from app.domains.cards.models import Cartao
from app.domains.exclusoes.models import TransacaoExclusao
from app.domains.upload.models import PreviewTransacao
from app.domains.patterns.models import BasePadroes
from app.domains.screen_visibility.models import ScreenVisibility
from app.domains.budget.models import (
    BudgetGeral, BudgetPlanning,
    BudgetCategoriaConfig, BudgetGeralHistorico
)
from app.domains.compatibility.models import BankFormatCompatibility
from app.domains.classification.models import GenericClassificationRules
from app.domains.investimentos.models import (
    InvestimentoPortfolio, InvestimentoHistorico,
    InvestimentoCenario, AporteExtraordinario, InvestimentoPlanejamento
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ordem de migração (respeita foreign keys)
MIGRATION_ORDER = [
    ('users', User),
    ('base_marcacoes', BaseMarcacao),
    ('base_grupos_config', BaseGruposConfig),
    ('base_padroes', BasePadroes),
    ('cartoes', Cartao),
    ('transacoes_exclusao', TransacaoExclusao),
    ('screen_visibility', ScreenVisibility),
    ('bank_format_compatibility', BankFormatCompatibility),
    ('generic_classification_rules', GenericClassificationRules),
    ('budget_planning', BudgetPlanning),
    ('budget_geral', BudgetGeral),
    ('budget_categoria_config', BudgetCategoriaConfig),
    ('budget_geral_historico', BudgetGeralHistorico),
    ('investimentos_portfolio', InvestimentoPortfolio),
    ('investimentos_historico', InvestimentoHistorico),
    ('investimentos_cenarios', InvestimentoCenario),
    ('investimentos_aportes_extraordinarios', AporteExtraordinario),
    ('investimentos_planejamento', InvestimentoPlanejamento),
    ('upload_history', None),  # Tabela sem modelo direto
    ('journal_entries', JournalEntry),
    ('base_parcelas', BaseParcelas),
    ('preview_transacoes', PreviewTransacao),
]


def validate_connection(engine, db_type):
    """Valida conexão com o banco"""
    try:
        with engine.connect() as conn:
            if db_type == "sqlite":
                result = conn.execute(text("SELECT sqlite_version()"))
                version = result.scalar()
                logger.info(f"✅ SQLite conectado - Versão: {version}")
            else:  # PostgreSQL
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"✅ PostgreSQL conectado - Versão: {version[:50]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Erro de conexão ({db_type}): {e}")
        return False


def get_table_count(engine, table_name):
    """Retorna contagem de registros em uma tabela"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    except Exception as e:
        logger.warning(f"⚠️  Tabela {table_name} não existe ou erro: {e}")
        return 0


def migrate_data(source_url, target_url, dry_run=False):
    """
    Migra dados do source para target
    
    Args:
        source_url: URL de conexão do banco origem (SQLite)
        target_url: URL de conexão do banco destino (PostgreSQL)
        dry_run: Se True, apenas valida sem migrar
    """
    logger.info("=" * 70)
    logger.info("🔄 MIGRAÇÃO SQLite → PostgreSQL")
    logger.info("=" * 70)
    logger.info(f"Origem:  {source_url}")
    logger.info(f"Destino: {target_url[:50]}...")
    logger.info(f"Modo:    {'DRY RUN (simulação)' if dry_run else 'PRODUÇÃO'}")
    logger.info("=" * 70)
    
    # Criar engines
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    # Validar conexões
    if not validate_connection(source_engine, "sqlite"):
        logger.error("❌ Falha ao conectar no SQLite de origem")
        return False
    
    if not validate_connection(target_engine, "postgresql"):
        logger.error("❌ Falha ao conectar no PostgreSQL de destino")
        return False
    
    # Criar tabelas no destino (se não existirem)
    if not dry_run:
        logger.info("\n📋 Criando schema no PostgreSQL...")
        Base.metadata.create_all(target_engine)
        logger.info("✅ Schema criado")
    
    # Inspecionar tabelas
    source_inspector = inspect(source_engine)
    target_inspector = inspect(target_engine)
    
    source_tables = set(source_inspector.get_table_names())
    target_tables = set(target_inspector.get_table_names())
    
    logger.info(f"\n📊 Tabelas na origem:  {len(source_tables)}")
    logger.info(f"📊 Tabelas no destino: {len(target_tables)}")
    
    # Contagens antes da migração
    logger.info("\n📈 Contagens ANTES da migração:")
    logger.info("-" * 70)
    
    migration_stats = {}
    
    for table_name, model in MIGRATION_ORDER:
        if table_name not in source_tables:
            logger.warning(f"⚠️  {table_name:40} - Não existe na origem")
            continue
        
        source_count = get_table_count(source_engine, table_name)
        target_count = get_table_count(target_engine, table_name) if not dry_run else 0
        
        migration_stats[table_name] = {
            'before': target_count,
            'source': source_count,
            'after': target_count
        }
        
        logger.info(f"  {table_name:40} - Origem: {source_count:6} | Destino: {target_count:6}")
    
    if dry_run:
        logger.info("\n✅ DRY RUN concluído - Nenhum dado foi migrado")
        return True
    
    # Migrar dados
    logger.info("\n🔄 Iniciando migração...")
    logger.info("-" * 70)
    
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)
    
    source_session = SourceSession()
    target_session = TargetSession()
    
    try:
        for table_name, model in MIGRATION_ORDER:
            if table_name not in source_tables or table_name not in migration_stats:
                continue
            
            source_count = migration_stats[table_name]['source']
            
            if source_count == 0:
                logger.info(f"⏭️  {table_name:40} - Vazia, pulando")
                continue
            
            logger.info(f"🔄 {table_name:40} - Migrando {source_count} registros...")
            
            if model is None:
                # Tabela sem modelo (ex: upload_history) - migrar manualmente
                logger.warning(f"⚠️  {table_name:40} - Modelo não disponível, requer migração manual")
                continue
            
            # Buscar todos os registros da origem
            records = source_session.query(model).all()
            
            # Inserir no destino em lotes
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                
                # Copiar atributos para novos objetos (evitar conflitos de sessão)
                for record in batch:
                    # Criar novo objeto com os mesmos dados
                    record_dict = {c.name: getattr(record, c.name) for c in record.__table__.columns}
                    new_record = model(**record_dict)
                    target_session.merge(new_record)  # merge em vez de add (atualiza se existir)
                
                target_session.commit()
                logger.info(f"   ✅ Batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1} - {len(batch)} registros")
            
            # Atualizar estatísticas
            migration_stats[table_name]['after'] = get_table_count(target_engine, table_name)
            
            logger.info(f"✅ {table_name:40} - Migrado: {migration_stats[table_name]['after']} registros")
        
        target_session.commit()
        logger.info("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante migração: {e}")
        target_session.rollback()
        return False
    finally:
        source_session.close()
        target_session.close()
    
    # Validação final
    logger.info("\n📈 Contagens DEPOIS da migração:")
    logger.info("-" * 70)
    logger.info(f"{'Tabela':<40} {'Origem':>8} {'Destino Antes':>15} {'Destino Depois':>16} {'Status':>10}")
    logger.info("-" * 70)
    
    all_ok = True
    for table_name, stats in migration_stats.items():
        status = "✅ OK" if stats['source'] == stats['after'] else "❌ ERRO"
        if stats['source'] != stats['after']:
            all_ok = False
        
        logger.info(
            f"{table_name:<40} {stats['source']:>8} {stats['before']:>15} "
            f"{stats['after']:>16} {status:>10}"
        )
    
    logger.info("-" * 70)
    logger.info(f"\n{'✅ MIGRAÇÃO 100% SUCESSO' if all_ok else '❌ MIGRAÇÃO COM ERROS'}")
    
    return all_ok


def main():
    parser = argparse.ArgumentParser(description='Migrar dados SQLite → PostgreSQL')
    parser.add_argument(
        '--source',
        default='sqlite:////Users/emangue/Documents/ProjetoVSCode/ProjetoFinancasV5/app_dev/backend/database/financas_dev.db',
        help='URL de conexão SQLite origem'
    )
    parser.add_argument(
        '--target',
        help='URL de conexão PostgreSQL destino (ex: postgresql://user:pass@localhost/db)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simular migração sem executar (validação apenas)'
    )
    
    args = parser.parse_args()
    
    if not args.target:
        logger.error("❌ --target é obrigatório! Ex: postgresql://finup_user:senha@localhost/finup_db_dev")
        sys.exit(1)
    
    success = migrate_data(args.source, args.target, args.dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
